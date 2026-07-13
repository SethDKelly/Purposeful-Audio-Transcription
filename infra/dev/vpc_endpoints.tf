# P0-AWS-5h — VPC endpoints for AWS API access without public internet.
# create endpoints with enable_vpc_endpoints; drop public IPs only when enable_no_egress_networking.

data "aws_route_table" "subnet" {
  for_each  = var.enable_vpc_endpoints ? toset(data.aws_subnets.default.ids) : toset([])
  subnet_id = each.value
}

locals {
  # ECR image layers are served from S3 — gateway must cover every task subnet RT.
  s3_route_table_ids = var.enable_vpc_endpoints ? distinct([
    for rt in data.aws_route_table.subnet : rt.id
  ]) : []

  interface_endpoint_services = var.enable_vpc_endpoints ? toset([
    "bedrock-runtime",
    "bedrock",
    "transcribe",
    "secretsmanager",
    "logs",
    "ecr.api",
    "ecr.dkr",
    "sts",
    "monitoring",
  ]) : toset([])
}

resource "aws_security_group" "vpc_endpoints" {
  count = var.enable_vpc_endpoints ? 1 : 0

  name        = "${local.name}-vpc-endpoints"
  description = "Interface VPC endpoints for RRE dev (HTTPS from ECS tasks)"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "HTTPS from VPC (ECS tasks)"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [data.aws_vpc.default.cidr_block]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_vpc_endpoint" "s3" {
  count = var.enable_vpc_endpoints ? 1 : 0

  vpc_id            = data.aws_vpc.default.id
  service_name      = "com.amazonaws.${var.aws_region}.s3"
  vpc_endpoint_type = "Gateway"
  route_table_ids   = local.s3_route_table_ids

  tags = {
    Name = "${local.name}-s3"
  }
}

resource "aws_vpc_endpoint" "interface" {
  for_each = local.interface_endpoint_services

  vpc_id              = data.aws_vpc.default.id
  service_name        = "com.amazonaws.${var.aws_region}.${each.value}"
  vpc_endpoint_type   = "Interface"
  subnet_ids          = data.aws_subnets.default.ids
  security_group_ids  = [aws_security_group.vpc_endpoints[0].id]
  private_dns_enabled = true

  tags = {
    Name = "${local.name}-${replace(each.value, ".", "-")}"
  }
}
