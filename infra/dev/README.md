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

- Uses default VPC and public Fargate tasks for dev simplicity.
- RDS PostgreSQL is private; credentials in Secrets Manager (`rre-dev/database`).
- Diarization disabled in AWS image; Bedrock/Transcribe come in later phases.
- VPC endpoints and no-egress networking are planned in [aws-deployment.md](../../doc/planning/aws-deployment.md).
