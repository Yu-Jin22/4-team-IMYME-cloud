// Release 서버 k6 부하 테스트 공통 설정
// 사용법: k6 run -e BASE_URL=https://your-release-server.com smoke-test.js

import http from 'k6/http';
import { check } from 'k6';
import { Rate } from 'k6/metrics';

// 환경변수에서 BASE_URL 가져오기 (기본값: release 서버)
export const BASE_URL = __ENV.BASE_URL || 'https://release.imymemine.kr/server';

// 커스텀 메트릭
export const errorRate = new Rate('errors');
export const loginFailRate = new Rate('login_failures');
const USER_ID_BASE = Number(__ENV.USER_ID_BASE || 1000000);

// UUID 생성 함수
export function generateUUID() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

// VU/ITER 기반으로 충돌 가능성이 낮은 userId 생성
export function generateUserId() {
  return USER_ID_BASE + ((__VU - 1) * 1000000) + __ITER;
}

// E2E 로그인으로 JWT 토큰 획득
export function login(userId = null, customDeviceUuid = null) {
  const deviceUuid = customDeviceUuid || generateUUID();
  // userId가 없으면 매 반복마다 신규 userId 생성
  const userIdToUse = userId || generateUserId();

  const payload = JSON.stringify({
    userId: userIdToUse,
    deviceUuid: deviceUuid,
  });

  const params = {
    headers: {
      'Content-Type': 'application/json',
    },
    timeout: '30s',
  };

  const res = http.post(`${BASE_URL}/e2e/login`, payload, params);

  const success = check(res, {
    'login status is 200': (r) => r.status === 200,
    'login has accessToken': (r) => {
      try {
        return JSON.parse(r.body).data.accessToken !== undefined;
      } catch {
        return false;
      }
    },
  });

  if (!success) {
    console.error(`Login failed: status=${res.status}, body=${res.body}`);
    loginFailRate.add(1);
    return null;
  }

  loginFailRate.add(0);
  const body = JSON.parse(res.body);
  return {
    accessToken: body.data.accessToken,
    refreshToken: body.data.refreshToken,
    userId: body.data.user?.id,
    deviceUuid: deviceUuid,
  };
}

// 인증 헤더 생성
export function authHeaders(accessToken) {
  return {
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json',
    },
    timeout: '30s',
  };
}

// 공통 헤더 (인증 불필요한 요청)
export function defaultHeaders() {
  return {
    headers: {
      'Content-Type': 'application/json',
    },
    timeout: '30s',
  };
}
