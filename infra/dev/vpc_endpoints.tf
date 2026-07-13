# P0-AWS-5h — VPC endpoints for AWS API access without public internet.
# create endpoints with enable_vpc_endpoints; drop public IPs only when enable_no_egress_networking.
#
# S3 gateway must attach to route tables. Do NOT look up RTs by subnet_id in the
# default VPC — subnets often use the main RT with no explicit association, and
# data.aws_route_table { subnet_id = ... } then returns "no results".
#
# Keep this data source un-counted so its address stays stable across applies
# (counted ↔ uncounted moves break CI terraform apply -target=ECR).

data "aws_route_tables" "vpc" {
  vpc_id = data.aws_vpc.default.id
}

moved {
  from = data.aws_route_tables.vpc[0]
  to   = data.aws_route_tables.vpc
}

locals {
  s3_route_table_ids = var.enable_vpc_endpoints ? data.aws_route_tables.vpc.ids : []

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
