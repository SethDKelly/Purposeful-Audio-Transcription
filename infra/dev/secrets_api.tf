# Application API key for UI→API auth (V07-1b). Always provisioned so
# Streamlit and FastAPI share the same secret via Secrets Manager.

resource "random_password" "api_key" {
  length  = 48
  special = false
}

resource "aws_secretsmanager_secret" "api_key" {
  name = "${local.name}/api-key"
}

resource "aws_secretsmanager_secret_version" "api_key" {
  secret_id = aws_secretsmanager_secret.api_key.id

  secret_string = jsonencode({
    api_key = random_password.api_key.result
  })
}
