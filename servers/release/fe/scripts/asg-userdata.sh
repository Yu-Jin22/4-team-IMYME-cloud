#!/bin/bash

# 1. ECR 로그인
aws ecr get-login-password --region ap-northeast-2 | \
    docker login --username AWS --password-stdin 219268921033.dkr.ecr.ap-northeast-2.amazonaws.com

# 2. 기존 .env 초기화 (없으면 생성)
> /home/ubuntu/.env

# 3. SSM에서 .env 생성
echo "# ------------- COMMON (공통) --------------" >> /home/ubuntu/.env

# COMMON 파라미터 가져오기
aws ssm get-parameters-by-path \
    --path "/MINE/MVP1/FE/ENV/COMMON" \
    --with-decryption \
    --query "Parameters[*].[Name,Value]" \
    --output text | while read name value; do
    key=$(basename $name)
    echo "$key=$value" >> /home/ubuntu/.env
done

echo "" >> /home/ubuntu/.env
echo "# ---------- RELEASE (환경별) -------" >> /home/ubuntu/.env

# RELEASE 파라미터 가져오기
aws ssm get-parameters-by-path \
    --path "/MINE/MVP1/FE/ENV/RELEASE" \
    --with-decryption \
    --query "Parameters[*].[Name,Value]" \
    --output text | while read name value; do
    key=$(basename $name)
    echo "$key=$value" >> /home/ubuntu/.env
done

# 4. 도커 컴포즈 실행
cd /home/ubuntu
docker compose pull
docker compose up -d
