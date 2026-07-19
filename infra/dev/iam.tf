# Service-specific IAM for ECS (v1.1 Workstream D).
#
# Permission boundaries:
# - UI task role: no Bedrock / Transcribe / S3 (API client only).
# - API task role: health catalog reads + S3/Transcribe for /api/transcribe; no InvokeModel.
# - Worker task role: full analysis (InvokeModel, Transcribe, S3, Marketplace subscribe).
# - Execution roles pull Secrets Manager into env; UI execution cannot read DATABASE_URL.

locals {
  ecs_task_assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "ecs-tasks.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })
}

# ---------------------------------------------------------------------------
# Execution roles (image pull, awslogs, secret injection)
# ---------------------------------------------------------------------------

resource "aws_iam_role" "ecs_execution" {
  name               = "${local.name}-ecs-execution"
  assume_role_policy = local.ecs_task_assume_role_policy
}

resource "aws_iam_role_policy_attachment" "ecs_execution" {
  role       = aws_iam_role.ecs_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role_policy" "ecs_execution_secrets" {
  name = "${local.name}-ecs-execution-secrets"
  role = aws_iam_role.ecs_execution.id

  # API + worker may inject DB and API key.
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "secretsmanager:GetSecretValue",
      ]
      Resource = [
        aws_secretsmanager_secret.database.arn,
        aws_secretsmanager_secret.api_key.arn,
      ]
    }]
  })
}

resource "aws_iam_role" "ecs_execution_ui" {
  name               = "${local.name}-ecs-execution-ui"
  assume_role_policy = local.ecs_task_assume_role_policy
}

resource "aws_iam_role_policy_attachment" "ecs_execution_ui" {
  role       = aws_iam_role.ecs_execution_ui.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role_policy" "ecs_execution_ui_secrets" {
  name = "${local.name}-ecs-execution-ui-secrets"
  role = aws_iam_role.ecs_execution_ui.id

  # UI must not be able to GetSecretValue on DATABASE_URL.
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "secretsmanager:GetSecretValue",
      ]
      Resource = [
        aws_secretsmanager_secret.api_key.arn,
      ]
    }]
  })
}

# ---------------------------------------------------------------------------
# Task roles (runtime AWS API calls from application code)
# ---------------------------------------------------------------------------

resource "aws_iam_role" "ecs_task_ui" {
  name               = "${local.name}-ecs-task-ui"
  assume_role_policy = local.ecs_task_assume_role_policy
}

# No inline app policy: Streamlit talks only to the HTTP API.

resource "aws_iam_role" "ecs_task_api" {
  name               = "${local.name}-ecs-task-api"
  assume_role_policy = local.ecs_task_assume_role_policy
}

data "aws_iam_policy_document" "ecs_task_api" {
  # /api/health probes catalog APIs only (not Converse / InvokeModel).
  statement {
    sid    = "BedrockModelCatalog"
    effect = "Allow"
    actions = [
      "bedrock:GetFoundationModel",
      "bedrock:ListFoundationModels",
      "bedrock:GetInferenceProfile",
      "bedrock:ListInferenceProfiles",
    ]
    resources = ["*"]
  }

  statement {
    sid    = "S3Uploads"
    effect = "Allow"
    actions = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:DeleteObject",
      "s3:ListBucket",
    ]
    resources = [
      aws_s3_bucket.uploads.arn,
      "${aws_s3_bucket.uploads.arn}/*",
    ]
  }

  statement {
    sid    = "TranscribeJobs"
    effect = "Allow"
    actions = [
      "transcribe:StartTranscriptionJob",
      "transcribe:GetTranscriptionJob",
      "transcribe:ListTranscriptionJobs",
    ]
    resources = ["*"]
  }

  statement {
    sid    = "CloudWatchLogs"
    effect = "Allow"
    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]
    resources = ["*"]
  }
}

resource "aws_iam_role_policy" "ecs_task_api" {
  name   = "${local.name}-ecs-task-api"
  role   = aws_iam_role.ecs_task_api.id
  policy = data.aws_iam_policy_document.ecs_task_api.json
}

resource "aws_iam_role" "ecs_task_worker" {
  name               = "${local.name}-ecs-task-worker"
  assume_role_policy = local.ecs_task_assume_role_policy
}

data "aws_iam_policy_document" "ecs_task_worker" {
  statement {
    sid    = "BedrockInvoke"
    effect = "Allow"
    actions = [
      "bedrock:InvokeModel",
      "bedrock:InvokeModelWithResponseStream",
    ]
    resources = [
      "arn:aws:bedrock:*::foundation-model/*",
      "arn:aws:bedrock:${var.aws_region}:${local.account_id}:inference-profile/*",
    ]
  }

  statement {
    sid    = "BedrockModelCatalog"
    effect = "Allow"
    actions = [
      "bedrock:GetFoundationModel",
      "bedrock:ListFoundationModels",
      "bedrock:GetInferenceProfile",
      "bedrock:ListInferenceProfiles",
    ]
    resources = ["*"]
  }

  # First invoke of Marketplace-served 3P models (Anthropic) auto-subscribes
  # via the calling role. Playground subscribe under an admin principal does
  # not always clear this for the ECS task role / inference-profile path.
  statement {
    sid    = "BedrockMarketplaceSubscribe"
    effect = "Allow"
    actions = [
      "aws-marketplace:ViewSubscriptions",
      "aws-marketplace:Subscribe",
      "aws-marketplace:Unsubscribe",
    ]
    resources = ["*"]
    condition {
      test     = "StringEquals"
      variable = "aws:CalledViaLast"
      values   = ["bedrock.amazonaws.com"]
    }
  }

  statement {
    sid    = "S3Uploads"
    effect = "Allow"
    actions = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:DeleteObject",
      "s3:ListBucket",
    ]
    resources = [
      aws_s3_bucket.uploads.arn,
      "${aws_s3_bucket.uploads.arn}/*",
    ]
  }

  statement {
    sid    = "TranscribeJobs"
    effect = "Allow"
    actions = [
      "transcribe:StartTranscriptionJob",
      "transcribe:GetTranscriptionJob",
      "transcribe:ListTranscriptionJobs",
    ]
    resources = ["*"]
  }

  statement {
    sid    = "CloudWatchLogs"
    effect = "Allow"
    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]
    resources = ["*"]
  }
}

resource "aws_iam_role_policy" "ecs_task_worker" {
  name   = "${local.name}-ecs-task-worker"
  role   = aws_iam_role.ecs_task_worker.id
  policy = data.aws_iam_policy_document.ecs_task_worker.json
}
