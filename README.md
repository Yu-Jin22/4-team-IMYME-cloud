# ☁️ Mine Cloud Infrastructure

<img width="1238" height="701" alt="Image" src="https://github.com/user-attachments/assets/3ed55f22-60fc-4c21-9235-b0b69b6bce11" />

이 레포지토리는 **MINE 서비스의 클라우드 인프라를 코드로 설계하고 구성한 내용을 정리한 저장소**입니다.

단일 서버 구조에서 시작하여, Docker 기반 확장 아키텍처를 거쳐, 현재는 Kubernetes 기반으로 고도화된 인프라를 운영하고 있습니다.

## 📄 Documentation

- [Cloud Wiki 바로가기](https://github.com/100-hours-a-week/4-team-IMYME-wiki/wiki/Cloud-WIKI)
- [Team Wiki 바로가기](https://github.com/100-hours-a-week/4-team-IMYME-wiki/wiki)

## 🏗️ Architecture Evolution

### 최종 아키텍처

<img width="731" height="772" alt="image" src="https://github.com/user-attachments/assets/074a1004-b7b7-405e-ad0d-70ad13cd81b0" />

### V1 — 단일 서버 구조

- 단일 EC2 인스턴스 기반 배포
- 구조 단순하지만, 장애 시 서비스 전체 영향
- 확장성 및 가용성 한계 존재

### V2 — Docker 기반 확장 아키텍처

- ALB + ASG + Docker 기반 3-Tier 구조
- 트래픽 증가 시 EC2 단위 오토스케일링
- 중앙 모니터링 (Prometheus, Grafana, Loki) 구축
- 인스턴스 단위 확장 한계
- 서비스별 세밀한 확장 어려움

### V3 — Kubernetes 기반 운영

- kubeadm 기반 클러스터 직접 구성
- Pod 단위 확장 (HPA)으로 유연한 스케일링
- ArgoCD 기반 GitOps 배포 도입

## 📁 Repository Structure

> 각 디렉토리에서 상세 README를 확인할 수 있습니다.

```
.
├── terraform/         # AWS 인프라 IaC (VPC, EC2, ALB 등)
├── k8s/               # Kubernetes manifests & Helm (ArgoCD 관리)
├── load_test/         # Locust 기반 부하 테스트 코드
├── Locust_Result/     # 부하 테스트 결과
├── .github/
└── README.md

```
