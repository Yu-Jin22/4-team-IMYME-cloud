# 첫 학습 시나리오 - 스트레스 테스트

## 개요

스트레스 테스트는 시스템의 성능 한계와 장애 발생 지점을 파악하기 위한 테스트입니다.

---

## 테스트 종류

### 1. p95 임계점 찾기 (p95_threshold.py)

**목적:**
- p95 응답 시간이 400ms를 넘어가는 지점 파악
- 성능 저하가 시작되는 시점 확인
- 적정 동시 사용자 수 산정

**테스트 설정:**
- 동시 사용자: 0 → 50명
- 증가율: 초당 1명 (천천히 증가)
- 실행 시간: 수동 중단 (p95 > 400ms 도달 시)

**실행 방법:**
```bash
# Web UI 모드
locust -f load_test/scenario/first_learning/stress_test/p95_threshold.py \
  --host=http://3.39.31.181:8080
```

**측정 방법:**
1. Web UI → Charts 탭 열기
2. Response Times (ms) 그래프에서 95th percentile 라인 주시
3. p95가 400ms를 넘어가는 순간 Stop 버튼 클릭
4. Statistics 탭에서 해당 시점의 동시 사용자 수 기록

**측정 목표:**
- p95 = 400ms 시점의 동시 사용자 수
- 해당 시점의 평균 응답 시간
- 해당 시점의 RPS

---

### 2. 시스템 한계 테스트 (system_limit.py)

**목적:**
- 몇 명까지 스트레스 테스트를 진행했을 때 백엔드 JVM 혹은 인스턴스가 터지는지 확인
- 시스템의 물리적 한계 지점 파악
- 장애 발생 시점과 복구 시간 측정

**테스트 설정:**
- 동시 사용자: 0 → 200명
- 증가율: 초당 5명 (공격적으로 증가)
- 실행 시간: 수동 중단 (시스템 장애 발생 시)

**실행 방법:**
```bash
# Web UI 모드
locust -f load_test/scenario/first_learning/stress_test/system_limit.py \
  --host=http://3.39.31.181:8080
```

**측정 방법:**
1. Web UI → Charts 탭 + Failures 탭 동시 모니터링
2. 서버 모니터링 도구에서 CPU, 메모리, JVM Heap 확인
3. 5xx 에러율 급증 또는 서버 응답 멈춤 시점 기록
4. 해당 시점의 동시 사용자 수와 시스템 리소스 상태 기록

**측정 목표:**
- 시스템 장애 발생 시점의 동시 사용자 수
- 5xx 에러율 50% 초과 시점
- CPU 사용률 100% 도달 시점
- JVM OutOfMemoryError 발생 여부
- 서버 복구 시간

**주의사항:**
- ⚠️ **실제 운영 환경에서는 절대 실행하지 말 것**
- 개발/테스트 환경에서만 실행
- 서버가 완전히 다운될 수 있음
- 테스트 전 서버 백업 및 복구 계획 수립

---

## 테스트 실행 순서

### Phase 1: p95 임계점 찾기
```bash
locust -f load_test/scenario/first_learning/stress_test/p95_threshold.py \
  --host=http://3.39.31.181:8080
```
→ 성능 저하가 시작되는 지점 파악

### Phase 2: 시스템 한계 테스트
```bash
locust -f load_test/scenario/first_learning/stress_test/system_limit.py \
  --host=http://3.39.31.181:8080
```
→ 시스템이 완전히 장애를 일으키는 지점 파악

---

## 결과 기록 템플릿

### p95 임계점 테스트 결과
```
테스트 일시: YYYY-MM-DD HH:MM

p95 = 400ms 도달 시점:
- 동시 사용자 수:
- 평균 응답 시간:
- RPS (Requests/sec):
- 성공률:
- 5xx 에러율:

시스템 상태:
- CPU 사용률:
- 메모리 사용률:
- JVM Heap 사용률:
```

### 시스템 한계 테스트 결과
```
테스트 일시: YYYY-MM-DD HH:MM

장애 발생 시점:
- 동시 사용자 수:
- 5xx 에러율:
- CPU 사용률:
- 메모리 사용률:
- JVM Heap 사용률:

장애 징후:
- 첫 5xx 에러 발생 시점:
- 5xx 에러율 50% 초과 시점:
- 서버 응답 멈춤 시점:

복구 시간:
- Stop 버튼 클릭 시각:
- 서버 정상화 시각:
- 총 복구 소요 시간:

발생한 에러:
- OutOfMemoryError 발생 여부:
- Connection refused 발생 여부:
- 기타 에러:
```

---

## 모니터링 체크리스트

### 테스트 실행 중 확인 사항

**Locust Web UI:**
- [ ] Statistics 탭 - 실시간 응답 시간 및 성공률
- [ ] Charts 탭 - p95 응답 시간 추이
- [ ] Failures 탭 - 에러 발생 패턴

**서버 모니터링:**
- [ ] CPU 사용률
- [ ] 메모리 사용률
- [ ] JVM Heap 사용률
- [ ] DB 커넥션 풀 상태
- [ ] Nginx access log (5xx 에러)
- [ ] Application log (에러 스택)

---

## 참고사항

- p95 임계점 테스트는 **운영 환경에서도 실행 가능** (점진적 증가로 안전)
- 시스템 한계 테스트는 **절대 운영 환경에서 실행 금지** (서버 다운 가능)
- 두 테스트 모두 Web UI 모드로 실행하여 실시간 모니터링 필수
