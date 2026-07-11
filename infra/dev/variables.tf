variable "aws_region" {
  description = "AWS region for dev deployment."
  type        = string
  default     = "us-east-2"
}

variable "name_prefix" {
  description = "Resource name prefix (must match aws-backbone IAM scope rre-dev-*)."
  type        = string
  default     = "rre-dev"
}

variable "image_tag" {
  description = "Container image tag for API and UI (typically git SHA from CI)."
  type        = string
  default     = "latest"
}

variable "api_cpu" {
  description = "Fargate CPU units for API task."
  type        = number
  default     = 1024
}

variable "api_memory" {
  description = "Fargate memory (MiB) for API task."
  type        = number
  default     = 4096
}

variable "ui_cpu" {
  description = "Fargate CPU units for UI task."
  type        = number
  default     = 256
}

variable "ui_memory" {
  description = "Fargate memory (MiB) for UI task."
  type        = number
  default     = 512
}

variable "api_desired_count" {
  type    = number
  default = 1
}

variable "ui_desired_count" {
  type    = number
  default = 1
}

variable "db_instance_class" {
  type    = string
  default = "db.t4g.micro"
}

variable "log_retention_days" {
  type    = number
  default = 14
}

variable "llm_provider" {
  description = "LLM backend for API tasks: ollama (local) or bedrock (AWS)."
  type        = string
  default     = "bedrock"
}

variable "bedrock_model_id" {
  description = "Default Bedrock foundation model ID for module runs."
  type        = string
  default     = "anthropic.claude-3-5-sonnet-20241022-v2:0"
}
