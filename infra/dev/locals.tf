locals {
  account_id = data.aws_caller_identity.current.account_id
  name       = var.name_prefix

  api_image = "${aws_ecr_repository.api.repository_url}:${var.image_tag}"
  ui_image  = "${aws_ecr_repository.ui.repository_url}:${var.image_tag}"

  api_log_group = "/rre/dev/api"
  ui_log_group  = "/rre/dev/ui"
}
