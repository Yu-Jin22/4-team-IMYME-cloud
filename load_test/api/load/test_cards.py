"""
=============================================================================
[Load Test] 학습 목록 조회 API (GET /cards)
=============================================================================
부하 유형: Load Test (일정 부하)
대상 API: GET /cards (마이페이지 학습 목록 리스트 조회)
목적: 일정 사용자가 지속적으로 요청할 때의 평균 응답 속도 기준점 측정

인증: GET /test/token/{userId} 로 JWT 토큰 자동 발급

실행:
  locust -f load_test/api/load/test_cards.py --host=https://imymemine.kr/server
=============================================================================
"""

import random
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from locust import HttpUser, task, between
from config.settings import (
    TEST_USER_IDS,
    TEST_CATEGORY_IDS,
    TEST_KEYWORD_IDS,
    LOAD_TEST,
)


class CardsLoadUser(HttpUser):
    """
    Load Test: 50명의 사용자가 1~3초 간격으로 학습 목록을 조회
    - 평균 응답 시간의 기준점(Baseline)을 잡기 위한 테스트
    - 매주 특정 시간대에 공부 루틴이 존재하는 고정 사용자 시뮬레이션
    """

    wait_time = between(1, 3)

    def on_start(self):
        """
        사용자 시작 시 테스트용 JWT 토큰을 자동 발급받습니다.
        GET /test/token/{userId} → {"accessToken": "eyJ..."}
        """
        user_id = random.choice(TEST_USER_IDS)
        response = self.client.get(
            f"/test/token/{user_id}",
            name="/test/token/{userId} [토큰 발급]",
        )
        if response.status_code == 200:
            data = response.json()
            # 응답에서 accessToken 키를 찾아 헤더에 세팅
            token = data.get("accessToken", data.get("access_token", ""))
            self.auth_headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }
        else:
            # 토큰 발급 실패 시 빈 헤더로 진행 (401 에러 발생 예상)
            self.auth_headers = {"Content-Type": "application/json"}

    @task(5)
    def get_cards_default(self):
        """기본 조회: 파라미터 없이 최신순 20개"""
        with self.client.get(
            "/cards",
            headers=self.auth_headers,
            name="/cards [기본 조회]",
        ) as response:
            if response.status_code == 200:
                data = response.json()
                pagination = data.get("pagination", {})
                if pagination.get("nextCursor"):
                    self.next_cursor = pagination["nextCursor"]

    @task(3)
    def get_cards_with_category_filter(self):
        """카테고리 필터 조회"""
        category_id = random.choice(TEST_CATEGORY_IDS)
        self.client.get(
            f"/cards?category_id={category_id}",
            headers=self.auth_headers,
            name="/cards [카테고리 필터]",
        )

    @task(2)
    def get_cards_with_keyword_filter(self):
        """키워드 필터 조회"""
        keyword_id = random.choice(TEST_KEYWORD_IDS)
        self.client.get(
            f"/cards?keyword_ids={keyword_id}",
            headers=self.auth_headers,
            name="/cards [키워드 필터]",
        )

    @task(2)
    def get_cards_pagination(self):
        """커서 기반 페이지네이션 (스크롤 추가 로딩)"""
        cursor = getattr(self, "next_cursor", None)
        if cursor:
            self.client.get(
                f"/cards?cursor={cursor}&limit=20",
                headers=self.auth_headers,
                name="/cards [페이지네이션]",
            )
        else:
            self.client.get(
                "/cards?limit=20",
                headers=self.auth_headers,
                name="/cards [첫 페이지]",
            )
