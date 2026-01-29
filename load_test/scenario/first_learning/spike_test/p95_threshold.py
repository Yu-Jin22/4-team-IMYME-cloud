"""
=============================================================================
MINE 스파이크 테스트 - p95 임계점 찾기
=============================================================================
목적:
  - 급격한 트래픽 증가 시 p95 응답 시간이 400ms를 넘어가는 지점 파악
  - 시험기간/면접기간처럼 갑자기 몰리는 상황에서 성능 저하 시작 지점 확인

테스트 설정:
  - 동시 사용자: 0 → 100명 (빠르게 증가)
  - 증가율: 초당 5명 (급격한 증가)
  - 실행 시간: 수동 중단 (p95 > 400ms 도달 시)
  - 특징: 짧은 시간에 급격한 부하 증가, 성능 한계 지점 관찰

실행 방법:
  # Web UI 모드 (권장)
  locust -f load_test/scenario/first_learning/spike_test/p95_threshold.py \
    --host=http://3.39.31.181:8080

  # Headless 모드
  locust -f load_test/scenario/first_learning/spike_test/p95_threshold.py \
    --host=http://3.39.31.181:8080 \
    --users 100 --spawn-rate 5 --headless

측정 방법:
  1. Web UI에서 Charts 탭 열기
  2. Response Times (ms) 그래프에서 95th percentile 라인 주시
  3. p95가 400ms를 넘어가는 순간 자동으로 중단됨
  4. 콘솔 출력에서 해당 시점의 동시 사용자 수 확인

측정 목표:
  - 급격한 트래픽 증가 시 p95 = 400ms 시점의 동시 사용자 수
  - 해당 시점의 평균 응답 시간
  - 해당 시점의 RPS (Requests Per Second)
=============================================================================
"""

import random
import sys
import os
from locust import constant


sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from locust import HttpUser, task, between, SequentialTaskSet, events
from locust.runners import STATE_STOPPING, STATE_STOPPED
from config.settings import (
    AUTH_TOKEN,
    JWT_TOKENS,
    TEST_USER_IDS,
    TEST_CARD_IDS,
    TEST_CATEGORY_IDS,
    TEST_KEYWORD_IDS,
)

# p95 임계값 (ms)
P95_THRESHOLD = 400


@events.request.add_listener
def check_p95_threshold(request_type, name, response_time, response_length, exception, context, **kwargs):
    """p95가 임계값을 넘으면 자동으로 테스트 중단"""
    if context and hasattr(context, 'environment'):
        runner = context.environment.runner

        if runner.state in [STATE_STOPPING, STATE_STOPPED]:
            return

        stats = runner.stats.total

        if stats.num_requests > 10:  # 최소 10개 요청 후부터 체크
            p95 = stats.get_response_time_percentile(0.95)

            if p95 and p95 > P95_THRESHOLD:
                user_count = runner.user_count
                avg_response_time = stats.avg_response_time
                rps = stats.total_rps

                print(f"\n{'='*80}")
                print(f"🚨 p95 임계값 초과 감지! (Spike Test)")
                print(f"{'='*80}")
                print(f"p95 응답 시간: {p95:.2f}ms (임계값: {P95_THRESHOLD}ms)")
                print(f"동시 사용자 수: {user_count}명")
                print(f"평균 응답 시간: {avg_response_time:.2f}ms")
                print(f"RPS: {rps:.2f} req/s")
                print(f"총 요청 수: {stats.num_requests}")
                print(f"성공률: {(1 - stats.fail_ratio) * 100:.2f}%")
                print(f"{'='*80}\n")

                runner.quit()



class FirstLearningScenario(SequentialTaskSet):
    """첫 학습 시나리오"""

    def on_start(self):
        if JWT_TOKENS:
            user_id = random.choice(TEST_USER_IDS)
            self.auth_token = JWT_TOKENS.get(user_id, AUTH_TOKEN)
            self.user_id = user_id
        else:
            self.auth_token = AUTH_TOKEN
            self.user_id = 1

    def get_headers(self):
        return {
            "Authorization": getattr(self, "auth_token", AUTH_TOKEN),
            "Content-Type": "application/json",
        }

    @task
    def step1_main_page(self):
        self.client.get(
            "/users/me",
            headers=self.get_headers(),
            name="[Spike-P95] 1. 메인페이지",
        )

    @task
    def step2_select_category(self):
        self.client.get(
            "/categories?isActive=true",
            headers=self.get_headers(),
            name="[Spike-P95] 2. 카테고리 선택",
        )

    @task
    def step3_select_keyword(self):
        category_id = random.choice(TEST_CATEGORY_IDS)
        self.client.get(
            f"/categories/{category_id}/keywords",
            headers=self.get_headers(),
            name="[Spike-P95] 3. 키워드 선택",
        )

    @task
    def step4_create_card(self):
        payload = {
            "categoryId": random.choice(TEST_CATEGORY_IDS),
            "keywordId": random.choice(TEST_KEYWORD_IDS),
            "title": f"테스트 카드 {random.randint(1, 9999)}",
        }
        with self.client.post(
            "/cards",
            json=payload,
            headers=self.get_headers(),
            name="[Spike-P95] 4. 카드 생성",
            catch_response=True,
        ) as response:
            if response.status_code == 201:
                data = response.json()
                self.created_card_id = data.get("data", {}).get("id") or data.get("id", random.choice(TEST_CARD_IDS))
                response.success()

    @task
    def step5_create_attempt(self):
        card_id = getattr(self, "created_card_id", random.choice(TEST_CARD_IDS))
        payload = {
            "durationSeconds": random.randint(30, 120),
        }
        with self.client.post(
            f"/cards/{card_id}/attempts",
            json=payload,
            headers=self.get_headers(),
            name="[Spike-P95] 5. Attempt 생성",
            catch_response=True,
        ) as response:
            if response.status_code == 201:
                data = response.json()
                self.attempt_id = data.get("data", {}).get("attemptId") or data.get("attemptId", 1)
                response.success()
            else:
                response.failure(f"Failed with status {response.status_code}: {response.text}")

    @task
    def step6_check_feedback(self):
        card_id = getattr(self, "created_card_id", random.choice(TEST_CARD_IDS))
        attempt_id = getattr(self, "attempt_id", 1)

        self.client.get(
            f"/cards/{card_id}/attempts/{attempt_id}",
            headers=self.get_headers(),
            name="[Spike-P95] 6. 피드백 조회",
        )
        self.interrupt()


class P95ThresholdUser(HttpUser):
    """Spike p95 임계점 찾기 사용자"""
    wait_time = constant(1)  # Spike 상황에서는 대기 시간을 짧게
    tasks = [FirstLearningScenario]
