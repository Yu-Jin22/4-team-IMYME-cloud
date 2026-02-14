terraform {
  backend "s3" {
    bucket = "mine-tfstate-apne2"   # 버킷 이름
    key    = "dev/terraform.tfstate"             # 버킷 안에서 state가 저장될 경로(파일 키)
    region = "ap-northeast-2"
    encrypt = true
  }
}