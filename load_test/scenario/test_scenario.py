"""
=============================================================================
MINE 부하 테스트 - 시나리오 테스트
=============================================================================
실제 사용자 행동 흐름을 시뮬레이션하는 시나리오 기반 부하 테스트입니다.

시나리오별 가중치:
  | 순위   | 시나리오  | 가중치 | 설명                                      |
  |--------|-----------|--------|-------------------------------------------|
  | 1순위  | 첫 학습   | 50%    | MVP 특성상 첫 사용자가 많고 고정 사용자가 적어, 첫 학습이 많이 이루어질 것으로 판단 |
  | 2순위  | 이어하기  | 30%    | 이전에 사용했던 사용자가 재 방문시 해당 서비스를 가장 먼저 사용할 것이라고 판단 |
  | 3순위  | 복습      | 20%    | 학습 후, 본인이 피드백 받은 내용을 다시 보는 사용자가 존재할 것이라고 예상 |

실행 방법:
  # Load Test
  locust -f load_test/scenario/test_scenario.py --host=https://imymemine.kr/server \
    --users 50 --spawn-rate 5 --run-time 5m

  # Stress Test (LoadTestShape 사용)
  locust -f load_test/scenario/test_scenario.py --host=https://imymemine.kr/server \
    ScenarioStressTest

  # Spike Test (LoadTestShape 사용)
  locust -f load_test/scenario/test_scenario.py --host=https://imymemine.kr/server \
    ScenarioSpikeTest
=============================================================================
"""

import random
import uuid
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from locust import HttpUser, task, between, SequentialTaskSet, LoadTestShape
from config.settings import (
    AUTH_TOKEN,
    KAKAO_AUTH_CODE,
    KAKAO_REDIRECT_URI,
    DEVICE_UUID,
    TEST_CARD_IDS,
    TEST_CATEGORY_IDS,
    TEST_KEYWORD_IDS,
    TEST_ATTEMPT_MAP,
    STRESS_TEST,
    SPIKE_TEST,
)


def get_auth_headers():
    return {
        "Authorization": AUTH_TOKEN,
        "Content-Type": "application/json",
    }


