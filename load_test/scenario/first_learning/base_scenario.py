"""
=============================================================================
MINE 부하 테스트 - 첫 학습 시나리오
=============================================================================
흐름: 로그인 → 메인페이지 → 카테고리 선택 → 키워드 선택
      → 녹음 및 피드백 요청 → 피드백 카드 조회

이유: MVP 특성상 첫 사용자가 많고 고정 사용자가 적어,
      첫 학습이 많이 이루어질 것으로 판단

OAuth 로그인 대체 방법:
  - /test/token/{userId} 엔드포인트로 테스트용 JWT 토큰 발급
  - 서버 설정에서 해당 엔드포인트는 인증 없이 접근 가능해야 함

실행 방법:
  locust -f load_test/scenario/first_learning.py --host=http://3.39.31.181:8080 \
    --users 50 --spawn-rate 5 --run-time 5m
=============================================================================
"""

import random
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

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
        # CSV 파일에서 로드된 토큰 중 랜덤 선택
        if JWT_TOKENS:
            user_id = random.choice(TEST_USER_IDS)
            self.auth_token = JWT_TOKENS.get(user_id, AUTH_TOKEN)
            self.user_id = user_id
        else:
            # CSV 로드 실패 시 폴백
            self.auth_token = AUTH_TOKEN
            self.user_id = 1

    def get_headers(self):
        """인증 헤더 반환"""
        return {
            "Authorization": getattr(self, "auth_token", AUTH_TOKEN),
            "Content-Type": "application/json",
        }

    @task
    def step1_main_page(self):
        """Step 1: 메인페이지"""
        self.client.get(
            "/users/me",
            headers=self.get_headers(),
            name="[첫학습] 1. 메인페이지(프로필)",
        )

    @task
    def step2_select_category(self):
        """Step 2: 카테고리 선택 (목록 조회)"""
        self.client.get(
            "/categories?isActive=true",
            headers=self.get_headers(),
            name="[첫학습] 2. 카테고리 선택",
        )

    @task
    def step3_select_keyword(self):
        """Step 3: 키워드 선택 (카테고리별 키워드 조회)"""
        category_id = random.choice(TEST_CATEGORY_IDS)
        self.client.get(
            f"/categories/{category_id}/keywords",
            headers=self.get_headers(),
            name="[첫학습] 3. 키워드 선택",
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
            name="[첫학습] 4. 카드 생성",
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
            name="[첫학습] 5. Attempt 생성",
            catch_response=True,
        ) as response:
            if response.status_code == 201:
                data = response.json()
                # API 응답 구조에 맞게 attemptId 추출
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
            name="[첫학습] 6. 피드백 결과 조회",
        )
        self.interrupt()


class FirstLearningUser(HttpUser):
    """첫 학습 시나리오 사용자"""
    wait_time = between(2, 5)
    tasks = [FirstLearningScenario]
