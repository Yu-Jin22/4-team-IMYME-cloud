# 첫 학습 시나리오 부하 테스트

## 개요

첫 학습 시나리오는 신규 사용자가 MINE 서비스를 처음 사용할 때 거치는 핵심 흐름입니다.

**흐름:**
1. 로그인 (JWT 토큰 사용)
2. 메인페이지 (프로필 조회)
3. 카테고리 선택
4. 키워드 선택
5. 카드 생성
6. Attempt 생성 (녹음 시도)
7. 피드백 결과 조회

---

## 테스트 종류

### 1. Load Test (부하 테스트)

**목적:**
- 매주 특정 시간대에 공부 루틴이 존재하는 고정 사용자의 일상적인 사용량 시뮬레이션
- 일정한 부하에서 시스템 안정성 확인
- 다른 테스트의 응답속도 기준점 결정

**테스트 설정:**
- 동시 사용자: 10명 (피크 타임 기준)
- 증가율: 초당 2명
- 실행 시간: 10분
- 특징: **일정한 부하 유지**

**실행 방법:**

**방법 1: Web UI 사용 (권장)**
```bash
locust -f load_test/scenario/first_learning/load_test.py \
  --host=http://3.39.31.181:8080
```
- 브라우저에서 `http://localhost:8089` 접속
- Number of users: 10
- Spawn rate: 2
- Run time: 10m (또는 수동으로 Stop 버튼 클릭)
- 실시간 그래프와 통계 확인 가능

**방법 2: Headless 모드 (CLI)**
```bash
locust -f load_test/scenario/first_learning/load_test.py \
  --host=http://3.39.31.181:8080 \
  --users 10 --spawn-rate 2 --run-time 10m --headless
```

**기대 결과:**
- 성공률: ≥ 99%
- 평균 응답 시간: < 200ms
- 5xx 에러율: ≤ 1%

---

### 2. Stress Test (스트레스 테스트)

**목적:**
- 밥을 먹고 공부하는 사용자, 밥을 먹고 조금 쉬었다가 공부하는 사용자 등
- 공부를 하면서 MINE 서비스를 사용하는 사용자가 누적되는 상황 시뮬레이션
- 점진적으로 증가하는 부하를 견디는지 확인
- **p95 응답 시간이 400ms를 넘어가는 지점 파악**

**테스트 설정:**
- 동시 사용자: 0 → 50명 (점진적 증가, 필요시 더 늘림)
- 증가율: 초당 1명 (천천히 증가)
- 실행 시간: 수동 중단 (p95 > 400ms 도달 시)
- 특징: **사용자가 누적되면서 부하가 지속적으로 증가, 성능 한계 지점 관찰**

**실행 방법:**

**방법 1: Web UI 사용 (권장)**
```bash
locust -f load_test/scenario/first_learning/stress_test.py \
  --host=http://3.39.31.181:8080
```

**방법 2: Headless 모드**
```bash
locust -f load_test/scenario/first_learning/stress_test.py \
  --host=http://3.39.31.181:8080 \
  --users 50 --spawn-rate 1 --headless
```

**측정 목표:**
- **p95 응답 시간이 400ms를 넘어가는 시점의 동시 사용자 수 파악**
- 사용자 증가에 따른 응답 시간 추이 관찰
- Web UI의 Charts 탭에서 실시간 p95 모니터링
- p95 > 400ms 도달 시 Stop 버튼 클릭하여 해당 지점 기록

---

### 3. Spike Test (스파이크 테스트)

**목적:**
- 시험기간이나 면접기간 때 많이 확 몰리는 환경 시뮬레이션
- 갑작스러운 사용자 급증 상황에서 시스템 안정성 확인
- 바이럴/홍보 효과로 인한 순간 트래픽 증가 대응 능력 검증

**테스트 설정:**
- 동시 사용자: 50명 (CCU의 약 17배)
- 증가율: 초당 5명 (빠른 증가)
- 실행 시간: 5분
- 특징: **짧은 시간에 급격한 부하 증가**

**실행 방법:**

**방법 1: Web UI 사용 (권장)**
```bash
locust -f load_test/scenario/first_learning/spike_test.py \
  --host=http://3.39.31.181:8080
```

**방법 2: Headless 모드**
```bash
locust -f load_test/scenario/first_learning/spike_test.py \
  --host=http://3.39.31.181:8080 \
  --users 50 --spawn-rate 5 --run-time 5m --headless
```