# =============================================================================
# 시나리오 1: 첫 학습 (가중치 50%)
# =============================================================================
# 흐름: 로그인 → 메인페이지 → 카테고리 선택 → 키워드 선택 → 녹음 및 피드백 요청 → 피드백 카드 조회
# 이유: MVP 특성상 첫 사용자가 많고 고정 사용자가 적어, 첫 학습이 많이 이루어질 것으로 판단
class FirstLearningScenario(SequentialTaskSet):
    """
    첫 학습 시나리오: 신규 사용자가 처음으로 학습하는 전체 흐름
    - 카테고리 → 키워드 → 카드 생성 → 녹음 → 피드백 조회
    - 전체 트래픽의 50%를 차지할 것으로 예상 (MVP 특성)
    """

    @task
    def step1_login(self):
        """Step 1: 로그인"""
        payload = {
            "code": KAKAO_AUTH_CODE,
            "redirectUri": KAKAO_REDIRECT_URI,
            "deviceUuid": str(uuid.uuid4()),
        }
        self.client.post(
            "/auth/oauth/kakao",
            json=payload,
            headers={"Content-Type": "application/json"},
            name="[첫학습] 1. 로그인",
        )

    @task
    def step2_main_page(self):
        """Step 2: 메인페이지"""
        self.client.get(
            "/users/me",
            headers=get_auth_headers(),
            name="[첫학습] 2. 메인페이지(프로필)",
        )

    @task
    def step3_select_category(self):
        """Step 3: 카테고리 선택 (목록 조회)"""
        self.client.get(
            "/categories?isActive=true",
            headers=get_auth_headers(),
            name="[첫학습] 3. 카테고리 선택",
        )

    @task
    def step4_select_keyword(self):
        """Step 4: 키워드 선택 (카테고리별 키워드 조회)"""
        category_id = random.choice(TEST_CATEGORY_IDS)
        self.client.get(
            f"/categories/{category_id}/keywords",
            headers=get_auth_headers(),
            name="[첫학습] 4. 키워드 선택",
        )

    @task
    def step5_create_card(self):
        """Step 5: 카드 생성"""
        payload = {
            "categoryId": random.choice(TEST_CATEGORY_IDS),
            "keywordId": random.choice(TEST_KEYWORD_IDS),
            "title": f"테스트 카드 {random.randint(1, 9999)}",
        }
        with self.client.post(
            "/cards",
            json=payload,
            headers=get_auth_headers(),
            name="[첫학습] 5. 카드 생성",
        ) as response:
            if response.status_code == 201:
                data = response.json()
                self.created_card_id = data.get("id", random.choice(TEST_CARD_IDS))

    @task
    def step6_presigned_url(self):
        """Step 6: 녹음 업로드를 위한 Presigned URL 발급"""
        card_id = getattr(self, "created_card_id", random.choice(TEST_CARD_IDS))
        payload = {
            "card_id": card_id,
            "file_extension": "mp3",
        }
        with self.client.post(
            "/learning/presigned-url",
            json=payload,
            headers=get_auth_headers(),
            name="[첫학습] 6. Presigned URL 발급",
        ) as response:
            if response.status_code == 201:
                data = response.json()
                self.attempt_id = data.get("attempt_id", 1)

    @task
    def step7_upload_complete(self):
        """Step 7: 업로드 완료 알림 (PENDING → UPLOADED)"""
        card_id = getattr(self, "created_card_id", random.choice(TEST_CARD_IDS))
        attempt_id = getattr(self, "attempt_id", 1)
        payload = {
            "audio_url": f"https://s3.example.com/test/audio_{random.randint(1, 9999)}.mp3",
            "duration_seconds": random.randint(10, 120),
        }
        self.client.put(
            f"/cards/{card_id}/attempts/{attempt_id}/upload-complete",
            json=payload,
            headers=get_auth_headers(),
            name="[첫학습] 7. 업로드 완료",
        )

    @task
    def step8_check_feedback(self):
        """Step 8: 피드백 결과 조회"""
        card_id = getattr(self, "created_card_id", random.choice(TEST_CARD_IDS))
        attempt_id = getattr(self, "attempt_id", 1)

        self.client.get(
            f"/cards/{card_id}/attempts/{attempt_id}",
            headers=get_auth_headers(),
            name="[첫학습] 8. 피드백 결과 조회",
        )
        self.interrupt()


