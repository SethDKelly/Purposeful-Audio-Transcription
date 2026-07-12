# RRE AWS dev infrastructure

Terraform for the **dev** environment in account `521018312783` (`us-east-2`).

| Resource | Name pattern |
|----------|----------------|
| State key | `purposeful-audio-transcription/dev/terraform.tfstate` |
| IAM roles | `rre-dev-ecs-execution`, `rre-dev-ecs-task` |
| ECS cluster | `rre-dev-cluster` |
| ECR | `rre-dev-api`, `rre-dev-ui` |
| ALB | `rre-dev-alb` |

## Prerequisites

- aws-backbone merged with RRE OIDC trust and `rre-dev-*` IAM prefix
- AWS credentials (`dev-developer` locally, or `dev-github-deploy` in CI)
- Terraform >= 1.5

## Deploy via GitHub Actions (recommended)

Push to **`phase-m0-docs`** — workflow `.github/workflows/deploy-dev.yml` runs tests, builds images, applies Terraform, and rolls ECS.

## Manual deploy

```powershell
cd infra/dev
copy terraform.tfvars.example terraform.tfvars

# Bootstrap ECR (first run only)
terraform init
terraform apply -target=aws_ecr_repository.api -target=aws_ecr_repository.ui

# Build and push images (from repo root)
$account = "521018312783"
$region = "us-east-2"
$tag = "manual-$(Get-Date -Format 'yyyyMMddHHmm')"

aws ecr get-login-password --region $region | docker login --username AWS --password-stdin "$account.dkr.ecr.$region.amazonaws.com"

docker build -t "rre-dev-api:$tag" -f Dockerfile .
docker tag "rre-dev-api:$tag" "$account.dkr.ecr.$region.amazonaws.com/rre-dev-api:$tag"
docker push "$account.dkr.ecr.$region.amazonaws.com/rre-dev-api:$tag"

docker build -t "rre-dev-ui:$tag" -f Dockerfile.ui .
docker tag "rre-dev-ui:$tag" "$account.dkr.ecr.$region.amazonaws.com/rre-dev-ui:$tag"
docker push "$account.dkr.ecr.$region.amazonaws.com/rre-dev-ui:$tag"

terraform apply -var="image_tag=$tag"
```

## Outputs

```powershell
terraform output alb_url
terraform output api_log_group
```

## URLs

| Service | Path |
|---------|------|
| Streamlit UI | `http://<alb_dns>/` |
| API health | `http://<alb_dns>/api/health` |
| API docs | `http://<alb_dns>/docs` |

## Notes

- **No-egress networking (default):** ECS tasks have no public IP. AWS APIs use VPC interface endpoints (Bedrock, Transcribe, Secrets Manager, CloudWatch Logs, ECR, STS) plus an S3 gateway endpoint. UI calls the API at `http://api.rre-dev.local:8000` via Cloud Map.
- Set `enable_no_egress_networking = false` in `terraform.tfvars` to restore public Fargate tasks (legacy).
- RDS PostgreSQL is private; credentials in Secrets Manager (`rre-dev/database`).
- **Audio diarization in AWS** still needs Hugging Face egress until P1-1 Transcribe (`HF_TOKEN` in Secrets Manager). Paste/upload transcript workflows and Bedrock analysis work without public egress.
- See [aws-deployment.md](../../doc/planning/aws-deployment.md) for the full network model.

## Pause / resume (avoid Fargate + RDS compute charges)

**Pause** — GitHub Actions → **Pause AWS dev** → Run workflow (or push changes to `pause-dev.yml`).

This sets ECS desired count to **0** and stops RDS `rre-dev-postgres`. Terraform state stays in sync.

**Resume** — run **Deploy to AWS dev** (push to `phase-m0-docs` or workflow_dispatch). The deploy workflow starts RDS if it was stopped, waits for it to become available, then scales ECS back to 1.

**Costs while paused:** ALB (~$16/mo), ECR image storage, Secrets Manager, RDS storage (no compute while stopped). RDS auto-restarts after ~7 days if not resumed.

Manual pause (with AWS CLI):

```powershell
aws ecs update-service --cluster rre-dev-cluster --service rre-dev-api --desired-count 0
aws ecs update-service --cluster rre-dev-cluster --service rre-dev-ui --desired-count 0
aws rds stop-db-instance --db-instance-identifier rre-dev-postgres
```
