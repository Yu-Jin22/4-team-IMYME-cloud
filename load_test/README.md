# MINE 부하 테스트 (Locust)

## 폴더 구조

```
load_test/
├── config/
│   ├── __init__.py
│   └── settings.py          # 공통 설정 (URL, 토큰 자동 발급, 테스트 데이터)
├── api/                      # 부하 유형별 API 테스트
│   ├── load/                 # Load Test (일정 부하)
│   │   ├── test_cards.py     # 학습 목록 조회
│   │   ├── test_attempts.py  # 피드백 카드 조회
│   │   └── test_login.py     # 로그인
│   ├── spike/                # Spike Test (갑작스런 폭증)
│   │   ├── test_cards.py
│   │   ├── test_attempts.py
│   │   └── test_login.py
│   └── stress/               # Stress Test (점진적 증가)
│       ├── test_cards.py
│       └── test_login.py
├── scenario/                 # 시나리오 기반 부하 테스트
│   ├── first_learning.py     # 첫 학습 시나리오
│   ├── continue_learning.py  # 이어하기 시나리오
│   └── review.py             # 복습 시나리오
├── requirements.txt
└── README.md
```

## 설치

```bash
cd load_test
pip install -r requirements.txt
```

## 인증 (중요!)

### OAuth 로그인 우회 방법

일반적으로 OAuth 로그인이 있는 환경에서 부하 테스트를 하는 방법:

1. **테스트 전용 토큰 발급 엔드포인트 사용** ⭐ (현재 사용 중)
   - `GET /test/token/{userId}` 엔드포인트로 JWT 토큰 자동 발급
   - **중요**: 서버에서 이 엔드포인트는 인증 없이 접근 가능하도록 설정 필요
   - 모든 시나리오는 `on_start()` 메서드에서 자동으로 토큰 발급

2. **사전 발급 토큰 사용**
   - 미리 유효한 JWT 토큰을 발급받아 `config/settings.py`의 `AUTH_TOKEN`에 설정
   - 토큰 만료 시간이 충분히 길어야 함

3. **Mock OAuth 서버**
   - 테스트 환경 전용 가짜 OAuth 서버 구축

### 설정 파일

`config/settings.py`에서 설정:
```python
AUTH_TOKEN = "Bearer eyJ..."  # 폴백용 기본 토큰
TEST_USER_IDS = [1, 2, 3, 4, 5]  # DB에 존재하는 사용자 ID
TEST_CARD_IDS = [1, 2, 3, 4, 5]  # 실제 카드 ID로 변경
```

## 실행 방법

### 1. Load Test (일정 부하)

**목적**: 평균 응답 속도의 기준점 측정
**패턴**: 50명의 사용자가 일정하게 요청

```bash
# 학습 목록 조회
locust -f load_test/api/load/test_cards.py --host=https://imymemine.kr/server

# 피드백 카드 조회
locust -f load_test/api/load/test_attempts.py --host=https://imymemine.kr/server

# 로그인
locust -f load_test/api/load/test_login.py --host=https://imymemine.kr/server
```

### 2. Spike Test (갑작스런 폭증)

**목적**: 시험기간/면접기간 트래픽 급증 대응 확인
**패턴**: 10명 → 200명 급증 → 유지 → 급감소 → 회복

```bash
# 학습 목록 조회
locust -f load_test/api/spike/test_cards.py --host=https://imymemine.kr/server

# 피드백 카드 조회
locust -f load_test/api/spike/test_attempts.py --host=https://imymemine.kr/server

# 로그인
locust -f load_test/api/spike/test_login.py --host=https://imymemine.kr/server
```

### 3. Stress Test (점진적 증가)

**목적**: 서버 한계점(병목 구간) 파악
**패턴**: 10명 → 50명 → 100명 → 200명 → 회복 (5단계)

```bash
# 학습 목록 조회
locust -f load_test/api/stress/test_cards.py --host=https://imymemine.kr/server

# 로그인
locust -f load_test/api/stress/test_login.py --host=https://imymemine.kr/server
```

