# k8s — ArgoCD + Helm (production manifests)

이 디렉토리는 ArgoCD 기반 GitOps 방식으로 운영되는 Kubernetes 배포 리포지토리입니다.

Helm Chart를 통해 애플리케이션을 정의하고,
Git 변경 사항이 ArgoCD를 통해 클러스터 상태로 자동 반영됩니다.

> Git = Single Source of Truth<br>
> → 클러스터 상태는 항상 Git과 동기화됩니다.

## 🏗️ Architecture (GitOps Flow)

<img width="749" height="286" alt="image" src="https://github.com/user-attachments/assets/a2c94bd9-4fc0-46f3-8f3e-b86316cb05d5" />

<img width="731" height="772" alt="image" src="https://github.com/user-attachments/assets/074a1004-b7b7-405e-ad0d-70ad13cd81b0" />

## 📁 Directory Structure

```
k8s/
├── README.md
├── argocd/
│   └── mine-prod.yaml               # ArgoCD Application 정의
└── prod/
    └── mine/
        ├── Chart.yaml               # Helm 차트 메타데이터
        ├── values.yaml              # 프로덕션 값
        └── templates/
            ├── ssm-secretstore.yaml # ExternalSecret / SSM 연동 설정
            ├── ingress/middleware.yaml
            ├── ai/                   # ai 서비스: deployment/service/externalsecret
            ├── backend/              # backend 서비스: deployment/service/externalsecret
            ├── frontend/             # frontend 서비스: deployment/service/externalsecret
            └── cronjob/              # ecr-secret-refresh cronjob 관련 템플릿
```

## 📌 Prerequisites

다음 도구와 권한이 필요합니다.(macOS 기준 명령 포함)

1. CLI 도구(kubectl, Helm, ArgoCD)

   ```bash
   brew install kubectl helm argocd
   kubectl version --client
   helm version
   argocd version --client
   ```

2. Kubernetes 접근 권한
   - 올바른 kubeconfig context 설정이 필요합니다.

3. Git Repository 접근 권한
   - ArgoCD가 해당 repo를 읽을 수 있어야 합니다.

4. AWS 권한 (필수)
   - SSM Parameter Store 접근 권한, ECR 이미지 Pull 권한이 필요합니다.

## 🚀 Deployment Flow

1. 로컬 검증

   ```bash
   # Helm 차트 문법/템플릿 확인
   helm lint prod/mine
   helm template prod/mine --values prod/mine/values.yaml | head -n 200
   ```

2. 자동 배포 (GitOps)

- values.yaml (image tag 등) 변경 후 Git Push
- ArgoCD가 변경 감지 → 자동 Sync → 배포

3. ArgoCD 수동 제어

   ```bash
   argocd login <ARGOCD_SERVER> --username <user> --password <pw>

   # 상태 확인
   argocd app get mine-prod

   # 강제 동기화
   argocd app sync mine-prod

   # 롤백
   argocd app rollback mine-prod <revision>
   ```

## 🔍 Troubleshooting Guide

1. 리소스 상태 확인
   ```
   kubectl -n <ns> get pods,svc,deploy -o wide
   ```
2. 로그 확인
   ```
   kubectl -n <ns> logs deploy/<deployment-name>
   ```
3. Secret/SSM 연동 문제
   ```
   kubectl -n <ns> get externalsecret,secret
   kubectl -n <ns> describe externalsecret/<name>
   ```
4. ArgoCD Sync 상태 확인
   ```
   argocd app get mine-prod
   ```

## ⚠️ Notes

- **kubectl로 직접 수정 금지** → Git 상태와 Drift 발생

- **values.yaml 변경 시 반드시 리뷰** → 잘못된 tag 배포 방지

- **Secret은 절대 Git에 저장하지 않음** → 반드시 SSM 통해 관리

## 📄 Related Documents

- [Kubernetes 클러스터 설계 (kubeadm 기반)](<https://github.com/100-hours-a-week/4-team-IMYME-wiki/wiki/%5BCloud%5D-%EC%84%A4%EA%B3%84-5%EB%8B%A8%EA%B3%84-:-Kubernetes-%ED%81%B4%EB%9F%AC%EC%8A%A4%ED%84%B0-%EC%84%A4%EA%B3%84-(kubeadm-%EA%B8%B0%EB%B0%98)>)
