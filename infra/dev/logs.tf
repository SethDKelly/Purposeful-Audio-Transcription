resource "aws_cloudwatch_log_group" "api" {
  name              = local.api_log_group
  retention_in_days = var.log_retention_days
}

resource "aws_cloudwatch_log_group" "ui" {
  name              = local.ui_log_group
  retention_in_days = var.log_retention_days
}

resource "aws_cloudwatch_log_group" "web" {
  name              = local.web_log_group
  retention_in_days = var.log_retention_days
}

resource "aws_cloudwatch_log_group" "worker" {
  name              = local.worker_log_group
  retention_in_days = var.log_retention_days
}