### 4. 시나리오 테스트

실제 사용자 행동 흐름을 재현하는 3가지 시나리오:

#### 시나리오 1: 첫 학습 (우선순위 1)
**흐름**: 로그인 → 메인페이지 → 카테고리 선택 → 키워드 선택 → 녹음 및 피드백 요청 → 피드백 카드 조회
**이유**: MVP 특성상 첫 사용자가 많고 고정 사용자가 적어, 첫 학습이 많이 이루어질 것으로 판단

```bash
locust -f load_test/scenario/first_learning.py --host=https://imymemine.kr/server
```

#### 시나리오 2: 이어하기 (우선순위 2)
**흐름**: 로그인 → 메인페이지 → 마이페이지(학습 목록 조회) → 녹음 및 피드백 요청 → 피드백 카드 조회
**이유**: 이전에 사용했던 사용자가 재 방문시 해당 서비스를 가장 먼저 사용할 것이라고 판단

```bash
locust -f load_test/scenario/continue_learning.py --host=https://imymemine.kr/server
```

#### 시나리오 3: 복습 (우선순위 3)
**흐름**: 로그인 → 메인페이지 → 마이페이지(학습 목록 조회) → 피드백 카드 조회
**이유**: 학습 후, 본인이 피드백 받은 내용을 다시 보는 사용자가 존재할 것이라고 예상

```bash
locust -f load_test/scenario/review.py --host=https://imymemine.kr/server
```

### 5. Web UI 모드 (대시보드)

플래그 없이 실행하면 웹 대시보드가 열립니다:

```bash
locust -f load_test/api/load/test_cards.py --host=https://imymemine.kr/server
# → http://localhost:8089 에서 대시보드 확인
```

### 6. Headless 모드 (CI/CD용)

```bash
locust -f load_test/api/load/test_cards.py \
  --host=https://imymemine.kr/server \
  --headless \
  --users 50 --spawn-rate 5 --run-time 5m \
  --csv=results/cards_load
```

## 부하 프로파일

### Load Test
- 동시 사용자: **50명**
- 초당 생성: **5명/초**
- 지속 시간: **5분**

### Stress Test (5단계)
| 단계 | 시간 | 사용자 | 설명 |
|------|------|--------|------|
| 1단계 | 60초 | 10명 | 워밍업 |
| 2단계 | 120초 | 50명 | 일반 부하 |
| 3단계 | 120초 | 100명 | 높은 부하 |
| 4단계 | 120초 | 200명 | **한계 부하** |
| 5단계 | 60초 | 0명 | 회복 |

### Spike Test (5단계)
| 단계 | 시간 | 사용자 | 설명 |
|------|------|--------|------|
| 1단계 | 30초 | 10명 | 평상시 |
| 2단계 | 10초 | 200명 | **스파이크!** |
| 3단계 | 60초 | 200명 | 스파이크 유지 |
| 4단계 | 10초 | 10명 | 급감소 |
| 5단계 | 60초 | 10명 | 회복 |

## 테스트 대상 API

| 순위 | API | Load | Spike | Stress |
|------|-----|------|-------|--------|
| 1순위 | 학습 목록 조회 `GET /cards` | ✅ | ✅ | ✅ |
| 1순위 | 피드백 카드 조회 `GET /cards/{id}/attempts/{id}` | ✅ | ✅ | ❌ |
| 2순위 | 로그인 `POST /auth/oauth/kakao` | ✅ | ✅ | ✅ |

## 주의사항

1. **테스트 데이터**: `config/settings.py`의 `TEST_CARD_IDS`, `TEST_ATTEMPT_MAP` 등을 실제 DB 데이터에 맞게 수정
2. **카카오 OAuth**: 로그인 테스트는 실제 인가코드가 일회성이므로 Mock 서버 권장
3. **프로덕션 주의**: 실 서버 대상 테스트 시 운영팀과 사전 협의 필요
