# Power control plane: DynamoDB state, ALB→Lambda login/wake, CodeBuild orchestrator,
# EventBridge idle checker. Wake/sleep uses boto3 (ECS/RDS/VPC endpoints) — not
# terraform apply inside CodeBuild — to avoid remote-state locks. Sleep/pause may
# delete VPC endpoints via CLI; next deploy-dev terraform apply reconciles
# enable_vpc_endpoints.

locals {
  power_enabled = var.enable_power_control

  power_lambda_env = {
    POWER_STATE_TABLE      = local.power_enabled ? aws_dynamodb_table.power_state[0].name : ""
    SES_FROM_EMAIL         = var.ses_from_email
    POWER_HANDOFF_SECRET   = local.power_enabled ? random_password.power_handoff[0].result : ""
    CODEBUILD_PROJECT_NAME = local.power_enabled ? aws_codebuild_project.power_orchestrator[0].name : ""
    # Do not set AWS_REGION — reserved by the Lambda runtime.
    NAME_PREFIX = local.name
  }

  power_buildspec = <<-EOF
    version: 0.2
    phases:
      build:
        commands:
          - echo "MODE=$POWER_MODE"
          - aws s3 cp "s3://$ORCHESTRATOR_BUCKET/power_orchestrator.py" ./power_orchestrator.py
          - pip install boto3 -q
          - python power_orchestrator.py "$POWER_MODE"
  EOF

  power_admin_email = "ollioxenhomefree@gmail.com"
  power_admin_id    = "00000000-0000-4000-a000-000000000001"
}

# ---------------------------------------------------------------------------
# DynamoDB
# ---------------------------------------------------------------------------

resource "aws_dynamodb_table" "power_state" {
  count = local.power_enabled ? 1 : 0

  name         = "${local.name}-power-state"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "pk"

  attribute {
    name = "pk"
    type = "S"
  }

  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  tags = {
    Name = "${local.name}-power-state"
  }
}

resource "aws_dynamodb_table_item" "power_admin_user" {
  count = local.power_enabled ? 1 : 0

  table_name = aws_dynamodb_table.power_state[0].name
  hash_key   = aws_dynamodb_table.power_state[0].hash_key

  item = jsonencode({
    pk           = { S = "USER#${local.power_admin_email}" }
    email        = { S = local.power_admin_email }
    user_id      = { S = local.power_admin_id }
    display_name = { S = "Admin" }
    is_admin     = { BOOL = true }
    is_active    = { BOOL = true }
  })
}

resource "aws_dynamodb_table_item" "power_state_seed" {
  count = local.power_enabled ? 1 : 0

  table_name = aws_dynamodb_table.power_state[0].name
  hash_key   = aws_dynamodb_table.power_state[0].hash_key

  item = jsonencode({
    pk                    = { S = "POWER#STATE" }
    state                 = { S = "awake" }
    last_activity_at      = { NULL = true }
    idle_timer_started_at = { NULL = true }
    active_jobs           = { N = "0" }
  })

  lifecycle {
    ignore_changes = [item]
  }
}

# ---------------------------------------------------------------------------
# Secrets
# ---------------------------------------------------------------------------

resource "random_password" "power_handoff" {
  count = local.power_enabled ? 1 : 0

  length  = 48
  special = false
}

resource "aws_secretsmanager_secret" "power_handoff" {
  count = local.power_enabled ? 1 : 0

  name = "${local.name}/power-handoff"
}

resource "aws_secretsmanager_secret_version" "power_handoff" {
  count = local.power_enabled ? 1 : 0

  secret_id = aws_secretsmanager_secret.power_handoff[0].id
  secret_string = jsonencode({
    power_handoff_secret = random_password.power_handoff[0].result
  })
}

# ---------------------------------------------------------------------------
# Orchestrator artifact bucket + CodeBuild
# ---------------------------------------------------------------------------

