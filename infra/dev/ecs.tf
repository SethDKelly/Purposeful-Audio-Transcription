resource "aws_ecs_cluster" "main" {
  name = "${local.name}-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

resource "aws_ecs_task_definition" "api" {
  family                   = "${local.name}-api"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = var.api_cpu
  memory                   = var.api_memory
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task_api.arn

  container_definitions = jsonencode([{
    name      = "api"
    image     = local.api_image
    essential = true

    portMappings = [{
      containerPort = 8000
      hostPort      = 8000
      protocol      = "tcp"
    }]

    environment = [
      { name = "LOG_JSON", value = "true" },
      { name = "LOG_LEVEL", value = "INFO" },
      { name = "PYTHONUNBUFFERED", value = "1" },
      { name = "LLM_PROVIDER", value = var.llm_provider },
      { name = "BEDROCK_MODEL_ID", value = var.bedrock_model_id },
      { name = "UPLOADS_BUCKET", value = aws_s3_bucket.uploads.bucket },
      { name = "TRANSCRIPTION_PROVIDER", value = var.transcription_provider },
      { name = "TRANSCRIBE_TIMEOUT_SECONDS", value = "3600" },
      { name = "WORKFLOW_MODULE_CONCURRENCY", value = "3" },
      { name = "BEDROCK_PROMPT_CACHE", value = "true" },
      { name = "BEDROCK_PROMPT_CACHE_TTL", value = "1h" },
      { name = "BEDROCK_MAX_TOKENS", value = "8192" },
      { name = "MODULE_RUN_MAX_RETRIES", value = "1" },
      { name = "WORKFLOW_WORKER_ENABLED", value = "true" },
      { name = "WORKFLOW_JOB_TIMEOUT_SECONDS", value = "7200" },
      { name = "WORKFLOW_JOB_MAX_ATTEMPTS", value = "2" },
      { name = "DIARIZATION_ENABLED", value = var.diarization_enabled ? "true" : "false" },
      { name = "ALEMBIC_AUTO_UPGRADE", value = "true" },
      { name = "TEMP_DIR", value = "/tmp/rre" },
      { name = "AWS_REGION", value = var.aws_region },
      { name = "AWS_DEFAULT_REGION", value = var.aws_region },
    ]

    secrets = [
      {
        name      = "DATABASE_URL"
        valueFrom = "${aws_secretsmanager_secret.database.arn}:database_url::"
      },
      {
        name      = "API_KEY"
        valueFrom = "${aws_secretsmanager_secret.api_key.arn}:api_key::"
      },
    ]

    logConfiguration = {
      logDriver = "awslogs"
      options = {
        awslogs-group         = aws_cloudwatch_log_group.api.name
        awslogs-region        = var.aws_region
        awslogs-stream-prefix = "api"
      }
    }

    healthCheck = {
      command     = ["CMD-SHELL", "curl -f http://127.0.0.1:8000/api/live || exit 1"]
      interval    = 30
      timeout     = 5
      retries     = 8
      startPeriod = 300
    }
  }])
}

resource "aws_ecs_task_definition" "ui" {
  family                   = "${local.name}-ui"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = var.ui_cpu
  memory                   = var.ui_memory
  execution_role_arn       = aws_iam_role.ecs_execution_ui.arn
  task_role_arn            = aws_iam_role.ecs_task_ui.arn

  container_definitions = jsonencode([{
    name      = "ui"
    image     = local.ui_image
    essential = true

    portMappings = [{
      containerPort = 8501
      hostPort      = 8501
      protocol      = "tcp"
    }]

    environment = [
      { name = "RRE_API_BASE_URL", value = local.ui_api_base_url },
      { name = "LOG_JSON", value = "true" },
    ]

    secrets = [{
      name      = "API_KEY"
      valueFrom = "${aws_secretsmanager_secret.api_key.arn}:api_key::"
    }]

    logConfiguration = {
      logDriver = "awslogs"
      options = {
        awslogs-group         = aws_cloudwatch_log_group.ui.name
        awslogs-region        = var.aws_region
        awslogs-stream-prefix = "ui"
      }
    }

    healthCheck = {
      command     = ["CMD-SHELL", "curl -f http://127.0.0.1:8501/_stcore/health || exit 1"]
      interval    = 30
      timeout     = 5
      retries     = 8
      startPeriod = 300
    }
  }])
}

resource "aws_ecs_service" "api" {
  name            = "${local.name}-api"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.api.arn
  desired_count   = var.api_desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = data.aws_subnets.default.ids
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = !var.enable_no_egress_networking
  }

  dynamic "service_registries" {
    for_each = var.enable_no_egress_networking ? [1] : []
    content {
      registry_arn = aws_service_discovery_service.api[0].arn
    }
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.api.arn
    container_name   = "api"
    container_port   = 8000
  }

  # desired_count=1: min 100% blocks deploys when the sole task is ALB-unhealthy
  # (common while Bedrock Converse holds a worker during burn-in).
  deployment_minimum_healthy_percent = 0
  deployment_maximum_percent         = 200
  # Allow Alembic + multi-worker bind before ALB marks the sole target unhealthy.
  health_check_grace_period_seconds = 420

  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }

  depends_on = [
    aws_lb_listener.http,
    aws_vpc_endpoint.s3,
    aws_vpc_endpoint.interface,
  ]
}

resource "aws_ecs_service" "ui" {
  name            = "${local.name}-ui"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.ui.arn
  desired_count   = var.ui_desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = data.aws_subnets.default.ids
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = !var.enable_no_egress_networking
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.ui.arn
    container_name   = "ui"
    container_port   = 8501
  }

  deployment_minimum_healthy_percent = 0
  deployment_maximum_percent         = 200
  health_check_grace_period_seconds  = 420

  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }

  depends_on = [
    aws_lb_listener.http,
    aws_vpc_endpoint.s3,
    aws_vpc_endpoint.interface,
  ]
}

