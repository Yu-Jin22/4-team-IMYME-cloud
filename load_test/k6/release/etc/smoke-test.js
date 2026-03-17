// Release 서버 스모크 테스트
// 배포 후 기본 동작 확인용 (낮은 부하)
// 사용법: k6 run -e BASE_URL=https://release.imymemine.kr/server smoke-test.js

import http from 'k6/http';
import { check, sleep } from 'k6';
import { BASE_URL, login, authHeaders, defaultHeaders, errorRate } from './config.js';

const LOGIN_EVERY_ITER = String(__ENV.LOGIN_EVERY_ITER || 'false').toLowerCase() === 'true';
let cachedAuth = null;

export const options = {
  vus: 1,              // 가상 사용자 1명
  duration: '30s',     // 30초 동안 실행
  thresholds: {
    http_req_duration: ['p(95)<2000'],  // 95%가 2초 이하
    http_req_failed: ['rate<0.01'],     // 실패율 1% 미만
    errors: ['rate<0.01'],
  },
};

export default function () {
  // 1. Health Check
  let res = http.get(`${BASE_URL}/health`, defaultHeaders());
  check(res, {
    'health check passed': (r) => r.status === 200,
  }) || errorRate.add(1);

  sleep(1);

  // 2. 카테고리 조회 (Public)
  res = http.get(`${BASE_URL}/categories`, defaultHeaders());
  check(res, {
    'categories loaded': (r) => r.status === 200,
  }) || errorRate.add(1);

  sleep(1);

  // 3. 키워드 조회 (Public)
  res = http.get(`${BASE_URL}/keywords`, defaultHeaders());
  check(res, {
    'keywords loaded': (r) => r.status === 200,
  }) || errorRate.add(1);

  sleep(1);

  // 4. E2E 로그인 테스트
  const auth = (LOGIN_EVERY_ITER || !cachedAuth) ? login() : cachedAuth;
  if (!auth) {
    errorRate.add(1);
    return;
  }
  cachedAuth = auth;

  sleep(1);

  // 5. 인증된 API 호출 - 사용자 프로필
  res = http.get(`${BASE_URL}/users/me`, authHeaders(auth.accessToken));
  check(res, {
    'profile loaded': (r) => r.status === 200,
    'has nickname': (r) => {
      try {
        return JSON.parse(r.body).data.nickname !== undefined;
      } catch {
        return false;
      }
    },
  }) || errorRate.add(1);

  sleep(2);
}

export function handleSummary(data) {
  const passed = data.metrics.http_req_failed.values.rate < 0.01;
  return {
    'smoke-test-result.json': JSON.stringify(data, null, 2),
    stdout: `
=====================================
  SMOKE TEST ${passed ? '✅ PASSED' : '❌ FAILED'}
=====================================
  Total Requests: ${data.metrics.http_reqs.values.count}
  Failed Rate: ${(data.metrics.http_req_failed.values.rate * 100).toFixed(2)}%
  Avg Duration: ${data.metrics.http_req_duration.values.avg.toFixed(2)}ms
  P95 Duration: ${data.metrics.http_req_duration.values['p(95)'].toFixed(2)}ms
=====================================
`,
  };
}
