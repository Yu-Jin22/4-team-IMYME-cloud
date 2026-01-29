"""
=============================================================================
MINE 부하 테스트 - 공통 설정 (settings.py)
=============================================================================
모든 테스트 스크립트가 참조하는 설정값을 한 곳에서 관리합니다.
환경변수로 오버라이드할 수 있어 CI/CD 파이프라인에서도 유연하게 사용 가능합니다.
=============================================================================
"""

import os


# =============================================================================
# 1. 서버 설정
# =============================================================================
BASE_URL = os.getenv("LOAD_TEST_BASE_URL", "http://3.39.31.181:8080")

# =============================================================================
# 2. 인증 설정
# =============================================================================
# JWT 토큰 CSV 파일 경로
JWT_TOKENS_CSV = os.path.join(os.path.dirname(__file__), "..", "..", "jwt_tokens.csv")

# CSV에서 JWT 토큰 로드
import csv
JWT_TOKENS = {}
if os.path.exists(JWT_TOKENS_CSV):
    with open(JWT_TOKENS_CSV, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            user_id = int(row['user_id'])
            JWT_TOKENS[user_id] = f"Bearer {row['jwt_token']}"

# 폴백용 기본 토큰 (CSV 로드 실패 시)
AUTH_TOKEN = os.getenv(
    "LOAD_TEST_AUTH_TOKEN",
    "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiaWF0IjoxNzY5NTQ4NzM1LCJleHAiOjQ5MjMxNDg3MzV9.nk29IpZ8GgB2qUgkaeNwFDBCGvAhAifRwojMjROncwk"
)

# 테스트용 사용자 ID 목록 (CSV에서 로드된 user_id)
TEST_USER_IDS = list(JWT_TOKENS.keys()) if JWT_TOKENS else list(range(1, 101))

# 테스트용 디바이스 UUID (로그인 시 필요)
DEVICE_UUID = os.getenv("LOAD_TEST_DEVICE_UUID", "550e8400-e29b-41d4-a716-446655440000")

# 카카오 OAuth 인가코드 (로그인 부하 테스트용)
KAKAO_AUTH_CODE = os.getenv("LOAD_TEST_KAKAO_CODE", "test_authorization_code")
KAKAO_REDIRECT_URI = os.getenv("LOAD_TEST_REDIRECT_URI", "https://imymemine.kr/callback")

# =============================================================================
# 3. 테스트 데이터 설정
# =============================================================================
# 실제 DB에 존재하는 값으로 교체 필요
TEST_CARD_IDS = [1, 2, 3, 4, 5]
TEST_CATEGORY_IDS = [1, 2, 3]
TEST_KEYWORD_IDS = [1, 2, 3, 4, 5]
TEST_ATTEMPT_MAP = {
    1: [1, 2],
    2: [3],
    3: [4, 5],
}

# =============================================================================
# 4. 부하 테스트 프로파일
# =============================================================================

# --- Load Test (일정 부하) ---
LOAD_TEST = {
    "users": 50,
    "spawn_rate": 5,
    "run_time": "5m",
}

# --- Stress Test (점진적 증가) ---
STRESS_TEST = {
    "stages": [
        {"duration": 60,  "users": 10,  "spawn_rate": 2},   # 1단계: 워밍업
        {"duration": 120, "users": 50,  "spawn_rate": 5},   # 2단계: 일반 부하
        {"duration": 120, "users": 100, "spawn_rate": 10},  # 3단계: 높은 부하
        {"duration": 120, "users": 200, "spawn_rate": 20},  # 4단계: 한계 부하
        {"duration": 60,  "users": 0,   "spawn_rate": 10},  # 5단계: 회복
    ],
}

# --- Spike Test (갑작스런 폭증) ---
SPIKE_TEST = {
    "stages": [
        {"duration": 30,  "users": 10,  "spawn_rate": 2},   # 1단계: 평상시
        {"duration": 10,  "users": 200, "spawn_rate": 50},  # 2단계: 스파이크!
        {"duration": 60,  "users": 200, "spawn_rate": 50},  # 3단계: 스파이크 유지
        {"duration": 10,  "users": 10,  "spawn_rate": 50},  # 4단계: 급감소
        {"duration": 60,  "users": 10,  "spawn_rate": 2},   # 5단계: 회복
    ],
}
