// Release 서버 스파이크 테스트
// 갑작스러운 트래픽 급증 시뮬레이션
// 사용법: k6 run -e BASE_URL=https://release.imymemine.kr/server spike-test.js

import http from 'k6/http';
import { check, sleep } from 'k6';
import { BASE_URL, login, authHeaders, defaultHeaders, errorRate } from './config.js';

const LOGIN_EVERY_ITER = String(__ENV.LOGIN_EVERY_ITER || 'false').toLowerCase() === 'true';
let cachedAuth = null;

export const options = {
  stages: [
    { duration: '30s', target: 10 },   // 웜업
    { duration: '10s', target: 100 },  // 스파이크! 급격히 100명
    { duration: '1m', target: 100 },   // 100명 유지
    { duration: '10s', target: 10 },   // 급격히 감소
    { duration: '30s', target: 10 },   // 안정화
    { duration: '10s', target: 150 },  // 두 번째 스파이크! 150명
    { duration: '1m', target: 150 },   // 150명 유지
    { duration: '30s', target: 0 },    // 종료
  ],
  thresholds: {
    http_req_duration: ['p(95)<5000'],  // 스파이크 시 5초까지 허용
    http_req_failed: ['rate<0.2'],      // 스파이크 시 20%까지 허용
  },
};

export default function () {
  // 로그인
  const auth = (LOGIN_EVERY_ITER || !cachedAuth) ? login() : cachedAuth;
  if (!auth) {
    errorRate.add(1);
    return;
  }
  cachedAuth = auth;

  // 주요 API 호출
  const res = http.get(`${BASE_URL}/users/me`, authHeaders(auth.accessToken));
  check(res, {
    'profile loaded': (r) => r.status === 200,
  }) || errorRate.add(1);

  // 카드 조회
  const cardsRes = http.get(`${BASE_URL}/cards`, authHeaders(auth.accessToken));
  check(cardsRes, {
    'cards loaded': (r) => r.status === 200,
  }) || errorRate.add(1);

  sleep(1);
}

export function handleSummary(data) {
  const p95 = data.metrics.http_req_duration.values['p(95)'];
  const failRate = data.metrics.http_req_failed.values.rate;

  return {
    'spike-test-result.json': JSON.stringify(data, null, 2),
    stdout: `
=====================================
  SPIKE TEST RESULTS
=====================================
  Total Requests: ${data.metrics.http_reqs.values.count}
  Failed Rate: ${(failRate * 100).toFixed(2)}%

  Response Times:
    Avg: ${data.metrics.http_req_duration.values.avg.toFixed(2)}ms
    P95: ${p95.toFixed(2)}ms
    Max: ${data.metrics.http_req_duration.values.max.toFixed(2)}ms

  Spike Levels: 100 -> 150 VUs

  Recovery: ${failRate < 0.2 ? '✅ System recovered from spikes' : '⚠️ System struggled with spikes'}
=====================================
`,
  };
}
