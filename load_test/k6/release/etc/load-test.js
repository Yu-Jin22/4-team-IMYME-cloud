// Release 서버 부하 테스트
// 일반적인 트래픽 상황 시뮬레이션
// 사용법: k6 run -e BASE_URL=https://release.imymemine.kr/server load-test.js

import http from 'k6/http';
import { check, sleep } from 'k6';
import { BASE_URL, login, authHeaders, defaultHeaders, errorRate } from './config.js';

const LOGIN_EVERY_ITER = String(__ENV.LOGIN_EVERY_ITER || 'false').toLowerCase() === 'true';
let cachedAuth = null;

export const options = {
  stages: [
    { duration: '30s', target: 10 },   // Ramp-up: 30초 동안 10명까지
    { duration: '1m', target: 30 },    // 1분 동안 30명까지
    { duration: '2m', target: 50 },    // 2분 동안 50명 유지
    { duration: '1m', target: 30 },    // 1분 동안 30명으로 감소
    { duration: '30s', target: 0 },    // Ramp-down: 30초 동안 종료
  ],
  thresholds: {
    http_req_duration: ['p(95)<1500'],  // 95%가 1.5초 이하
    http_req_failed: ['rate<0.05'],     // 실패율 5% 미만
    errors: ['rate<0.05'],
    login_failures: ['rate<0.1'],       // 로그인 실패율 10% 미만
  },
};

export default function () {
  // 1. 로그인하여 토큰 획득
  const auth = (LOGIN_EVERY_ITER || !cachedAuth) ? login() : cachedAuth;
  if (!auth) {
    errorRate.add(1);
    sleep(2);
    return;
  }
  cachedAuth = auth;

  // 2. 카테고리 조회 (Public)
  let res = http.get(`${BASE_URL}/categories`, defaultHeaders());
  check(res, {
    'categories status 200': (r) => r.status === 200,
  }) || errorRate.add(1);

  sleep(1);

  // 3. 키워드 조회 (Public)
  res = http.get(`${BASE_URL}/keywords`, defaultHeaders());
  check(res, {
    'keywords status 200': (r) => r.status === 200,
  }) || errorRate.add(1);

  sleep(1);

  // 4. 사용자 프로필 조회
  res = http.get(`${BASE_URL}/users/me`, authHeaders(auth.accessToken));
  check(res, {
    'profile status 200': (r) => r.status === 200,
  }) || errorRate.add(1);

  sleep(1);

  // 5. 카드 목록 조회
  res = http.get(`${BASE_URL}/cards`, authHeaders(auth.accessToken));
  check(res, {
    'cards status 200': (r) => r.status === 200,
  }) || errorRate.add(1);

  sleep(2);
}

export function handleSummary(data) {
  const p95 = data.metrics.http_req_duration.values['p(95)'];
  const failRate = data.metrics.http_req_failed.values.rate;
  const passed = p95 < 1500 && failRate < 0.05;

  return {
    'load-test-result.json': JSON.stringify(data, null, 2),
    stdout: `
=====================================
  LOAD TEST ${passed ? '✅ PASSED' : '❌ FAILED'}
=====================================
  Total Requests: ${data.metrics.http_reqs.values.count}
  Failed Rate: ${(failRate * 100).toFixed(2)}%
  Avg Duration: ${data.metrics.http_req_duration.values.avg.toFixed(2)}ms
  P95 Duration: ${p95.toFixed(2)}ms
  P99 Duration: ${data.metrics.http_req_duration.values['p(99)'].toFixed(2)}ms
  Max VUs: 50
=====================================
`,
  };
}
