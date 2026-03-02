# Release 서버 K6 부하 테스트

```bash
cd /Users/wonhyeonseob/Desktop/git/MINE/cloud/4-team-IMYME-cloud/load_test/k6/release
```

## 테스트 흐름

각 VU(가상 사용자)가 반복 실행:

```
1. POST /e2e/login     → JWT 토큰 발급 (기본: VU당 1회, 옵션: 매 반복)
2. GET /categories     → 카테고리 조회 (Public)
3. GET /keywords       → 키워드 조회 (Public)
4. GET /users/me       → 프로필 조회 (인증)
5. GET /cards          → 카드 목록 (인증)
```

## 명령어

### smoke-test.js
배포 직후 API 정상 응답 검증 (1 VU, 30초)
```bash
k6 run --vus {VU수} --duration {시간} smoke-test.js
```

### load-test.js
평소 사용자 수준 부하 테스트 (10→50 VUs, 5분)
```bash
k6 run --vus {VU수} --duration {시간} load-test.js
```

### stress-test.js
점진적 부하 증가로 병목 구간 파악 (50→200 VUs, 12분)
```bash
k6 run --vus {VU수} --duration {시간} stress-test.js
```

### spike-test.js
이벤트/푸시 등 순간 폭주 시나리오 (10→100→150 VUs, 4분)
```bash
k6 run --vus {VU수} --duration {시간} spike-test.js
```

### soak-test.js
메모리 누수, 연결 고갈 등 장기 문제 확인 (30 VUs, 34분)
```bash
k6 run --vus {VU수} --duration {시간} soak-test.js

1. k6 run --vus 30  --duration 10m soak-test.js

```

### scenario-learning.js
카드 조회→학습 시도 생성 전체 플로우 (10→30 VUs, 5분)
```bash
k6 run --vus {VU수} --duration {시간} scenario-learning.js
```

## 예시

```bash
k6 run --vus 50 --duration 5m load-test.js
k6 run --vus 30 --duration 15m soak-test.js
```

## 다른 서버 대상

```bash
k6 run --vus {VU수} --duration {시간} -e BASE_URL=https://다른서버.com/server load-test.js
```

## 설정

- BASE_URL: `https://release.imymemine.kr/server`
- 인증: E2E 로그인 API (`/e2e/login`)
- LOGIN_EVERY_ITER: 기본 `false` (VU당 로그인 1회 캐시), `true`면 반복마다 로그인
- USER_ID_BASE: 기본 `1000000` (로그인용 userId 시작값)
- userId 생성 규칙: `USER_ID_BASE + ((__VU - 1) * 1000000) + __ITER`
- deviceUuid: 로그인마다 랜덤 UUID 생성
- prod 환경 실행 불가 (E2E API 비활성화)

## 현재 인프라 (release)

| 항목 | 값 |
|------|-----|
| 인스턴스 | t4g.small x 2개 |
| ASG | min 1 / max 3 / desired 2 |
| FIS 테스트 권장 | 30~50 VUs, 10~15분 |
