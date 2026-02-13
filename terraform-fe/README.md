# Terraform Frontend Parameter Store 관리

이 Terraform 프로젝트는 프론트엔드용 AWS Systems Manager Parameter Store를 관리합니다.

## 구조

```
terraform-fe/
├── provider.tf              # AWS 프로바이더 설정
├── variables.tf             # 입력 변수 정의
├── parameter_store.tf       # Parameter Store 리소스
├── outputs.tf               # 출력 값
├── terraform.tfvars         # 변수 파일 (git에 커밋하지 않음)
└── .gitignore              # Git 제외 파일
```

## 사용 방법

### 1. 초기 설정

```bash
cd terraform-fe
terraform init
```

### 2. 실행 계획 확인

```bash
terraform plan
```

### 3. 적용

```bash
terraform apply
```

## Parameter Store 구조

생성되는 파라미터는 다음과 같은 네이밍 컨벤션을 따릅니다:

```
/MINE/MVP1/FE/ENV/COMMON/     # 공통 환경변수
/MINE/MVP1/FE/ENV/RELEASE/    # RELEASE 환경별 환경변수
```

예시:
- `/MINE/MVP1/FE/ENV/COMMON/NODE_ENV`
- `/MINE/MVP1/FE/ENV/COMMON/NEXT_PUBLIC_KAKAO_REST_API_KEY`
- `/MINE/MVP1/FE/ENV/RELEASE/NEXT_PUBLIC_KAKAO_REDIRECT_URI`

## Parameter 타입

- **String**: 일반 문자열 값 (Next.js의 NEXT_PUBLIC_ 변수 포함)
- **SecureString**: KMS로 암호화된 민감한 정보

## 보안 주의사항

1. `terraform.tfvars` 파일은 절대 Git에 커밋하지 마세요
2. 민감한 정보는 반드시 `SecureString` 타입을 사용하세요
3. Terraform state 파일도 민감한 정보를 포함하므로 원격 백엔드(S3 + DynamoDB)를 사용하는 것을 권장합니다

## 리소스 정리

```bash
terraform destroy
```
