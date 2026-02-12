# Terraform Parameter Store 관리

이 Terraform 프로젝트는 AWS Systems Manager Parameter Store를 관리합니다.

## 구조

```
terraform/
├── provider.tf              # AWS 프로바이더 설정
├── variables.tf             # 입력 변수 정의
├── parameter_store.tf       # Parameter Store 리소스
├── outputs.tf               # 출력 값
├── terraform.tfvars.example # 예제 변수 파일
└── .gitignore              # Git 제외 파일
```

## 사용 방법

### 1. 초기 설정

```bash
# Terraform 초기화
terraform init
```

### 2. 변수 파일 생성

예제 파일을 복사하여 실제 값을 입력합니다:

```bash
cp terraform.tfvars.example terraform.tfvars
```

`terraform.tfvars` 파일을 편집하여 실제 값을 입력합니다.

### 3. 실행 계획 확인

```bash
terraform plan
```

### 4. 적용

```bash
terraform apply
```

### 5. 특정 환경 적용

```bash
# 개발 환경
terraform apply -var="environment=dev"

# 프로덕션 환경
terraform apply -var="environment=prod"
```

## Parameter Store 구조

생성되는 파라미터는 다음과 같은 네이밍 컨벤션을 따릅니다:

```
/{environment}/{parameter_key}
```

예시:
- `/dev/database/host`
- `/dev/database/password`
- `/prod/api/secret-key`

## Parameter 타입

- **String**: 일반 문자열 값
- **StringList**: 쉼표로 구분된 문자열 리스트
- **SecureString**: KMS로 암호화된 민감한 정보

## IAM 정책

이 프로젝트는 다음 IAM 정책을 생성합니다:

1. **parameter-store-read-policy**: Parameter Store 읽기 권한
2. **parameter-store-write-policy**: Parameter Store 쓰기 권한

EC2, ECS, Lambda 등의 리소스에 이 정책을 연결하여 Parameter Store 접근 권한을 부여할 수 있습니다.

## 예제: 새 파라미터 추가

`terraform.tfvars`에 다음과 같이 추가:

```hcl
parameters = {
  "myapp/config" = {
    value       = "my-config-value"
    type        = "String"
    description = "My application configuration"
    tier        = "Standard"
  }
}
```

## 보안 주의사항

1. `terraform.tfvars` 파일은 절대 Git에 커밋하지 마세요
2. 민감한 정보는 반드시 `SecureString` 타입을 사용하세요
3. Terraform state 파일도 민감한 정보를 포함하므로 원격 백엔드(S3 + DynamoDB)를 사용하는 것을 권장합니다

## 원격 State 백엔드 설정 (선택사항)

`provider.tf`의 주석을 해제하고 설정:

```hcl
backend "s3" {
  bucket         = "your-terraform-state-bucket"
  key            = "parameter-store/terraform.tfstate"
  region         = "ap-northeast-2"
  encrypt        = true
  dynamodb_table = "terraform-lock"
}
```

## 리소스 정리

```bash
terraform destroy
```

## 주의사항

- Parameter Store는 Standard tier와 Advanced tier가 있으며, Advanced tier는 추가 비용이 발생합니다
- SecureString 타입 파라미터는 AWS KMS를 사용하여 암호화되며, KMS 키 사용 비용이 발생할 수 있습니다
