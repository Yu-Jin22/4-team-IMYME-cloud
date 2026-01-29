"""
=============================================================================
[Load Test] 피드백 카드 조회 API (GET /cards/{cardId}/attempts/{attemptId})
=============================================================================
부하 유형: Load Test (일정 부하)
대상 API: GET /cards/{cardId}/attempts/{attemptId} (AI 피드백 카드 조회)
목적: 피드백 조회의 평균 응답 속도 기준점 측정

인증: GET /test/token/{userId} 로 JWT 토큰 자동 발급

실행:
  locust -f load_test/api/load/test_attempts.py --host=https://imymemine.kr/server
=============================================================================
"""

import random
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from locust import HttpUser, task, between
from config.settings import (
    TEST_USER_IDS,
    TEST_CARD_IDS,
    TEST_ATTEMPT_MAP,
    LOAD_TEST,
)


class AttemptsLoadUser(HttpUser):
    """
    Load Test: 50명이 일정하게 피드백 카드를 조회
    - AI 피드백 결과 확인 API의 기준 응답 시간 측정
    - 상태별 응답 (PENDING/UPLOADED/PROCESSING/COMPLETED/FAILED)
    """

    wait_time = between(1, 3)

    def on_start(self):
        """테스트용 JWT 토큰 자동 발급"""
        user_id = random.choice(TEST_USER_IDS)
        response = self.client.get(
            f"/test/token/{user_id}",
            name="/test/token/{userId} [토큰 발급]",
        )
        if response.status_code == 200:
            data = response.json()
            token = data.get("accessToken", data.get("access_token", ""))
            self.auth_headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }
        else:
            self.auth_headers = {"Content-Type": "application/json"}

    @task(5)
    def get_attempt_detail(self):
        """개별 시도 상세 조회 (피드백 결과 확인)"""
        card_id = random.choice(TEST_CARD_IDS)
        attempt_ids = TEST_ATTEMPT_MAP.get(card_id, [1])
        attempt_id = random.choice(attempt_ids)

        self.client.get(
            f"/cards/{card_id}/attempts/{attempt_id}",
            headers=self.auth_headers,
            name="/cards/{cardId}/attempts/{attemptId} [피드백 조회]",
        )

    @task(3)
    def get_card_detail(self):
        """카드 상세 조회 (시도 목록 포함)"""
        card_id = random.choice(TEST_CARD_IDS)
        self.client.get(
            f"/cards/{card_id}",
            headers=self.auth_headers,
            name="/cards/{cardId} [카드 상세]",
        )

    @task(2)
    def polling_attempt_status(self):
        """
        상태 폴링 시뮬레이션
        AI 분석 중일 때 프론트엔드가 주기적으로 상태 확인하는 패턴
        """
        card_id = random.choice(TEST_CARD_IDS)
        attempt_ids = TEST_ATTEMPT_MAP.get(card_id, [1])
        attempt_id = random.choice(attempt_ids)

        self.client.get(
            f"/cards/{card_id}/attempts/{attempt_id}",
            headers=self.auth_headers,
            name="/cards/{cardId}/attempts/{attemptId} [상태 폴링]",
        )