**주의사항:**
- MVP1 예상치를 크게 초과하는 부하
- 성능 저하 및 에러 발생 예상
- 실제 운영 환경에서는 주의해서 실행

**측정 목표:**
- 시스템 한계 파악
- 5xx 에러 발생 시점 확인
- DB 커넥션 풀, 메모리, CPU 사용량 모니터링
- 장애 복구 시간 측정

---

## 테스트 실행 순서 (권장)

### Phase 1: Load Test
```bash
# Web UI 모드
locust -f load_test/scenario/first_learning/load_test.py \
  --host=http://3.39.31.181:8080
```
→ 기본 성능 기준점 확보

### Phase 2: Stress Test
```bash
# Web UI 모드
locust -f load_test/scenario/first_learning/stress_test.py \
  --host=http://3.39.31.181:8080
```
→ 점진적 부하 증가에 대한 대응 능력 확인

### Phase 3: Spike Test
```bash
# Web UI 모드
locust -f load_test/scenario/first_learning/spike_test.py \
  --host=http://3.39.31.181:8080
```
→ 급격한 트래픽 증가에 대한 시스템 한계 파악

---

## 파일 구조

```
load_test/scenario/first_learning/
├── README.md              # 이 파일
├── base_scenario.py       # 기본 시나리오 (원본)
├── load_test.py          # Load Test (CCU 3명, 10분)
├── stress_test.py        # Stress Test (0→15명, 15분)
└── spike_test.py         # Spike Test (50명, 5분)
```

---

## 측정 지표

### API별 목표 응답 시간

| API | Load Test | Stress Test | Spike Test |
|-----|-----------|-------------|------------|
| GET /users/me | < 100ms | < 150ms | 측정 |
| GET /categories | < 100ms | < 150ms | 측정 |
| GET /categories/{id}/keywords | < 150ms | < 200ms | 측정 |
| POST /cards | < 200ms | < 250ms | 측정 |
| POST /cards/{id}/attempts | < 200ms | < 250ms | 측정 |
| GET /cards/{id}/attempts/{id} | < 150ms | < 200ms | 측정 |

### 전체 시스템 목표

| 지표 | Load Test | Stress Test | Spike Test |
|------|-----------|-------------|------------|
| 성공률 | ≥ 99% | ≥ 99% | 측정 |
| 5xx 에러율 | ≤ 1% | ≤ 1% | 측정 |
| 평균 응답 시간 | < 200ms | < 300ms | 측정 |

---

## 결과 기록 템플릿

### Load Test
```
테스트 일시: YYYY-MM-DD HH:MM
설정: Users=10, Spawn-rate=2, Run-time=10m

총 요청 수:
성공:
실패:
성공률:

평균 응답 시간:
P50:
P95:
P99:

5xx 에러:
4xx 에러:
```

### Stress Test
```
테스트 일시: YYYY-MM-DD HH:MM
설정: Users=15, Spawn-rate=0.5, Run-time=15m

총 요청 수:
성공:
실패:
성공률:

평균 응답 시간:
P50:
P95:
P99:

5xx 에러:
4xx 에러:

사용자 증가 구간별 응답 시간:
- 0~5명:
- 5~10명:
- 10~15명:
```

### Spike Test
```
테스트 일시: YYYY-MM-DD HH:MM
설정: Users=50, Spawn-rate=5, Run-time=5m

총 요청 수:
성공:
실패:
성공률:

평균 응답 시간:
P50:
P95:
P99:

5xx 에러:
4xx 에러:

시스템 한계 관찰:
- 에러 발생 시작 시점:
- CPU/메모리 사용량:
- DB 커넥션 풀 상태:
```

---

## 모니터링 체크리스트

테스트 실행 중 확인 사항:

**서버 리소스:**
- [ ] CPU 사용률 (평균, 최대)
- [ ] 메모리 사용률
- [ ] DB 커넥션 풀 사용량
- [ ] Nginx 동시 연결 수

**애플리케이션:**
- [ ] Backend 로그에 에러 없음
- [ ] DB 슬로우 쿼리 발생 여부
- [ ] Nginx access log 5xx 에러 수

**네트워크:**
- [ ] 네트워크 I/O 대역폭
- [ ] 응답 지연 (latency)
