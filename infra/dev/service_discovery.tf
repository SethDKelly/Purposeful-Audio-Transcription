# Private DNS for UI → API when ECS tasks have no public IP (no NAT).

resource "aws_service_discovery_private_dns_namespace" "main" {
  count = var.enable_no_egress_networking ? 1 : 0

  name = "${local.name}.local"
  vpc  = data.aws_vpc.default.id
}

resource "aws_service_discovery_service" "api" {
  count = var.enable_no_egress_networking ? 1 : 0

  name = "api"

  dns_config {
    namespace_id = aws_service_discovery_private_dns_namespace.main[0].id

    dns_records {
      ttl  = 10
      type = "A"
    }

    routing_policy = "MULTIVALUE"
  }

  health_check_custom_config {
    failure_threshold = 1
  }
}