resource "aws_s3_bucket" "power_orchestrator" {
  count = local.power_enabled ? 1 : 0

  bucket = "${local.name}-power-orchestrator-${local.account_id}"
}

resource "aws_s3_bucket_public_access_block" "power_orchestrator" {
  count = local.power_enabled ? 1 : 0

  bucket = aws_s3_bucket.power_orchestrator[0].id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "power_orchestrator" {
  count = local.power_enabled ? 1 : 0

  bucket = aws_s3_bucket.power_orchestrator[0].id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_object" "power_orchestrator_script" {
  count = local.power_enabled ? 1 : 0

  bucket = aws_s3_bucket.power_orchestrator[0].id
  key    = "power_orchestrator.py"
  source = "${path.module}/../../scripts/power_orchestrator.py"
  etag   = filemd5("${path.module}/../../scripts/power_orchestrator.py")
}

resource "aws_iam_role" "power_codebuild" {
  count = local.power_enabled ? 1 : 0

  name = "${local.name}-power-codebuild"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "codebuild.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })
}

data "aws_iam_policy_document" "power_codebuild" {
  count = local.power_enabled ? 1 : 0

  statement {
    sid    = "Logs"
    effect = "Allow"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]
    resources = [
      "arn:aws:logs:${var.aws_region}:${local.account_id}:log-group:/aws/codebuild/${local.name}-power-orchestrator",
      "arn:aws:logs:${var.aws_region}:${local.account_id}:log-group:/aws/codebuild/${local.name}-power-orchestrator:*",
    ]
  }

  statement {
    sid    = "OrchestratorBucket"
    effect = "Allow"
    actions = [
      "s3:GetObject",
      "s3:ListBucket",
    ]
    resources = [
      aws_s3_bucket.power_orchestrator[0].arn,
      "${aws_s3_bucket.power_orchestrator[0].arn}/*",
    ]
  }

  statement {
    sid    = "EcsScale"
    effect = "Allow"
    actions = [
      "ecs:UpdateService",
      "ecs:DescribeServices",
      "ecs:DescribeClusters",
      "ecs:ListServices",
    ]
    resources = ["*"]
  }

  statement {
    sid    = "RdsStartStop"
    effect = "Allow"
    actions = [
      "rds:StartDBInstance",
      "rds:StopDBInstance",
      "rds:DescribeDBInstances",
    ]
    resources = [aws_db_instance.main.arn]
  }

  statement {
    sid    = "VpcEndpoints"
    effect = "Allow"
    actions = [
      "ec2:DescribeVpcs",
      "ec2:DescribeSubnets",
      "ec2:DescribeRouteTables",
      "ec2:DescribeSecurityGroups",
      "ec2:DescribeVpcEndpoints",
      "ec2:CreateVpcEndpoint",
      "ec2:DeleteVpcEndpoints",
      "ec2:CreateTags",
    ]
    resources = ["*"]
  }

  statement {
    sid    = "DynamoPowerState"
    effect = "Allow"
    actions = [
      "dynamodb:GetItem",
      "dynamodb:PutItem",
      "dynamodb:UpdateItem",
    ]
    resources = [aws_dynamodb_table.power_state[0].arn]
  }
}

resource "aws_iam_role_policy" "power_codebuild" {
  count = local.power_enabled ? 1 : 0

  name   = "${local.name}-power-codebuild"
  role   = aws_iam_role.power_codebuild[0].id
  policy = data.aws_iam_policy_document.power_codebuild[0].json
}

