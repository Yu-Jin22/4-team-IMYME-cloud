// Release 서버 내구성 테스트 (Soak Test)
// /categories 엔드포인트만 장시간 호출하여 안정성 확인

import http from 'k6/http';
import { check, sleep } from 'k6';
import { BASE_URL, defaultHeaders, errorRate } from './config.js';

export const options = {
  stages: [
    { duration: '3s', target: 3000 },
  { duration: '10m', target: 3000 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<2000'],
    http_req_failed: ['rate<0.05'],
  },
};

export default function () {
  const res = http.get(`${BASE_URL}/categories`, defaultHeaders());
  check(res, { 'categories ok': (r) => r && r.status === 200 }) || errorRate.add(1);
  sleep(3);
}

// ---- handleSummary 안전화 버전 ----
function num(v) {
  return typeof v === 'number' && Number.isFinite(v) ? v : null;
}
function fixed(v, d = 2, suffix = '') {
  const n = num(v);
  return n === null ? 'n/a' : `${n.toFixed(d)}${suffix}`;
}
function pickPercentile(values, p) {
  // k6 버전/출력에 따라 키가 'p(95)' 또는 'p(95.00)' 등으로 다를 수 있어 후보를 넓게 잡음
  if (!values) return null;
  const candidates = [
    `p(${p})`,
    `p(${p}.00)`,
    `p(${Number(p).toFixed(2)})`,
  ];
  for (const k of candidates) {
    if (k in values) return values[k];
  }
  return null;
}

export function handleSummary(data) {
  const durationMin = (data?.state?.testRunDurationMs ?? 0) / 1000 / 60;

  const httpReqs = data?.metrics?.http_reqs?.values?.count;
  const failRate = data?.metrics?.http_req_failed?.values?.rate; // 0~1

  const durVals = data?.metrics?.http_req_duration?.values;
  const avg = durVals?.avg;
  const p95 = pickPercentile(durVals, 95);
  const p99 = pickPercentile(durVals, 99);
  const max = durVals?.max;

  const vusMax = data?.metrics?.vus_max?.values?.value;
  const vus = data?.metrics?.vus?.values?.value;

  const stable = typeof failRate === 'number' ? failRate < 0.05 : false;

  return {
    'soak-test-result.json': JSON.stringify(data, null, 2),
    stdout: `
=====================================
  SOAK TEST RESULTS
=====================================
  Test Duration: ${fixed(durationMin, 1, ' minutes')}
  Total Requests: ${num(httpReqs) ?? 'n/a'}
  Failed Rate: ${typeof failRate === 'number' ? (failRate * 100).toFixed(2) + '%' : 'n/a'}

  Response Times:
    Avg: ${fixed(avg, 2, 'ms')}
    P95: ${fixed(p95, 2, 'ms')}
    P99: ${fixed(p99, 2, 'ms')}
    Max: ${fixed(max, 2, 'ms')}

  VUs (observed):
    current: ${num(vus) ?? 'n/a'}
    max: ${num(vusMax) ?? 'n/a'}

  Stability: ${stable ? '✅ System is stable under sustained load' : '⚠️ Potential stability issues'}
=====================================
`,
  };
}