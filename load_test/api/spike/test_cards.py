"""
=============================================================================
[Spike Test] 학습 목록 조회 API (GET /cards)
=============================================================================
부하 유형: Spike Test (갑작스런 트래픽 폭증)
시나리오: 시험기간에 학습 목록 조회가 급증
부하 패턴: 10명 → 200명 급증 → 유지 → 급감소 → 회복

실행:
  locust -f load_test/api/spike/test_cards.py --host=https://imymemine.kr/server
=============================================================================
"""

import random
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from locust import HttpUser, task, between, LoadTestShape
from config.settings import (
    TEST_USER_IDS,
    TEST_CATEGORY_IDS,
    TEST_KEYWORD_IDS,
    SPIKE_TEST,
)


class CardsSpikeShape(LoadTestShape):
    """
    Spike Test 부하 패턴:
    - 1단계 (0~30초):   10명, 평상시
    - 2단계 (30~40초):  200명, 갑자기 폭증!
    - 3단계 (40~100초): 200명, 폭증 유지
    - 4단계 (100~110초): 10명, 급감소
    - 5단계 (110~170초): 10명, 회복
    """

    stages = SPIKE_TEST["stages"]

    def tick(self):
        run_time = self.get_run_time()
        elapsed = 0
        for stage in self.stages:
            elapsed += stage["duration"]
            if run_time < elapsed:
                return (stage["users"], stage["spawn_rate"])
        return None


class CardsSpikeUser(HttpUser):
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
    def get_cards_default(self):
        with self.client.get("/cards", headers=self.auth_headers, name="/cards [기본]") as response:
            if response.status_code == 200:
                data = response.json()
                self.next_cursor = data.get("pagination", {}).get("nextCursor")

    @task(3)
    def get_cards_category_filter(self):
        category_id = random.choice(TEST_CATEGORY_IDS)
        self.client.get(f"/cards?category_id={category_id}", headers=self.auth_headers, name="/cards [카테고리]")

    @task(2)
    def get_cards_keyword_filter(self):
        keyword_id = random.choice(TEST_KEYWORD_IDS)
        self.client.get(f"/cards?keyword_ids={keyword_id}", headers=self.auth_headers, name="/cards [키워드]")

    @task(2)
    def get_cards_pagination(self):
        cursor = getattr(self, "next_cursor", None)
        if cursor:
            self.client.get(f"/cards?cursor={cursor}&limit=20", headers=self.auth_headers, name="/cards [페이징]")
        else:
            self.client.get("/cards?limit=20", headers=self.auth_headers, name="/cards [첫페이지]")
