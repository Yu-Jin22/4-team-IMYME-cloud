import random
import sys
import os
from locust import HttpUser, SequentialTaskSet, constant, events
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

# p95 체크 이벤트
@events.request.add_listener
def check_p95_threshold(request_type, name, response_time, response_length, exception, context, **kwargs):
    """p95가 임계값을 넘으면 자동으로 테스트 중단"""
    if context and hasattr(context, 'environment'):
        runner = context.environment.runner

        if runner.state in [STATE_STOPPING, STATE_STOPPED]:
            return

        stats = runner.stats.total
        if stats.num_requests > 10:
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
    """첫 학습 시나리오 - 순서 보장"""

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

    def run_scenario(self):
        """순서대로 시나리오 실행"""

        # 1. 메인페이지 조회
        self.client.get("/users/me", headers=self.get_headers(), name="[Spike-P95] 1. 메인페이지")

        # 2. 카테고리 선택
        self.client.get("/categories?isActive=true", headers=self.get_headers(), name="[Spike-P95] 2. 카테고리 선택")

        # 3. 키워드 선택
        category_id = random.choice(TEST_CATEGORY_IDS)
        self.client.get(f"/categories/{category_id}/keywords", headers=self.get_headers(), name="[Spike-P95] 3. 키워드 선택")

        # 4. 카드 생성
        payload = {
            "categoryId": random.choice(TEST_CATEGORY_IDS),
            "keywordId": random.choice(TEST_KEYWORD_IDS),
            "title": f"테스트 카드 {random.randint(1, 9999)}",
        }
        with self.client.post("/cards", json=payload, headers=self.get_headers(), name="[Spike-P95] 4. 카드 생성", catch_response=True) as response:
            if response.status_code == 201:
                data = response.json()
                self.created_card_id = data.get("data", {}).get("id") or data.get("id", random.choice(TEST_CARD_IDS))
                response.success()
            else:
                response.failure(f"Failed with status {response.status_code}")

        # 5. Attempt 생성
        card_id = getattr(self, "created_card_id", random.choice(TEST_CARD_IDS))
        payload = {"durationSeconds": random.randint(30, 120)}
        with self.client.post(f"/cards/{card_id}/attempts", json=payload, headers=self.get_headers(), name="[Spike-P95] 5. Attempt 생성", catch_response=True) as response:
            if response.status_code == 201:
                data = response.json()
                self.attempt_id = data.get("data", {}).get("attemptId") or data.get("attemptId", 1)
                response.success()
            else:
                response.failure(f"Failed with status {response.status_code}")

        # 6. 피드백 조회
        card_id = getattr(self, "created_card_id", random.choice(TEST_CARD_IDS))
        attempt_id = getattr(self, "attempt_id", 1)
        self.client.get(f"/cards/{card_id}/attempts/{attempt_id}", headers=self.get_headers(), name="[Spike-P95] 6. 피드백 조회")

    @task
    def scenario_task(self):
        """유저 루프에서 시나리오 반복"""
        self.run_scenario()


class P95ThresholdUser(HttpUser):
    """Spike p95 임계점 찾기 사용자"""
    tasks = [FirstLearningScenario]
    wait_time = constant(1)  # Spike 상황에서는 대기 시간을 짧게