# =============================================================================
# 시나리오 2: 이어하기 (가중치 30%)
# =============================================================================
# 흐름: 로그인 → 메인페이지 → 마이페이지(학습 목록 조회) → 녹음 및 피드백 요청 → 피드백 카드 조회
# 이유: 이전에 사용했던 사용자가 재 방문시 해당 서비스를 가장 먼저 사용할 것이라고 판단
class ContinueLearningScenario(SequentialTaskSet):
    """
    이어하기 시나리오: 기존 카드로 다시 학습하는 흐름
    - 이미 생성된 카드에서 새로운 시도(Attempt)를 생성
    - 전체 트래픽의 30%를 차지할 것으로 예상
    """

    @task
    def step1_login(self):
        """Step 1: 로그인"""
        payload = {
            "code": KAKAO_AUTH_CODE,
            "redirectUri": KAKAO_REDIRECT_URI,
            "deviceUuid": str(uuid.uuid4()),
        }
        self.client.post(
            "/auth/oauth/kakao",
            json=payload,
            headers={"Content-Type": "application/json"},
            name="[첫학습] 1. 로그인",
        )

    @task
    def step2_main_page(self):
        """Step 2: 메인페이지"""
        self.client.get(
            "/users/me",
            headers=get_auth_headers(),
            name="[첫학습] 2. 메인페이지(프로필)",
        )

    @task
    def step3_select_category(self):
        """Step 3: 카테고리 선택 (목록 조회)"""
        self.client.get(
            "/categories?isActive=true",
            headers=get_auth_headers(),
            name="[첫학습] 3. 카테고리 선택",
        )

    @task
    def step4_select_keyword(self):
        """Step 4: 키워드 선택 (카테고리별 키워드 조회)"""
        category_id = random.choice(TEST_CATEGORY_IDS)
        self.client.get(
            f"/categories/{category_id}/keywords",
            headers=get_auth_headers(),
            name="[첫학습] 4. 키워드 선택",
        )

    @task
    def step5_create_card(self):
        """Step 5: 카드 생성"""
        payload = {
            "categoryId": random.choice(TEST_CATEGORY_IDS),
            "keywordId": random.choice(TEST_KEYWORD_IDS),
            "title": f"테스트 카드 {random.randint(1, 9999)}",
        }
        with self.client.post(
            "/cards",
            json=payload,
            headers=get_auth_headers(),
            name="[첫학습] 5. 카드 생성",
        ) as response:
            if response.status_code == 201:
                data = response.json()
                self.created_card_id = data.get("id", random.choice(TEST_CARD_IDS))

    @task
    def step6_presigned_url(self):
        """Step 6: 녹음 업로드를 위한 Presigned URL 발급"""
        card_id = getattr(self, "created_card_id", random.choice(TEST_CARD_IDS))
        payload = {
            "card_id": card_id,
            "file_extension": "mp3",
        }
        with self.client.post(
            "/learning/presigned-url",
            json=payload,
            headers=get_auth_headers(),
            name="[첫학습] 6. Presigned URL 발급",
        ) as response:
            if response.status_code == 201:
                data = response.json()
                self.attempt_id = data.get("attempt_id", 1)

    @task
    def step7_upload_complete(self):
        """Step 7: 업로드 완료 알림 (PENDING → UPLOADED)"""
        card_id = getattr(self, "created_card_id", random.choice(TEST_CARD_IDS))
        attempt_id = getattr(self, "attempt_id", 1)
        payload = {
            "audio_url": f"https://s3.example.com/test/audio_{random.randint(1, 9999)}.mp3",
            "duration_seconds": random.randint(10, 120),
        }
        self.client.put(
            f"/cards/{card_id}/attempts/{attempt_id}/upload-complete",
            json=payload,
            headers=get_auth_headers(),
            name="[첫학습] 7. 업로드 완료",
        )

    @task
    def step8_check_feedback(self):
        """Step 8: 피드백 결과 조회"""
        card_id = getattr(self, "created_card_id", random.choice(TEST_CARD_IDS))
        attempt_id = getattr(self, "attempt_id", 1)

        self.client.get(
            f"/cards/{card_id}/attempts/{attempt_id}",
            headers=get_auth_headers(),
            name="[첫학습] 8. 피드백 결과 조회",
        )
        self.interrupt()


