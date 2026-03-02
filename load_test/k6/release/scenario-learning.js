// Release 서버 학습 플로우 시나리오 테스트
// 실제 사용자 학습 패턴 시뮬레이션
// 사용법: k6 run -e BASE_URL=https://release.imymemine.kr/server scenario-learning.js

import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Trend, Counter } from 'k6/metrics';
import { BASE_URL, login, authHeaders, defaultHeaders, errorRate, generateUUID } from './config.js';

const LOGIN_EVERY_ITER = String(__ENV.LOGIN_EVERY_ITER || 'false').toLowerCase() === 'true';
let cachedAuth = null;

// 커스텀 메트릭
const loginDuration = new Trend('login_duration');
const cardLoadDuration = new Trend('card_load_duration');
const attemptCreateDuration = new Trend('attempt_create_duration');
const learningFlowCounter = new Counter('learning_flows_completed');

export const options = {
  stages: [
    { duration: '30s', target: 10 },   // 10명까지
    { duration: '2m', target: 30 },    // 30명까지
    { duration: '2m', target: 30 },    // 30명 유지
    { duration: '30s', target: 0 },    // 종료
  ],
  thresholds: {
    http_req_duration: ['p(95)<2000'],
    http_req_failed: ['rate<0.1'],
    login_duration: ['p(95)<3000'],
    card_load_duration: ['p(95)<1000'],
  },
};

export default function () {
  let auth = null;
  // Step 1: 로그인
  group('Step 1: Login', function () {
    if (LOGIN_EVERY_ITER || !cachedAuth) {
      const startTime = Date.now();
      auth = login();
      loginDuration.add(Date.now() - startTime);
      if (auth) {
        cachedAuth = auth;
      }
    } else {
      auth = cachedAuth;
    }

    if (!auth) {
      errorRate.add(1);
    }
  });

  if (!auth) return;

  sleep(1);

  // Step 2: 카테고리 & 키워드 조회 (학습 시작 전)
  group('Step 2: Browse Categories', function () {
    const catRes = http.get(`${BASE_URL}/categories`, defaultHeaders());
    check(catRes, {
      'categories loaded': (r) => r.status === 200,
    }) || errorRate.add(1);

    const kwRes = http.get(`${BASE_URL}/keywords`, defaultHeaders());
    check(kwRes, {
      'keywords loaded': (r) => r.status === 200,
    }) || errorRate.add(1);
  });

  sleep(2);

  // Step 3: 내 카드 목록 조회
  let cards = [];
  group('Step 3: Load My Cards', function () {
    const startTime = Date.now();
    const res = http.get(`${BASE_URL}/cards`, authHeaders(auth.accessToken));
    cardLoadDuration.add(Date.now() - startTime);

    const success = check(res, {
      'cards loaded': (r) => r.status === 200,
      'cards is array': (r) => {
        try {
          const data = JSON.parse(r.body).data;
          return Array.isArray(data);
        } catch {
          return false;
        }
      },
    });

    if (success) {
      try {
        cards = JSON.parse(res.body).data || [];
      } catch {
        cards = [];
      }
    } else {
      errorRate.add(1);
    }
  });

  sleep(1);

  // Step 4: 카드 상세 조회 (카드가 있는 경우)
  if (cards.length > 0) {
    group('Step 4: View Card Detail', function () {
      const randomCard = cards[Math.floor(Math.random() * cards.length)];
      const cardId = randomCard.id || randomCard.cardId;

      if (cardId) {
        const res = http.get(`${BASE_URL}/cards/${cardId}`, authHeaders(auth.accessToken));
        check(res, {
          'card detail loaded': (r) => r.status === 200,
        }) || errorRate.add(1);
      }
    });

    sleep(2);

    // Step 5: 학습 시도 생성 (Presigned URL 발급)
    group('Step 5: Create Learning Attempt', function () {
      const randomCard = cards[Math.floor(Math.random() * cards.length)];
      const cardId = randomCard.id || randomCard.cardId;

      if (cardId) {
        const startTime = Date.now();
        const payload = JSON.stringify({
          fileName: `test-audio-${generateUUID()}.webm`
        });

        const res = http.post(
          `${BASE_URL}/cards/${cardId}/attempts`,
          payload,
          authHeaders(auth.accessToken)
        );
        attemptCreateDuration.add(Date.now() - startTime);

        const success = check(res, {
          'attempt created': (r) => r.status === 201 || r.status === 200,
        });

        if (success) {
          learningFlowCounter.add(1);
        } else {
          // 카드가 없거나 권한 문제일 수 있음 - 에러로 처리하지 않음
          console.log(`Attempt creation: status=${res.status}`);
        }
      }
    });
  }

  sleep(3);
}

export function handleSummary(data) {
  const completedFlows = data.metrics.learning_flows_completed?.values?.count || 0;
  const totalRequests = data.metrics.http_reqs.values.count;
  const failRate = data.metrics.http_req_failed.values.rate;

  return {
    'scenario-learning-result.json': JSON.stringify(data, null, 2),
    stdout: `
=====================================
  LEARNING FLOW SCENARIO RESULTS
=====================================
  Total Requests: ${totalRequests}
  Learning Flows Completed: ${completedFlows}
  Failed Rate: ${(failRate * 100).toFixed(2)}%

  Response Times:
    Overall P95: ${data.metrics.http_req_duration.values['p(95)'].toFixed(2)}ms
    Login P95: ${data.metrics.login_duration?.values['p(95)']?.toFixed(2) || 'N/A'}ms
    Card Load P95: ${data.metrics.card_load_duration?.values['p(95)']?.toFixed(2) || 'N/A'}ms

  Status: ${failRate < 0.1 ? '✅ PASSED' : '⚠️ Some issues detected'}
=====================================
`,
  };
}