# React product UI — provisioned at desired_count=0 until ALB cutover.
resource "aws_ecs_task_definition" "web" {
  family                   = "${local.name}-web"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = var.web_cpu
  memory                   = var.web_memory
  execution_role_arn       = aws_iam_role.ecs_execution_ui.arn
  task_role_arn            = aws_iam_role.ecs_task_ui.arn

  container_definitions = jsonencode([{
    name      = "web"
    image     = local.web_image
    essential = true

    portMappings = [{
      containerPort = 80
      hostPort      = 80
      protocol      = "tcp"
    }]

    environment = [
      { name = "LOG_JSON", value = "true" },
    ]

    logConfiguration = {
      logDriver = "awslogs"
      options = {
        awslogs-group         = aws_cloudwatch_log_group.web.name
        awslogs-region        = var.aws_region
        awslogs-stream-prefix = "web"
      }
    }

    healthCheck = {
      command     = ["CMD-SHELL", "wget -q -O /dev/null http://127.0.0.1/ || curl -f http://127.0.0.1/ || exit 1"]
      interval    = 30
      timeout     = 5
      retries     = 3
      startPeriod = 30
    }
  }])
}

resource "aws_ecs_service" "web" {
  name            = "${local.name}-web"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.web.arn
  desired_count   = var.web_desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = data.aws_subnets.default.ids
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = !var.enable_no_egress_networking
  }

  deployment_minimum_healthy_percent = 0
  deployment_maximum_percent         = 200

  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }

  depends_on = [
    aws_vpc_endpoint.s3,
    aws_vpc_endpoint.interface,
  ]
}

resource "aws_ecs_task_definition" "worker" {
  family                   = "${local.name}-worker"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = var.worker_cpu
  memory                   = var.worker_memory
  execution_role_arn       = aws_iam_role.ecs_execution.arn
  task_role_arn            = aws_iam_role.ecs_task_worker.arn

  container_definitions = jsonencode([{
    name      = "worker"
    image     = local.api_image
    essential = true

    environment = [
      { name = "RRE_PROCESS", value = "worker" },
      { name = "LOG_JSON", value = "true" },
      { name = "LOG_LEVEL", value = "INFO" },
      { name = "PYTHONUNBUFFERED", value = "1" },
      { name = "LLM_PROVIDER", value = var.llm_provider },
      { name = "BEDROCK_MODEL_ID", value = var.bedrock_model_id },
      { name = "UPLOADS_BUCKET", value = aws_s3_bucket.uploads.bucket },
      { name = "TRANSCRIPTION_PROVIDER", value = var.transcription_provider },
      { name = "TRANSCRIBE_TIMEOUT_SECONDS", value = "3600" },
      { name = "WORKFLOW_MODULE_CONCURRENCY", value = "3" },
      { name = "BEDROCK_PROMPT_CACHE", value = "true" },
      { name = "BEDROCK_PROMPT_CACHE_TTL", value = "1h" },
      { name = "BEDROCK_MAX_TOKENS", value = "8192" },
      { name = "MODULE_RUN_MAX_RETRIES", value = "1" },
      { name = "WORKFLOW_JOB_TIMEOUT_SECONDS", value = "7200" },
      { name = "WORKFLOW_JOB_MAX_ATTEMPTS", value = "2" },
      { name = "WORKFLOW_WORKER_POLL_SECONDS", value = "2" },
      { name = "WORKFLOW_WORKER_MAX_CLAIM_PER_POLL", value = "1" },
      { name = "WORKFLOW_WORKER_MAX_IN_FLIGHT", value = "2" },
      { name = "WORKFLOW_WORKER_HEALTH_PORT", value = "8080" },
      { name = "WORKFLOW_JOB_STALE_SECONDS", value = "7800" },
      { name = "BEDROCK_THROTTLE_MAX_RETRIES", value = "5" },
      { name = "BEDROCK_THROTTLE_BASE_SECONDS", value = "2" },
      { name = "DIARIZATION_ENABLED", value = var.diarization_enabled ? "true" : "false" },
      { name = "ALEMBIC_AUTO_UPGRADE", value = "false" },
      { name = "TEMP_DIR", value = "/tmp/rre" },
      { name = "AWS_REGION", value = var.aws_region },
      { name = "AWS_DEFAULT_REGION", value = var.aws_region },
    ]

    secrets = [
      {
        name      = "DATABASE_URL"
        valueFrom = "${aws_secretsmanager_secret.database.arn}:database_url::"
      },
    ]

    logConfiguration = {
      logDriver = "awslogs"
      options = {
        awslogs-group         = aws_cloudwatch_log_group.worker.name
        awslogs-region        = var.aws_region
        awslogs-stream-prefix = "worker"
      }
    }

    healthCheck = {
      command     = ["CMD-SHELL", "curl -f http://127.0.0.1:8080/health || exit 1"]
      interval    = 30
      timeout     = 5
      retries     = 3
      startPeriod = 60
    }
  }])
}

resource "aws_ecs_service" "worker" {
  name            = "${local.name}-worker"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.worker.arn
  desired_count   = var.worker_desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = data.aws_subnets.default.ids
    security_groups  = [aws_security_group.ecs_tasks.id]
    assign_public_ip = !var.enable_no_egress_networking
  }

  deployment_minimum_healthy_percent = 0
  deployment_maximum_percent         = 200

  deployment_circuit_breaker {
    enable   = true
    rollback = true
  }

  depends_on = [
    aws_vpc_endpoint.s3,
    aws_vpc_endpoint.interface,
  ]
}
