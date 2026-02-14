# Terraform AWS Infrastructure

Terraform을 사용하여 AWS 인프라(VPC, Subnet, Security Group, EC2)를
코드(IaC)로 관리하는 인프라 레포지토리입니다.

현재는 Big-Bang 배포를 기준으로 한 단순한 인프라 구성을 다루고 있지만,
서비스와 인프라 구조가 변화함에 따라
해당 레포지토리 또한 점진적으로 확장·개선해 나갈 예정입니다.

## 📁 Project Structure

```
terraform/
├── .terraform.lock.hcl     # Provider 버전 고정 파일 (팀 간 동일한 실행 환경 보장)
├── main.tf                 # 주요 인프라 리소스 정의 (VPC, Subnet, SG, EC2)
├── providers.tf            # Terraform 및 AWS Provider 설정
├── variables.tf            # 인프라에서 사용하는 변수 정의
├── outputs.tf              # apply 후 확인할 출력 값 정의 (Public IP, DNS 등)
├── .gitignore              # Git에 포함되지 않아야 할 파일/디렉토리 정의
└── README.md               # 인프라 레포 설명 및 사용 가이드

```

## 📌 Prerequisites

Terraform을 실행하기 위해 아래 도구들이 필요합니다.
MacOS 버전으로 작성되었습니다.

### 1. Terraform 설치

```bash
brew update
brew install terraform

# 설치된 버전 확인
terraform -version
```

### 2. AWS CLI 설치

```bash
brew install awscli
aws --version
```

### 3. AWS 자격증명 설정

- Terraform은 AWS CLI 자격증명을 사용합니다.
  - AWS 계정의 AWS Access Key / Secret Key를 발급받아 아래 명령어로 설정합니다.
  - 실제 Access Key / Secret Key 값은 Git에 커밋하지 않도록 주의해야합니다.

```bash
aws configure
```

## ▶️ How to Run

```
# ====== 사전 작업 ======

# terraform 폴더로 이동
cd terraform

# 코드 포맷만 정리
terraform fmt -recursive

# Terraform 문법 및 구조 검증
terraform init

# Terraform 문법 및 구조 검증
terraform validate

# 변경 사항 미리 확인 (AWS 리소스 생성 X)
terraform plan

# ====== 실행 ======

# AWS 인프라 생성
terraform apply


# ====== 결과물 확인 및 동작 확인 ======

# apply 결과 출력 값 확인
terraform output

# SSH 접속하여 동작 확인
ssh -i <your-key.pem> ubuntu@<public_ip>

# ====== 삭제 ======

# 삭제 계획 확인
terraform plan -destroy

# 생성된 리소스 실제 삭제
terraform destroy

```

## 📦 Terraform State Management (S3 Backend)

Terraform state를 여러 환경에서 일관되게 관리하기 위해,
본 레포지토리는 S3를 원격 backend로 사용합니다.

### 1. S3 버킷을 AWS 콘솔 또는 CLI를 통해 생성

```
aws s3api create-bucket \
  --bucket <BUCKEY_NAME> \
  --region <REGION> \
  --create-bucket-configuration LocationConstraint=<REGION>
```

### 2. backend.tf 생성

`terraform/` 디렉토리 하위에 `backend.tf` 파일을 생성합니다.

```
terraform {
  backend "s3" {
    bucket = "<BUCKET_NAME>"        # 1번에서 생성한 버킷명
    key    = "<TERRAFORM_TFSTATE>"  # state 파일이 저장될 경로
    region = "<REGION>"             # S3 버킷이 위치한 리전
  }
}
```

- S3 region은 Terraform을 실행할 AWS 리전과 동일하게 설정해야합니다.

## ⚠️ Notes

- 본 레포는 실제 AWS 리소스를 생성합니다.
- `terraform apply` 실행 시 과금이 발생할 수 있습니다.
- 실행 전 반드시 사용 중인 AWS 계정과 리전을 확인하세요.
