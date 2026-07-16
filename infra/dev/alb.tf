resource "aws_security_group" "alb" {
  name        = "${local.name}-alb"
  description = "ALB for RRE dev"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  dynamic "ingress" {
    for_each = local.https_enabled ? [1] : []
    content {
      description = "HTTPS"
      from_port   = 443
      to_port     = 443
      protocol    = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
    }
  }

  dynamic "egress" {
    for_each = var.enable_no_egress_networking ? [] : [1]
    content {
      from_port   = 0
      to_port     = 0
      protocol    = "-1"
      cidr_blocks = ["0.0.0.0/0"]
    }
  }
}

# S3 gateway endpoints route to the regional S3 prefix list (public IPs), not
# VPC CIDR. Stage B must allow 443 to that prefix list or ECR layer pulls fail.
data "aws_prefix_list" "s3" {
  count = var.enable_no_egress_networking ? 1 : 0
  name  = "com.amazonaws.${var.aws_region}.s3"
}

resource "aws_security_group" "ecs_tasks" {
  name        = "${local.name}-ecs-tasks"
  description = "ECS tasks for RRE dev"
  vpc_id      = data.aws_vpc.default.id

  dynamic "ingress" {
    for_each = var.enable_no_egress_networking ? [1] : []
    content {
      description = "UI to API via Cloud Map"
      from_port   = 8000
      to_port     = 8000
      protocol    = "tcp"
      self        = true
    }
  }

  dynamic "egress" {
    for_each = var.enable_no_egress_networking ? [1] : []
    content {
      description = "HTTPS to VPC interface endpoints"
      from_port   = 443
      to_port     = 443
      protocol    = "tcp"
      cidr_blocks = [data.aws_vpc.default.cidr_block]
    }
  }

  dynamic "egress" {
    for_each = var.enable_no_egress_networking ? [1] : []
    content {
      description     = "HTTPS to S3 via gateway endpoint (ECR image layers)"
      from_port       = 443
      to_port         = 443
      protocol        = "tcp"
      prefix_list_ids = [data.aws_prefix_list.s3[0].id]
    }
  }

  dynamic "egress" {
    for_each = var.enable_no_egress_networking ? [1] : []
    content {
      description = "DNS to AmazonProvidedDNS (VPC+.2)"
      from_port   = 53
      to_port     = 53
      protocol    = "udp"
      cidr_blocks = [data.aws_vpc.default.cidr_block]
    }
  }

  dynamic "egress" {
    for_each = var.enable_no_egress_networking ? [1] : []
    content {
      description = "DNS TCP fallback"
      from_port   = 53
      to_port     = 53
      protocol    = "tcp"
      cidr_blocks = [data.aws_vpc.default.cidr_block]
    }
  }

  dynamic "egress" {
    for_each = var.enable_no_egress_networking ? [1] : []
    content {
      description = "PostgreSQL within VPC"
      from_port   = 5432
      to_port     = 5432
      protocol    = "tcp"
      cidr_blocks = [data.aws_vpc.default.cidr_block]
    }
  }

  dynamic "egress" {
    for_each = var.enable_no_egress_networking ? [1] : []
    content {
      description = "UI to API via Cloud Map"
      from_port   = 8000
      to_port     = 8000
      protocol    = "tcp"
      self        = true
    }
  }

  dynamic "egress" {
    for_each = var.enable_no_egress_networking ? [] : [1]
    content {
      from_port   = 0
      to_port     = 0
      protocol    = "-1"
      cidr_blocks = ["0.0.0.0/0"]
    }
  }
}

resource "aws_security_group_rule" "alb_egress_to_ecs" {
  count = var.enable_no_egress_networking ? 1 : 0

  type                     = "egress"
  description              = "To ECS tasks"
  from_port                = 0
  to_port                  = 65535
  protocol                 = "tcp"
  security_group_id        = aws_security_group.alb.id
  source_security_group_id = aws_security_group.ecs_tasks.id
}

resource "aws_security_group_rule" "ecs_ingress_from_alb" {
  count = var.enable_no_egress_networking ? 1 : 0

  type                     = "ingress"
  description              = "From ALB"
  from_port                = 0
  to_port                  = 65535
  protocol                 = "tcp"
  security_group_id        = aws_security_group.ecs_tasks.id
  source_security_group_id = aws_security_group.alb.id
}

resource "aws_security_group_rule" "ecs_ingress_from_alb_legacy" {
  count = var.enable_no_egress_networking ? 0 : 1

  type                     = "ingress"
  description              = "From ALB"
  from_port                = 0
  to_port                  = 65535
  protocol                 = "tcp"
  security_group_id        = aws_security_group.ecs_tasks.id
  source_security_group_id = aws_security_group.alb.id
}

resource "aws_lb" "main" {
  name               = "${local.name}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = data.aws_subnets.default.ids
}

resource "aws_lb_target_group" "api" {
  name        = "${local.name}-api"
  port        = 8000
  protocol    = "HTTP"
  vpc_id      = data.aws_vpc.default.id
  target_type = "ip"

  deregistration_delay = 15

  health_check {
    enabled           = true
    path              = "/api/live"
    matcher           = "200"
    healthy_threshold = 2
    # Burn-in / Bedrock load can delay answers briefly; require sustained failure
    # before marking the sole API target unhealthy.
    unhealthy_threshold = 10
    interval            = 30
    timeout             = 10
  }
}

resource "aws_lb_target_group" "ui" {
  name        = "${local.name}-ui"
  port        = 8501
  protocol    = "HTTP"
  vpc_id      = data.aws_vpc.default.id
  target_type = "ip"

  deregistration_delay = 15

  health_check {
    enabled             = true
    path                = "/_stcore/health"
    matcher             = "200"
    healthy_threshold   = 2
    unhealthy_threshold = 10
    interval            = 30
    timeout             = 15
  }
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = 80
  protocol          = "HTTP"

  dynamic "default_action" {
    for_each = local.https_enabled ? [1] : []
    content {
      type = "redirect"
      redirect {
        port        = "443"
        protocol    = "HTTPS"
        status_code = "HTTP_301"
      }
    }
  }

  dynamic "default_action" {
    for_each = local.https_enabled ? [] : [1]
    content {
      type             = "forward"
      target_group_arn = aws_lb_target_group.ui.arn
    }
  }
}

resource "aws_lb_listener" "https" {
  count = local.https_enabled ? 1 : 0

  load_balancer_arn = aws_lb.main.arn
  port              = 443
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"
  certificate_arn   = var.acm_certificate_arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.ui.arn
  }
}

locals {
  app_listener_arn = local.https_enabled ? aws_lb_listener.https[0].arn : aws_lb_listener.http.arn
}

resource "aws_lb_listener_rule" "api" {
  listener_arn = local.app_listener_arn
  priority     = 10

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.api.arn
  }

  condition {
    path_pattern {
      values = ["/api", "/api/*"]
    }
  }
}

resource "aws_lb_listener_rule" "api_docs" {
  listener_arn = local.app_listener_arn
  priority     = 20

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.api.arn
  }

  condition {
    path_pattern {
      values = ["/docs", "/docs/*", "/openapi.json", "/redoc", "/redoc/*"]
    }
  }
}