resource "aws_codebuild_project" "power_orchestrator" {
  count = local.power_enabled ? 1 : 0

  name          = "${local.name}-power-orchestrator"
  description   = "Wake/sleep RRE dev (ECS, RDS, VPC endpoints) via boto3"
  service_role  = aws_iam_role.power_codebuild[0].arn
  build_timeout = 60

  artifacts {
    type = "NO_ARTIFACTS"
  }

  environment {
    compute_type                = "BUILD_GENERAL1_SMALL"
    image                       = "aws/codebuild/standard:7.0"
    type                        = "LINUX_CONTAINER"
    image_pull_credentials_type = "CODEBUILD"
    privileged_mode             = false

    environment_variable {
      name  = "POWER_MODE"
      value = "wake"
    }
    environment_variable {
      name  = "ORCHESTRATOR_BUCKET"
      value = aws_s3_bucket.power_orchestrator[0].bucket
    }
    environment_variable {
      name  = "POWER_STATE_TABLE"
      value = aws_dynamodb_table.power_state[0].name
    }
    environment_variable {
      name  = "NAME_PREFIX"
      value = local.name
    }
    environment_variable {
      name  = "AWS_DEFAULT_REGION"
      value = var.aws_region
    }
  }

  source {
    type      = "NO_SOURCE"
    buildspec = local.power_buildspec
  }

  logs_config {
    cloudwatch_logs {
      group_name = "/aws/codebuild/${local.name}-power-orchestrator"
      status     = "ENABLED"
    }
  }

  tags = {
    Name = "${local.name}-power-orchestrator"
  }
}

# ---------------------------------------------------------------------------
# Lambda (ALB auth/wake + idle checker)
# ---------------------------------------------------------------------------

data "archive_file" "power_control" {
  count = local.power_enabled ? 1 : 0

  type        = "zip"
  source_dir  = "${path.module}/../lambda/power_control"
  output_path = "${path.module}/.terraform/power_control.zip"
}

resource "aws_cloudwatch_log_group" "power_lambda" {
  count = local.power_enabled ? 1 : 0

  name              = "/aws/lambda/${local.name}-power-control"
  retention_in_days = var.log_retention_days
}

resource "aws_cloudwatch_log_group" "power_idle_lambda" {
  count = local.power_enabled ? 1 : 0

  name              = "/aws/lambda/${local.name}-power-idle"
  retention_in_days = var.log_retention_days
}

resource "aws_iam_role" "power_lambda" {
  count = local.power_enabled ? 1 : 0

  name = "${local.name}-power-lambda"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })
}

data "aws_iam_policy_document" "power_lambda" {
  count = local.power_enabled ? 1 : 0

  statement {
    sid    = "Logs"
    effect = "Allow"
    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]
    resources = [
      "${aws_cloudwatch_log_group.power_lambda[0].arn}:*",
      "${aws_cloudwatch_log_group.power_idle_lambda[0].arn}:*",
    ]
  }

  statement {
    sid    = "DynamoPowerState"
    effect = "Allow"
    actions = [
      "dynamodb:GetItem",
      "dynamodb:PutItem",
      "dynamodb:UpdateItem",
      "dynamodb:DeleteItem",
      "dynamodb:Query",
    ]
    resources = [aws_dynamodb_table.power_state[0].arn]
  }

  statement {
    sid    = "SesSend"
    effect = "Allow"
    actions = [
      "ses:SendEmail",
      "ses:SendRawEmail",
    ]
    resources = ["*"]
  }

  statement {
    sid    = "CodeBuildStart"
    effect = "Allow"
    actions = [
      "codebuild:StartBuild",
      "codebuild:BatchGetBuilds",
    ]
    resources = [aws_codebuild_project.power_orchestrator[0].arn]
  }
}

resource "aws_iam_role_policy" "power_lambda" {
  count = local.power_enabled ? 1 : 0

  name   = "${local.name}-power-lambda"
  role   = aws_iam_role.power_lambda[0].id
  policy = data.aws_iam_policy_document.power_lambda[0].json
}