# =============================================================================
# 시나리오 3: 반복 학습 (가중치 20%)
# =============================================================================
# 흐름: 로그인 → 메인페이지 → 마이페이지(학습 목록 조회)
#       → 녹음 및 피드백 요청 → 피드백 카드 조회
# 이유: 같은 주제 반복 연습, 피드백 요청 부하
class RepeatLearningScenario(SequentialTaskSet):
    """
    반복 학습 시나리오: 기존 카드로 다시 학습하는 흐름
    - 이미 생성된 카드에서 새로운 시도(Attempt)를 생성
    - 전체 트래픽의 20%
    """

    @task
    def step1_login(self):
        """Step 1: 로그인"""
        payload = {
            "code": KAKAO_AUTH_CODE,
            "redirectUri": KAKAO_REDIRECT_URI,
            "deviceUuid": str(uuid.uuid4()),
        }
        self.client.post(
            "/auth/oauth/kakao",
            json=payload,
            headers={"Content-Type": "application/json"},
            name="[반복학습] 1. 로그인",
        )

    @task
    def step2_main_page(self):
        """Step 2: 메인페이지"""
        self.client.get(
            "/users/me",
            headers=get_auth_headers(),
            name="[반복학습] 2. 메인페이지(프로필)",
        )

    @task
    def step3_card_list(self):
        """Step 3: 학습 목록 조회"""
        with self.client.get(
            "/cards",
            headers=get_auth_headers(),
            name="[반복학습] 3. 학습 목록 조회",
        ) as response:
            if response.status_code == 200:
                data = response.json()
                cards = data.get("cards", [])
                if cards:
                    self.selected_card_id = cards[0].get("id", TEST_CARD_IDS[0])
                else:
                    self.selected_card_id = random.choice(TEST_CARD_IDS)

    @task
    def step4_presigned_url(self):
        """Step 4: 녹음 업로드를 위한 Presigned URL 발급"""
        card_id = getattr(self, "selected_card_id", random.choice(TEST_CARD_IDS))
        payload = {
            "card_id": card_id,
            "file_extension": "mp3",
        }
        with self.client.post(
            "/learning/presigned-url",
            json=payload,
            headers=get_auth_headers(),
            name="[반복학습] 4. Presigned URL 발급",
        ) as response:
            if response.status_code == 201:
                data = response.json()
                self.attempt_id = data.get("attempt_id", 1)

    @task
    def step5_upload_complete(self):
        """Step 5: 업로드 완료"""
        card_id = getattr(self, "selected_card_id", random.choice(TEST_CARD_IDS))
        attempt_id = getattr(self, "attempt_id", 1)
        payload = {
            "audio_url": f"https://s3.example.com/test/audio_{random.randint(1, 9999)}.mp3",
            "duration_seconds": random.randint(10, 120),
        }
        self.client.put(
            f"/cards/{card_id}/attempts/{attempt_id}/upload-complete",
            json=payload,
            headers=get_auth_headers(),
            name="[반복학습] 5. 업로드 완료",
        )

    @task
    def step6_check_feedback(self):
        """Step 6: 피드백 결과 조회"""
        card_id = getattr(self, "selected_card_id", random.choice(TEST_CARD_IDS))
        attempt_id = getattr(self, "attempt_id", 1)

        self.client.get(
            f"/cards/{card_id}/attempts/{attempt_id}",
            headers=get_auth_headers(),
            name="[반복학습] 6. 피드백 결과 조회",
        )
        self.interrupt()


