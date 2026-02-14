"""
=============================================================================
[Load Test] 로그인 API (POST /auth/oauth/kakao)
=============================================================================
부하 유형: Load Test (일정 부하)
대상 API: POST /auth/oauth/{provider} (카카오 OAuth 로그인)
목적: 로그인 처리의 평균 응답 속도 기준점 측정

주의: 실제 카카오 인가코드는 일회성이므로, 테스트 환경에서는
      Mock 처리가 필요하거나 401 에러를 예상하고 서버 처리 성능만 측정

실행:
  locust -f load_test/api/load/test_login.py --host=https://imymemine.kr/server
=============================================================================
"""

import uuid
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from locust import HttpUser, task, between
from config.settings import (
    KAKAO_AUTH_CODE,
    KAKAO_REDIRECT_URI,
    LOAD_TEST,
)


class LoginLoadUser(HttpUser):
    """
    Load Test: 50명이 일정하게 로그인 요청
    - 로그인/회원가입 API의 기준 응답 시간 측정
    - 터지면 서비스 접근 불가이므로 중요한 API
    """

    wait_time = between(1, 3)

    @task(5)
    def oauth_login(self):
        """
        카카오 OAuth 로그인 요청
        매번 다른 deviceUuid로 다중 기기 시뮬레이션
        """
        payload = {
            "code": KAKAO_AUTH_CODE,
            "redirectUri": KAKAO_REDIRECT_URI,
            "deviceUuid": str(uuid.uuid4()),
        }
        self.client.post(
            "/auth/oauth/kakao",
            json=payload,
            headers={"Content-Type": "application/json"},
            name="/auth/oauth/kakao [로그인]",
        )

    @task(3)
    def refresh_token(self):
        """
        토큰 갱신 요청
        액세스 토큰 만료 시 호출 (1시간마다)
        """
        payload = {
            "refreshToken": "test_refresh_token_placeholder",
        }
        self.client.post(
            "/auth/refresh",
            json=payload,
            headers={"Content-Type": "application/json"},
            name="/auth/refresh [토큰 갱신]",
        )