resource "aws_lambda_function" "power_control" {
  count = local.power_enabled ? 1 : 0

  function_name = "${local.name}-power-control"
  role          = aws_iam_role.power_lambda[0].arn
  handler       = "handler.handler"
  runtime       = "python3.12"
  timeout       = 30
  memory_size   = 256

  filename         = data.archive_file.power_control[0].output_path
  source_code_hash = data.archive_file.power_control[0].output_base64sha256

  environment {
    variables = merge(local.power_lambda_env, {
      API_BASE_URL = "${local.alb_scheme}://${aws_lb.main.dns_name}"
    })
  }

  depends_on = [
    aws_cloudwatch_log_group.power_lambda,
    aws_iam_role_policy.power_lambda,
  ]

  tags = {
    Name = "${local.name}-power-control"
  }
}

resource "aws_lambda_function" "power_idle" {
  count = local.power_enabled ? 1 : 0

  function_name = "${local.name}-power-idle"
  role          = aws_iam_role.power_lambda[0].arn
  handler       = "idle_handler.handler"
  runtime       = "python3.12"
  timeout       = 60
  memory_size   = 256

  filename         = data.archive_file.power_control[0].output_path
  source_code_hash = data.archive_file.power_control[0].output_base64sha256

  environment {
    variables = merge(local.power_lambda_env, {
      API_BASE_URL = "${local.alb_scheme}://${aws_lb.main.dns_name}"
      API_KEY      = random_password.api_key.result
    })
  }

  depends_on = [
    aws_cloudwatch_log_group.power_idle_lambda,
    aws_iam_role_policy.power_lambda,
  ]

  tags = {
    Name = "${local.name}-power-idle"
  }
}

resource "aws_lambda_permission" "power_alb" {
  count = local.power_enabled ? 1 : 0

  statement_id  = "AllowExecutionFromALB"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.power_control[0].function_name
  principal     = "elasticloadbalancing.amazonaws.com"
  source_arn    = aws_lb_target_group.power[0].arn
}

resource "aws_lb_target_group" "power" {
  count = local.power_enabled ? 1 : 0

  name        = "${local.name}-power"
  target_type = "lambda"

  tags = {
    Name = "${local.name}-power"
  }
}

resource "aws_lb_target_group_attachment" "power" {
  count = local.power_enabled ? 1 : 0

  target_group_arn = aws_lb_target_group.power[0].arn
  target_id        = aws_lambda_function.power_control[0].arn
  depends_on       = [aws_lambda_permission.power_alb]
}

resource "aws_lb_listener_rule" "power_api" {
  count = local.power_enabled ? 1 : 0

  listener_arn = local.app_listener_arn
  priority     = 5

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.power[0].arn
  }

  condition {
    path_pattern {
      # Lambda owns login/wake auth + public status. Leave handoff/heartbeat/
      # idle-status on priority-10 /api/* → ECS when the stack is awake.
      values = [
        "/api/v1/ops/power/status",
        "/api/v1/ops/power/auth",
        "/api/v1/ops/power/auth/*",
        "/api/v1/ops/power/wake",
      ]
    }
  }
}

resource "aws_lb_listener_rule" "power_login" {
  count = local.power_enabled ? 1 : 0

  listener_arn = local.app_listener_arn
  priority     = 6

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.power[0].arn
  }

  condition {
    path_pattern {
      values = ["/login", "/login/*"]
    }
  }
}

# ---------------------------------------------------------------------------
# Idle schedule (EventBridge → idle Lambda)
# ---------------------------------------------------------------------------

resource "aws_cloudwatch_event_rule" "power_idle" {
  count = local.power_enabled ? 1 : 0

  name                = "${local.name}-power-idle"
  description         = "Check idle sleep threshold for RRE dev"
  schedule_expression = "rate(5 minutes)"
}

resource "aws_cloudwatch_event_target" "power_idle" {
  count = local.power_enabled ? 1 : 0

  rule      = aws_cloudwatch_event_rule.power_idle[0].name
  target_id = "power-idle-lambda"
  arn       = aws_lambda_function.power_idle[0].arn
}

resource "aws_lambda_permission" "power_idle_events" {
  count = local.power_enabled ? 1 : 0

  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.power_idle[0].function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.power_idle[0].arn
}
