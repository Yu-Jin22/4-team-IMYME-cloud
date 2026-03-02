// Release 서버 스트레스 테스트
// 시스템 한계치 확인 (점진적 부하 증가)
// 사용법: k6 run -e BASE_URL=https://release.imymemine.kr/server stress-test.js

import http from 'k6/http';
import { check, sleep } from 'k6';
import { BASE_URL, login, authHeaders, defaultHeaders, errorRate } from './config.js';

const LOGIN_EVERY_ITER = String(__ENV.LOGIN_EVERY_ITER || 'false').toLowerCase() === 'true';
let cachedAuth = null;

export const options = {
  stages: [
    { duration: '1m', target: 50 },    // 1분: 50명
    { duration: '2m', target: 100 },   // 2분: 100명
    { duration: '2m', target: 150 },   // 2분: 150명
    { duration: '2m', target: 200 },   // 2분: 200명 (스트레스 구간)
    { duration: '3m', target: 200 },   // 3분: 200명 유지
    { duration: '2m', target: 0 },     // 2분: 종료
  ],
  thresholds: {
    http_req_duration: ['p(95)<3000'],  // 95%가 3초 이하
    http_req_failed: ['rate<0.15'],     // 실패율 15% 미만 (스트레스 상황)
  },
};

export default function () {
  // 1. 로그인
  const auth = (LOGIN_EVERY_ITER || !cachedAuth) ? login() : cachedAuth;
  if (!auth) {
    errorRate.add(1);
    sleep(1);
    return;
  }
  cachedAuth = auth;

  // 2. 혼합 워크로드
  const scenarios = [
    () => http.get(`${BASE_URL}/categories`, defaultHeaders()),
    () => http.get(`${BASE_URL}/keywords`, defaultHeaders()),
    () => http.get(`${BASE_URL}/users/me`, authHeaders(auth.accessToken)),
    () => http.get(`${BASE_URL}/cards`, authHeaders(auth.accessToken)),
    () => http.get(`${BASE_URL}/health`, defaultHeaders()),
  ];

  // 랜덤하게 2-3개 API 호출
  const numCalls = Math.floor(Math.random() * 2) + 2;
  for (let i = 0; i < numCalls; i++) {
    const scenario = scenarios[Math.floor(Math.random() * scenarios.length)];
    const res = scenario();
    check(res, {
      'status is 2xx': (r) => r.status >= 200 && r.status < 300,
    }) || errorRate.add(1);
    sleep(0.5);
  }

  sleep(1);
}

export function handleSummary(data) {
  const p95 = data.metrics.http_req_duration.values['p(95)'];
  const p99 = data.metrics.http_req_duration.values['p(99)'];
  const maxDuration = data.metrics.http_req_duration.values.max;
  const failRate = data.metrics.http_req_failed.values.rate;

  return {
    'stress-test-result.json': JSON.stringify(data, null, 2),
    stdout: `
=====================================
  STRESS TEST RESULTS
=====================================
  Total Requests: ${data.metrics.http_reqs.values.count}
  Failed Rate: ${(failRate * 100).toFixed(2)}%

  Response Times:
    Avg: ${data.metrics.http_req_duration.values.avg.toFixed(2)}ms
    P95: ${p95.toFixed(2)}ms
    P99: ${p99.toFixed(2)}ms
    Max: ${maxDuration.toFixed(2)}ms

  Peak VUs: 200

  Status: ${failRate < 0.15 ? '✅ System handled stress' : '⚠️ System under heavy stress'}
=====================================
`,
  };
}
