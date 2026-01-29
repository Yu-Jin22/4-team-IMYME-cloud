"""
=============================================================================
[Spike Test] 로그인 API
=============================================================================
부하 유형: Spike Test
시나리오: 시험기간/면접기간에 다수의 사용자가 동시에 로그인 시도

실행:
  locust -f load_test/api/spike/test_login.py --host=https://imymemine.kr/server
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
    SPIKE_TEST,
)


class LoginSpikeShape(LoadTestShape):
    stages = SPIKE_TEST["stages"]

    def tick(self):
        run_time = self.get_run_time()
        elapsed = 0
        for stage in self.stages:
            elapsed += stage["duration"]
            if run_time < elapsed:
                return (stage["users"], stage["spawn_rate"])
        return None


class LoginSpikeUser(HttpUser):
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
