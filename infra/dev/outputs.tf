output "aws_region" {
  value = var.aws_region
}

output "account_id" {
  value = local.account_id
}

output "alb_dns_name" {
  description = "Public URL for RRE dev (UI default; API at /api)."
  value       = aws_lb.main.dns_name
}

output "alb_url" {
  value = "${local.alb_scheme}://${aws_lb.main.dns_name}"
}

output "https_enabled" {
  value = local.https_enabled
}

output "api_key_secret_arn" {
  description = "Secrets Manager ARN for UI/API shared API_KEY (smoke may read api_key)."
  value       = aws_secretsmanager_secret.api_key.arn
}

output "ecr_api_repository_url" {
  value = aws_ecr_repository.api.repository_url
}

output "ecr_ui_repository_url" {
  value = aws_ecr_repository.ui.repository_url
}

output "ecs_cluster_name" {
  value = aws_ecs_cluster.main.name
}

output "ecs_api_service_name" {
  value = aws_ecs_service.api.name
}

output "ecs_ui_service_name" {
  value = aws_ecs_service.ui.name
}

output "api_target_group_arn" {
  description = "ALB target group ARN for API smoke (AWS-3f)."
  value       = aws_lb_target_group.api.arn
}

output "ui_target_group_arn" {
  description = "ALB target group ARN for UI smoke (AWS-3f)."
  value       = aws_lb_target_group.ui.arn
}

output "api_log_group" {
  value = aws_cloudwatch_log_group.api.name
}

output "ui_log_group" {
  value = aws_cloudwatch_log_group.ui.name
}

output "rds_endpoint" {
  value = aws_db_instance.main.address
}

output "uploads_bucket" {
  value = aws_s3_bucket.uploads.bucket
}

output "no_egress_networking_enabled" {
  description = "ECS tasks run without public IPs; AWS APIs via VPC endpoints."
  value       = var.enable_no_egress_networking
}

output "vpc_endpoints_enabled" {
  description = "VPC endpoints are provisioned for AWS APIs."
  value       = var.enable_vpc_endpoints
}

output "ui_api_base_url" {
  description = "Server-side API URL used by the Streamlit container."
  value       = local.ui_api_base_url
}
