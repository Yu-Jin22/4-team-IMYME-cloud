"""
=============================================================================
[Stress Test] 학습 목록 조회 API
=============================================================================
부하 유형: Stress Test (점진적 증가)
시나리오: 주말/평일 오후 공부 시간대 점진적 사용자 증가
목적: 서버 한계점(병목 구간) 파악

부하 패턴: 10명 → 50명 → 100명 → 200명 → 회복 (5단계)

실행:
  locust -f load_test/api/stress/test_cards.py --host=https://imymemine.kr/server
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
    STRESS_TEST,
)


class CardsStressShape(LoadTestShape):
    """
    Stress Test 부하 패턴:
    - 1단계 (0~60초):   10명, 워밍업
    - 2단계 (60~180초):  50명, 일반 부하
    - 3단계 (180~300초): 100명, 높은 부하
    - 4단계 (300~420초): 200명, 한계 부하
    - 5단계 (420~480초): 0명, 회복
    """

    stages = STRESS_TEST["stages"]

    def tick(self):
        run_time = self.get_run_time()
        elapsed = 0
        for stage in self.stages:
            elapsed += stage["duration"]
            if run_time < elapsed:
                return (stage["users"], stage["spawn_rate"])
        return None


class CardsStressUser(HttpUser):
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
