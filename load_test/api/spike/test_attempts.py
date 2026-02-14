"""
=============================================================================
[Spike Test] 피드백 카드 조회 API
=============================================================================
부하 유형: Spike Test
시나리오: 학습 시간대에 피드백 카드 조회 급증

실행:
  locust -f load_test/api/spike/test_attempts.py --host=https://imymemine.kr/server
=============================================================================
"""

import random
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from locust import HttpUser, task, between, LoadTestShape
from config.settings import (
    TEST_USER_IDS,
    TEST_CARD_IDS,
    TEST_ATTEMPT_MAP,
    SPIKE_TEST,
)


class AttemptsSpikeShape(LoadTestShape):
    stages = SPIKE_TEST["stages"]

    def tick(self):
        run_time = self.get_run_time()
        elapsed = 0
        for stage in self.stages:
            elapsed += stage["duration"]
            if run_time < elapsed:
                return (stage["users"], stage["spawn_rate"])
        return None


class AttemptsSpikeUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        user_id = random.choice(TEST_USER_IDS)
        response = self.client.get(f"/test/token/{user_id}", name="/test/token/{userId}")
        if response.status_code == 200:
            data = response.json()
            token = data.get("accessToken", data.get("access_token", ""))
            self.auth_headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        else:
            self.auth_headers = {"Content-Type": "application/json"}

    @task(5)
    def get_attempt_detail(self):
        card_id = random.choice(TEST_CARD_IDS)
        attempt_ids = TEST_ATTEMPT_MAP.get(card_id, [1])
        attempt_id = random.choice(attempt_ids)
        self.client.get(
            f"/cards/{card_id}/attempts/{attempt_id}",
            headers=self.auth_headers,
            name="/cards/{cardId}/attempts/{attemptId}",
        )

    @task(3)
    def get_card_detail(self):
        card_id = random.choice(TEST_CARD_IDS)
        self.client.get(f"/cards/{card_id}", headers=self.auth_headers, name="/cards/{cardId}")

    @task(2)
    def polling_attempt_status(self):
        card_id = random.choice(TEST_CARD_IDS)
        attempt_ids = TEST_ATTEMPT_MAP.get(card_id, [1])
        attempt_id = random.choice(attempt_ids)
        self.client.get(
            f"/cards/{card_id}/attempts/{attempt_id}",
            headers=self.auth_headers,
            name="/cards/{cardId}/attempts/{attemptId} [폴링]",
        )
