"""
=============================================================================
MINE 부하 테스트 - 복습 시나리오
=============================================================================
흐름: 로그인 → 메인페이지 → 마이페이지(학습 목록 조회)
      → 피드백 카드 조회

이유: 학습 후, 본인이 피드백 받은 내용을 다시 보는 사용자가
      존재할 것이라고 예상

OAuth 로그인 대체 방법:
  - /test/token/{userId} 엔드포인트로 테스트용 JWT 토큰 발급
  - 서버 설정에서 해당 엔드포인트는 인증 없이 접근 가능해야 함

실행 방법:
  locust -f load_test/scenario/review.py --host=http://3.39.31.181:8080 \
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
)


class ReviewScenario(SequentialTaskSet):
    """
    복습 시나리오: 이미 학습한 카드의 피드백을 다시 확인하는 흐름
    - 학습 목록 조회 후 피드백 카드만 확인 (새로운 녹음 없음)
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

    def get_headers(self):
        """인증 헤더 반환"""
        return {
            "Authorization": getattr(self, "auth_token", AUTH_TOKEN),
            "Content-Type": "application/json",
        }

    @task
    def step1_main_page(self):
        """Step 1: 메인페이지 (프로필 조회)"""
        self.client.get(
            "/users/me",
            headers=self.get_headers(),
            name="[복습] 1. 메인페이지(프로필)",
        )

    @task
    def step2_card_list(self):
        """Step 2: 마이페이지에서 학습 목록 조회"""
        with self.client.get(
            "/cards",
            headers=self.get_headers(),
            name="[복습] 2. 학습 목록 조회",
        ) as response:
            if response.status_code == 200:
                data = response.json()
                cards = data.get("cards", [])
                if cards:
                    card = cards[0]
                    self.selected_card_id = card.get("id", TEST_CARD_IDS[0])
                    # 카드의 첫 번째 시도 ID 가져오기
                    attempts = card.get("attempts", [])
                    if attempts:
                        self.attempt_id = attempts[0].get("id", 1)
                    else:
                        self.attempt_id = 1
                else:
                    self.selected_card_id = random.choice(TEST_CARD_IDS)
                    self.attempt_id = 1

    @task
    def step3_feedback_card(self):
        """Step 3: 피드백 카드 조회 (시도 상세)"""
        card_id = getattr(self, "selected_card_id", random.choice(TEST_CARD_IDS))
        attempt_id = getattr(self, "attempt_id", 1)

        self.client.get(
            f"/cards/{card_id}/attempts/{attempt_id}",
            headers=self.get_headers(),
            name="[복습] 3. 피드백 카드 조회",
        )
        self.interrupt()


class ReviewUser(HttpUser):
    """복습 시나리오 사용자"""
    wait_time = between(2, 5)
    tasks = [ReviewScenario]