# =============================================================================
# 시나리오 4: 빠른 학습 (가중치 10%)
# =============================================================================
# 흐름: 메인페이지 → 카테고리 선택 → 녹음 및 피드백 요청 → 피드백 카드 조회
# 이유: 로그인 유지 상태에서 바로 학습 (로그인 단계 생략)
class QuickLearningScenario(SequentialTaskSet):
    """
    빠른 학습 시나리오: 이미 로그인된 상태에서 바로 학습
    - 로그인 단계를 건너뛰고 바로 카테고리 선택부터 시작
    - 전체 트래픽의 10%
    """

    @task
    def step1_main_page(self):
        """Step 1: 메인페이지 (로그인 유지 상태)"""
        self.client.get(
            "/users/me",
            headers=get_auth_headers(),
            name="[빠른학습] 1. 메인페이지(프로필)",
        )

    @task
    def step2_select_category(self):
        """Step 2: 카테고리 선택"""
        self.client.get(
            "/categories?isActive=true",
            headers=get_auth_headers(),
            name="[빠른학습] 2. 카테고리 선택",
        )

    @task
    def step3_select_keyword(self):
        """Step 3: 키워드 선택"""
        category_id = random.choice(TEST_CATEGORY_IDS)
        self.client.get(
            f"/categories/{category_id}/keywords",
            headers=get_auth_headers(),
            name="[빠른학습] 3. 키워드 선택",
        )

    @task
    def step4_create_card_and_presigned(self):
        """Step 4: 카드 생성 + Presigned URL 발급"""
        card_payload = {
            "categoryId": random.choice(TEST_CATEGORY_IDS),
            "keywordId": random.choice(TEST_KEYWORD_IDS),
            "title": f"빠른학습 {random.randint(1, 9999)}",
        }
        with self.client.post(
            "/cards",
            json=card_payload,
            headers=get_auth_headers(),
            name="[빠른학습] 4-1. 카드 생성",
        ) as response:
            if response.status_code == 201:
                data = response.json()
                self.created_card_id = data.get("id", random.choice(TEST_CARD_IDS))

        card_id = getattr(self, "created_card_id", random.choice(TEST_CARD_IDS))
        presigned_payload = {
            "card_id": card_id,
            "file_extension": "mp3",
        }
        with self.client.post(
            "/learning/presigned-url",
            json=presigned_payload,
            headers=get_auth_headers(),
            name="[빠른학습] 4-2. Presigned URL 발급",
        ) as response:
            if response.status_code == 201:
                data = response.json()
                self.attempt_id = data.get("attempt_id", 1)

    @task
    def step5_upload_complete(self):
        """Step 5: 업로드 완료"""
        card_id = getattr(self, "created_card_id", random.choice(TEST_CARD_IDS))
        attempt_id = getattr(self, "attempt_id", 1)
        payload = {
            "audio_url": f"https://s3.example.com/test/audio_{random.randint(1, 9999)}.mp3",
            "duration_seconds": random.randint(10, 120),
        }
        self.client.put(
            f"/cards/{card_id}/attempts/{attempt_id}/upload-complete",
            json=payload,
            headers=get_auth_headers(),
            name="[빠른학습] 5. 업로드 완료",
        )

    @task
    def step6_check_feedback(self):
        """Step 6: 피드백 결과 조회"""
        card_id = getattr(self, "created_card_id", random.choice(TEST_CARD_IDS))
        attempt_id = getattr(self, "attempt_id", 1)

        self.client.get(
            f"/cards/{card_id}/attempts/{attempt_id}",
            headers=get_auth_headers(),
            name="[빠른학습] 6. 피드백 결과 조회",
        )
        self.interrupt()


# =============================================================================
# 시나리오 사용자 정의 (가중치 반영)
# =============================================================================
# Locust의 @task(weight) 데코레이터로 시나리오별 가중치를 설정합니다.
# weight 값이 해당 시나리오가 선택될 확률 비율입니다.

class ScenarioLoadTest(HttpUser):
    """
    시나리오 Load Test: 일정 부하에서 실제 사용 패턴 재현
    가중치: 복습(50%), 첫학습(20%), 반복학습(20%), 빠른학습(10%)
    """

    wait_time = between(2, 5)

    # 각 시나리오를 tasks 리스트에 가중치와 함께 등록
    # {TaskSet: weight} 형태로 지정하면 Locust가 가중치에 따라 시나리오를 선택
    tasks = {
        ReviewScenario: 50,         # 복습: 50%
        FirstLearningScenario: 20,  # 첫 학습: 20%
        RepeatLearningScenario: 20, # 반복 학습: 20%
        QuickLearningScenario: 10,  # 빠른 학습: 10%
    }


# =============================================================================
# Stress Test Shape (시나리오)
# =============================================================================
class ScenarioStressShape(LoadTestShape):
    """
    시나리오 기반 Stress Test: 점진적으로 사용자를 늘리며 시나리오 실행
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


class ScenarioStressTest(HttpUser):
    wait_time = between(2, 5)
    tasks = {
        ReviewScenario: 50,
        FirstLearningScenario: 20,
        RepeatLearningScenario: 20,
        QuickLearningScenario: 10,
    }


# =============================================================================
# Spike Test Shape (시나리오)
# =============================================================================
class ScenarioSpikeShape(LoadTestShape):
    """
    시나리오 기반 Spike Test: 시험기간 갑작스런 사용자 폭증 시뮬레이션
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


class ScenarioSpikeTest(HttpUser):
    wait_time = between(2, 5)
    tasks = {
        ReviewScenario: 50,
        FirstLearningScenario: 20,
        RepeatLearningScenario: 20,
        QuickLearningScenario: 10,
    }
