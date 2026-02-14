"""
=============================================================================
MINE 부하 테스트 - 이어하기 시나리오
=============================================================================
흐름: 로그인 → 메인페이지 → 마이페이지(학습 목록 조회)
      → 녹음 및 피드백 요청 → 피드백 카드 조회

이유: 이전에 사용했던 사용자가 재 방문시 해당 서비스를
      가장 먼저 사용할 것이라고 판단

OAuth 로그인 대체 방법:
  - /test/token/{userId} 엔드포인트로 테스트용 JWT 토큰 발급
  - 서버 설정에서 해당 엔드포인트는 인증 없이 접근 가능해야 함

실행 방법:
  locust -f load_test/scenario/continue_learning.py --host=http://3.39.31.181:8080 \
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


class ContinueLearningScenario(SequentialTaskSet):
    """
    이어하기 시나리오: 기존 카드로 다시 학습하는 흐름
    - 이미 생성된 카드에서 새로운 시도(Attempt)를 생성
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
        """Step 1: 메인페이지"""
        self.client.get(
            "/users/me",
            headers=self.get_headers(),
            name="[이어하기] 1. 메인페이지(프로필)",
        )

    @task
    def step2_card_list(self):
        """Step 2: 학습 목록 조회"""
        with self.client.get(
            "/cards",
            headers=self.get_headers(),
            name="[이어하기] 2. 학습 목록 조회",
        ) as response:
            if response.status_code == 200:
                data = response.json()
                cards = data.get("cards", [])
                if cards:
                    self.selected_card_id = cards[0].get("id", TEST_CARD_IDS[0])
                else:
                    self.selected_card_id = random.choice(TEST_CARD_IDS)

    @task
    def step3_presigned_url(self):
        """Step 3: 녹음 업로드를 위한 Presigned URL 발급"""
        card_id = getattr(self, "selected_card_id", random.choice(TEST_CARD_IDS))
        payload = {
            "card_id": card_id,
            "file_extension": "mp3",
        }
        with self.client.post(
            "/learning/presigned-url",
            json=payload,
            headers=self.get_headers(),
            name="[이어하기] 3. Presigned URL 발급",
        ) as response:
            if response.status_code == 201:
                data = response.json()
                self.attempt_id = data.get("attempt_id", 1)

    @task
    def step4_upload_complete(self):
        """Step 4: 업로드 완료"""
        card_id = getattr(self, "selected_card_id", random.choice(TEST_CARD_IDS))
        attempt_id = getattr(self, "attempt_id", 1)
        payload = {
            "audio_url": f"https://s3.example.com/test/audio_{random.randint(1, 9999)}.mp3",
            "duration_seconds": random.randint(10, 120),
        }
        self.client.put(
            f"/cards/{card_id}/attempts/{attempt_id}/upload-complete",
            json=payload,
            headers=self.get_headers(),
            name="[이어하기] 4. 업로드 완료",
        )

    @task
    def step5_check_feedback(self):
        """Step 5: 피드백 결과 조회"""
        card_id = getattr(self, "selected_card_id", random.choice(TEST_CARD_IDS))
        attempt_id = getattr(self, "attempt_id", 1)

        self.client.get(
            f"/cards/{card_id}/attempts/{attempt_id}",
            headers=self.get_headers(),
            name="[이어하기] 5. 피드백 결과 조회",
        )
        self.interrupt()


class ContinueLearningUser(HttpUser):
    """이어하기 시나리오 사용자"""
    wait_time = between(2, 5)
    tasks = [ContinueLearningScenario]
