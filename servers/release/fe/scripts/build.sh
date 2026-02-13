#!/bin/bash

# 스크립트 디렉토리 경로
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# .env 파일 경로
ENV_FILE="$PROJECT_ROOT/env/.env"

# .env 파일 로드
if [ -f "$ENV_FILE" ]; then
  echo "📂 Loading environment variables from: $ENV_FILE"
  export $(grep -v '^#' "$ENV_FILE" | grep -v '^$' | xargs)
else
  echo "❌ Error: .env file not found at $ENV_FILE"
  exit 1
fi

echo "🚀 Building Docker image for release environment..."

# 환경변수 확인
echo "Environment variables loaded:"
echo "  NEXT_PUBLIC_API_BASE_URL: $NEXT_PUBLIC_API_BASE_URL"
echo "  NEXT_PUBLIC_SERVER_URL: $NEXT_PUBLIC_SERVER_URL"
echo "  NEXT_PUBLIC_KAKAO_REDIRECT_URI: $NEXT_PUBLIC_KAKAO_REDIRECT_URI"

IMAGE_TAG="imyme-frontend:release"

# Docker 빌드
docker build \
  --build-arg NODE_ENV="$NODE_ENV" \
  --build-arg NEXT_PUBLIC_KAKAO_REST_API_KEY="$NEXT_PUBLIC_KAKAO_REST_API_KEY" \
  --build-arg NEXT_PUBLIC_API_BASE_URL="$NEXT_PUBLIC_API_BASE_URL" \
  --build-arg NEXT_PUBLIC_SERVER_URL="$NEXT_PUBLIC_SERVER_URL" \
  --build-arg NEXT_PUBLIC_GOOGLE_ANALYTICS="$NEXT_PUBLIC_GOOGLE_ANALYTICS" \
  --build-arg NEXT_PUBLIC_PVP_OPEN="$NEXT_PUBLIC_PVP_OPEN" \
  --build-arg NEXT_PUBLIC_KAKAO_REDIRECT_URI="$NEXT_PUBLIC_KAKAO_REDIRECT_URI" \
  --build-arg NEXT_PUBLIC_SECURE="$NEXT_PUBLIC_SECURE" \
  --build-arg E2E_BASE_URL="$E2E_BASE_URL" \
  --build-arg PERF_BASE_URL="$PERF_BASE_URL" \
  --build-arg ALLOW_E2E_LOGIN="$ALLOW_E2E_LOGIN" \
  -f "$PROJECT_ROOT/docker/Dockerfile" \
  -t $IMAGE_TAG \
  .

if [ $? -eq 0 ]; then
  echo "✅ Build successful: $IMAGE_TAG"
  echo ""
  echo "To run the container:"
  echo "  docker run -p 3000:3000 $IMAGE_TAG"
  echo ""
  echo "To push to ECR:"
  echo "  docker tag $IMAGE_TAG 219268921033.dkr.ecr.ap-northeast-2.amazonaws.com/imyme-frontend:latest"
  echo "  docker push 219268921033.dkr.ecr.ap-northeast-2.amazonaws.com/imyme-frontend:latest"
else
  echo "❌ Build failed"
  exit 1
fi
