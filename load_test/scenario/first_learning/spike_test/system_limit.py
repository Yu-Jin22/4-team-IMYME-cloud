"""
=============================================================================
MINE 스파이크 테스트 - 시스템 한계 테스트
=============================================================================
목적:
  - 급격한 트래픽 증가 시 시스템이 견디는 한계 확인
  - 시험기간/면접기간의 폭발적인 트래픽에서 시스템 장애 발생 지점 파악
  - 갑작스러운 바이럴/홍보 효과 시 시스템 복구 능력 측정

테스트 설정:
  - 동시 사용자: 0 → 300명 (매우 공격적으로 증가)
  - 증가율: 초당 10명 (폭발적인 증가)
  - 실행 시간: 수동 중단 (시스템 장애 발생 시 또는 최대 사용자 도달 시)
  - 특징: 극단적인 트래픽 급증 상황에서 시스템 한계 테스트

실행 방법:
  # Web UI 모드 (권장)
  locust -f load_test/scenario/first_learning/spike_test/system_limit.py \
    --host=http://3.39.31.181:8080

  # Headless 모드
  locust -f load_test/scenario/first_learning/spike_test/system_limit.py \
    --host=http://3.39.31.181:8080 \
    --users 300 --spawn-rate 10 --headless

측정 방법:
  1. Web UI에서 Charts 탭과 Failures 탭 동시 모니터링
  2. 서버 모니터링 도구에서 CPU, 메모리, JVM Heap 사용량 확인
  3. 5xx 에러율이 급증하거나 서버 응답이 멈추는 시점 기록
  4. 해당 시점의 동시 사용자 수와 시스템 리소스 상태 기록

주의사항:
  - 실제 운영 환경에서는 절대 실행하지 말 것
  - 개발/테스트 환경에서만 실행
  - 서버가 완전히 다운될 수 있음
  - 테스트 전 서버 백업 및 복구 계획 수립

측정 목표:
  - 급격한 트래픽 증가 시 시스템 장애 발생 시점의 동시 사용자 수
  - 5xx 에러율이 50%를 넘는 시점
  - CPU 사용률 100% 도달 시점
  - JVM OutOfMemoryError 발생 여부
  - 서버 복구 시간 (Stop 버튼 클릭 후 정상화까지 소요 시간)
=============================================================================
"""

import random
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from locust import HttpUser, task, between, SequentialTaskSet
from config.settings import (
    AUTH_TOKEN,
    JWT_TOKENS,
    TEST_USER_IDS,
    TEST_CARD_IDS,
    TEST_CATEGORY_IDS,
    TEST_KEYWORD_IDS,
)


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
            name="[Spike-Limit] 1. 메인페이지",
        )

    @task
    def step2_select_category(self):
        self.client.get(
            "/categories?isActive=true",
            headers=self.get_headers(),
            name="[Spike-Limit] 2. 카테고리 선택",
        )

    @task
    def step3_select_keyword(self):
        category_id = random.choice(TEST_CATEGORY_IDS)
        self.client.get(
            f"/categories/{category_id}/keywords",
            headers=self.get_headers(),
            name="[Spike-Limit] 3. 키워드 선택",
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
            name="[Spike-Limit] 4. 카드 생성",
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
            name="[Spike-Limit] 5. Attempt 생성",
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
            name="[Spike-Limit] 6. 피드백 조회",
        )
        self.interrupt()


class SystemLimitUser(HttpUser):
    """Spike 시스템 한계 테스트 사용자"""
    wait_time = between(0.5, 2)  # 매우 짧은 대기 시간으로 극한의 부하
    tasks = [FirstLearningScenario]
