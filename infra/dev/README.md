# RRE AWS dev infrastructure

Terraform for the **dev** environment in account `521018312783` (`us-east-2`).

| Resource | Name pattern |
|----------|----------------|
| State key | `purposeful-audio-transcription/dev/terraform.tfstate` |
| IAM roles | `rre-dev-ecs-execution`, `rre-dev-ecs-execution-ui`, `rre-dev-ecs-task-{ui,api,worker}` |
| ECS cluster | `rre-dev-cluster` |
| ECS services | `rre-dev-api`, `rre-dev-ui`, `rre-dev-worker` |
| ECR | `rre-dev-api`, `rre-dev-ui` (worker reuses API image) |
| ALB | `rre-dev-alb` |

## Prerequisites

- aws-backbone merged with RRE OIDC trust and `rre-dev-*` IAM prefix
- AWS credentials (`dev-developer` locally, or `dev-github-deploy` in CI)
- Terraform >= 1.5

## Deploy via GitHub Actions

**Push of a `v*.*.*` tag** or manual **Deploy to AWS dev** wakes ECS/RDS. Ordinary commits to `main` do not auto-deploy.

Manual: Actions → **Deploy to AWS dev** → Run workflow (optional `component`: `all` / `api` / `ui` / `worker`).

Builds selected image(s), applies Terraform, updates matching ECS services, smokes AWS-3f scoped by component.

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

- **VPC endpoints (default on):** S3 gateway (all VPC route tables) + interface endpoints for Bedrock, Transcribe, Secrets Manager, CloudWatch Logs, ECR, STS, monitoring.
- **No-egress mode (default on — Stage B):** Tasks have no public IP; SGs allow HTTPS to VPC endpoints + S3 prefix list, DNS/Postgres in-VPC, and UI→API via Cloud Map (`http://api.rre-dev.local:8000`). Rollback: set `enable_no_egress_networking = false`.
- RDS PostgreSQL is private; credentials in Secrets Manager (`rre-dev/database`).
- **API auth:** Shared `API_KEY` in Secrets Manager (`rre-dev/api-key`) is injected into API + UI tasks. UI sends `X-API-Key` on backend calls.
- **HTTPS (optional):** Set `acm_certificate_arn` to an ACM cert in this region to enable ALB `:443` and HTTP→HTTPS redirect. Default remains HTTP-only on the ALB DNS name (no cert without a domain you control).
- See [aws-deployment.md](../../docs/developer/aws-deployment.md) for the full network model.

## Pause / resume (avoid Fargate + RDS compute charges)

**Standing practice:** After each minor-version deploy, pause when the stack sits idle (between coding sessions, overnight). Resume only when you need AWS again.

**Pause** — GitHub Actions → **Pause AWS dev** → Run workflow.

This sets ECS desired count to **0** and stops RDS `rre-dev-postgres`. Terraform state stays in sync.

**Resume** — **Deploy to AWS dev** (`workflow_dispatch`) or push a `v*.*.*` tag. The deploy workflow starts RDS if stopped, **clears any lingering ECS tasks**, then scales ECS with the new image.

**Task size (P1-2d):** Slim API defaults — `api_cpu=1024`, `api_memory=2048` (was 1024/4096). Tried 512/2048; ALB `/api/live` timed out during cutover. UI remains `256` / `512`.

**API serving (burn-in resilience):** Cloud image runs **2 uvicorn workers** so `/api/live` stays responsive during Bedrock Converse. ALB unhealthy_threshold is **10** (was 5). Deploy clears tasks to desired 0 before apply (clean slate for single-task Fargate + ALB).

**Costs while paused:** ALB (~$16/mo), ECR image storage, Secrets Manager, RDS storage (no compute while stopped). RDS auto-restarts after ~7 days if not resumed.

Manual pause (with AWS CLI):

```powershell
aws ecs update-service --cluster rre-dev-cluster --service rre-dev-api --desired-count 0
aws ecs update-service --cluster rre-dev-cluster --service rre-dev-ui --desired-count 0
aws rds stop-db-instance --db-instance-identifier rre-dev-postgres
```
