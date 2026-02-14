"""
=============================================================================
[Stress Test] 로그인 API
=============================================================================
부하 유형: Stress Test (점진적 증가)
시나리오: 수업 끝 → 퇴근 → 저녁 학습 시간대별 점진적 로그인 증가
목적: 로그인 처리의 한계점 파악

실행:
  locust -f load_test/api/stress/test_login.py --host=https://imymemine.kr/server
=============================================================================
"""

import uuid
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from locust import HttpUser, task, between, LoadTestShape
from config.settings import (
    KAKAO_AUTH_CODE,
    KAKAO_REDIRECT_URI,
    STRESS_TEST,
)


class LoginStressShape(LoadTestShape):
    stages = STRESS_TEST["stages"]

    def tick(self):
        run_time = self.get_run_time()
        elapsed = 0
        for stage in self.stages:
            elapsed += stage["duration"]
            if run_time < elapsed:
                return (stage["users"], stage["spawn_rate"])
        return None


class LoginStressUser(HttpUser):
    wait_time = between(1, 3)

    @task(5)
    def oauth_login(self):
        payload = {
            "code": KAKAO_AUTH_CODE,
            "redirectUri": KAKAO_REDIRECT_URI,
            "deviceUuid": str(uuid.uuid4()),
        }
        self.client.post(
            "/auth/oauth/kakao",
            json=payload,
            headers={"Content-Type": "application/json"},
            name="/auth/oauth/kakao",
        )

    @task(3)
    def refresh_token(self):
        payload = {"refreshToken": "test_refresh_token"}
        self.client.post(
            "/auth/refresh",
            json=payload,
            headers={"Content-Type": "application/json"},
            name="/auth/refresh",
        )
