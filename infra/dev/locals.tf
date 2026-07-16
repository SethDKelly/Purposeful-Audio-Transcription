locals {
  account_id = data.aws_caller_identity.current.account_id
  name       = var.name_prefix

  api_image = "${aws_ecr_repository.api.repository_url}:${var.image_tag}"
  ui_image  = "${aws_ecr_repository.ui.repository_url}:${var.image_tag}"

  api_log_group = "/rre/dev/api"
  ui_log_group  = "/rre/dev/ui"

  # UI server-side httpx calls: public ALB when tasks have public IPs; Cloud Map when private.
  https_enabled   = trimspace(var.acm_certificate_arn) != ""
  alb_scheme      = local.https_enabled ? "https" : "http"
  ui_api_base_url = var.enable_no_egress_networking ? "http://api.${var.name_prefix}.local:8000" : "${local.alb_scheme}://${aws_lb.main.dns_name}"
}
