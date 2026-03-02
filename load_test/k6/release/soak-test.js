// Release 서버 내구성 테스트 (Soak Test)
// 장시간 부하를 유지하여 메모리 누수, 연결 고갈 등 확인
// 사용법: k6 run -e BASE_URL=https://release.imymemine.kr/server soak-test.js

import http from 'k6/http';
import { check, sleep } from 'k6';
import { BASE_URL, defaultHeaders, errorRate } from './config.js';

export const options = {
  stages: [
    { duration: '10s', target: 50 },   // 30분: 30명 유지 (핵심 구간)
    { duration: '10m', target: 50 },     // 2분: 종료
  ],
thresholds: {
    http_req_duration: ['p(95)<2000'],
    http_req_failed: ['rate<0.05'],
  },
};

export default function () {
  sleep(1);

  let res = http.get(`${BASE_URL}/categories`, defaultHeaders());
  check(res, { 'categories ok': (r) => r.status === 200 }) || errorRate.add(1);

  sleep(3);
}

export function handleSummary(data) {
  const duration = data.state.testRunDurationMs / 1000 / 60; // minutes
  const failRate = data.metrics.http_req_failed.values.rate;

  return {
    'soak-test-result.json': JSON.stringify(data, null, 2),
    stdout: `
=====================================
  SOAK TEST RESULTS
=====================================
  Test Duration: ${duration.toFixed(1)} minutes
  Total Requests: ${data.metrics.http_reqs.values.count}
  Failed Rate: ${(failRate * 100).toFixed(2)}%

  Response Times:
    Avg: ${data.metrics.http_req_duration.values.avg.toFixed(2)}ms
    P95: ${data.metrics.http_req_duration.values['p(95)'].toFixed(2)}ms
    P99: ${data.metrics.http_req_duration.values['p(99)'].toFixed(2)}ms
    Max: ${data.metrics.http_req_duration.values.max.toFixed(2)}ms

  Sustained VUs: 30

  Stability: ${failRate < 0.05 ? '✅ System is stable under sustained load' : '⚠️ Potential stability issues'}
=====================================
`,
  };
}
