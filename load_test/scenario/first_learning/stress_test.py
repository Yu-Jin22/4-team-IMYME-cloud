"""
=============================================================================
MINE 부하 테스트 - 첫 학습 시나리오 (Stress Test)
=============================================================================
목적:
  - 밥을 먹고 공부하는 사용자, 밥을 먹고 조금 쉬었다가 공부하는 사용자,
    그리고 밥을 먹고 개인적인 시간을 보내다가 일을 하는 사용자처럼
    공부를 하면서 MINE 서비스를 사용하는 사용자는 누적될 것으로 예상
  - 누적 부하를 견디는지 확인
  - p95 응답 시간이 400ms를 넘어가는 지점 파악

테스트 설정:
  - 동시 사용자: 0 → 50명 (점진적 증가, 필요시 더 늘림)
  - 증가율: 초당 1명 (천천히 증가)
  - 실행 시간: 수동 중단 (p95 > 400ms 도달 시)
  - 특징: 사용자가 누적되면서 부하가 지속적으로 증가

실행 방법:
  # Web UI 모드 (권장)
  locust -f load_test/scenario/first_learning/stress_test.py \\
    --host=http://3.39.31.181:8080

  # Headless 모드
  locust -f load_test/scenario/first_learning/stress_test.py \\
    --host=http://3.39.31.181:8080 \\
    --users 50 --spawn-rate 1 --headless

측정 목표:
  - p95 응답 시간이 400ms를 넘어가는 시점의 동시 사용자 수 파악
  - 사용자 증가에 따른 응답 시간 추이 관찰
  - Web UI의 Charts 탭에서 실시간 p95 모니터링
=============================================================================
"""

import random
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

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
    """
    첫 학습 시나리오: 신규 사용자가 처음으로 학습하는 전체 흐름
    - 카테고리 → 키워드 → 카드 생성 → 녹음 → 피드백 조회
    """

    def on_start(self):
        """시나리오 시작 시 CSV에서 로드된 JWT 토큰 할당"""
        if JWT_TOKENS:
            user_id = random.choice(TEST_USER_IDS)
            self.auth_token = JWT_TOKENS.get(user_id, AUTH_TOKEN)
            self.user_id = user_id
        else:
            self.auth_token = AUTH_TOKEN
            self.user_id = 1

        # 전체 시나리오 시작 시간 기록
        self.scenario_start_time = None

    def get_headers(self):
        """인증 헤더 반환"""
        return {
            "Authorization": getattr(self, "auth_token", AUTH_TOKEN),
            "Content-Type": "application/json",
        }

    @task
    def step1_main_page(self):
        """Step 1: 메인페이지"""
        # 시나리오 시작 시간 기록
        self.scenario_start_time = time.time()

        self.client.get(
            "/users/me",
            headers=self.get_headers(),
            name="[Stress] 1. 메인페이지(프로필)",
        )

    @task
    def step2_select_category(self):
        """Step 2: 카테고리 선택 (목록 조회)"""
        self.client.get(
            "/categories?isActive=true",
            headers=self.get_headers(),
            name="[Stress] 2. 카테고리 선택",
        )

    @task
    def step3_select_keyword(self):
        """Step 3: 키워드 선택 (카테고리별 키워드 조회)"""
        category_id = random.choice(TEST_CATEGORY_IDS)
        self.client.get(
            f"/categories/{category_id}/keywords",
            headers=self.get_headers(),
            name="[Stress] 3. 키워드 선택",
        )

    @task
    def step4_create_card(self):
        """Step 4: 카드 생성"""
        payload = {
            "categoryId": random.choice(TEST_CATEGORY_IDS),
            "keywordId": random.choice(TEST_KEYWORD_IDS),
            "title": f"테스트 카드 {random.randint(1, 9999)}",
        }
        with self.client.post(
            "/cards",
            json=payload,
            headers=self.get_headers(),
            name="[Stress] 4. 카드 생성",
            catch_response=True,
        ) as response:
            if response.status_code == 201:
                data = response.json()
                self.created_card_id = data.get("data", {}).get("id") or data.get("id", random.choice(TEST_CARD_IDS))
                response.success()

    @task
    def step5_create_attempt(self):
        """Step 5: Attempt 생성 (녹음 시도 생성)"""
        card_id = getattr(self, "created_card_id", random.choice(TEST_CARD_IDS))
        payload = {
            "durationSeconds": random.randint(30, 120),
        }
        with self.client.post(
            f"/cards/{card_id}/attempts",
            json=payload,
            headers=self.get_headers(),
            name="[Stress] 5. Attempt 생성",
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
        """Step 6: 피드백 결과 조회"""
        card_id = getattr(self, "created_card_id", random.choice(TEST_CARD_IDS))
        attempt_id = getattr(self, "attempt_id", 1)

        self.client.get(
            f"/cards/{card_id}/attempts/{attempt_id}",
            headers=self.get_headers(),
            name="[Stress] 6. 피드백 결과 조회",
        )

        # 전체 시나리오 완료 시간 계산 및 기록
        if self.scenario_start_time:
            total_time = int((time.time() - self.scenario_start_time) * 1000)
            self.client.request(
                "SCENARIO",
                "/full_scenario",
                name="[Stress] 전체 시나리오",
                response_time=total_time,
                response_length=0,
                exception=None,
                context={}
            )

        self.interrupt()


class StressTestUser(HttpUser):
    """Stress Test 사용자 - 누적 부하 시뮬레이션"""
    wait_time = between(2, 5)  # 각 태스크 사이 2~5초 대기
    tasks = [FirstLearningScenario]
