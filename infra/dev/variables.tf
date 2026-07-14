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
  description = "Fargate CPU units for API task (1024 = 1 vCPU). 512 caused ALB /api/live timeouts during cutover; slim image still needs headroom for boot + Alembic."
  type        = number
  default     = 1024
}

variable "api_memory" {
  description = "Fargate memory (MiB) for API task. Cut from Whisper-era 4096; Bedrock/Transcribe are off-box."
  type        = number
  default     = 2048
}

variable "ui_cpu" {
  description = "Fargate CPU units for UI task."
  type        = number
  default     = 256
}

variable "ui_memory" {
  description = "Fargate memory (MiB) for UI task (Streamlit cold start)."
  type        = number
  default     = 1024
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
  description = "Bedrock model or inference profile ID for module runs (Claude 4.x requires an inference profile)."
  type        = string
  default     = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
}

variable "transcription_provider" {
  description = "whisper (full image) or transcribe (Amazon Transcribe; use with Dockerfile.cloud)."
  type        = string
  default     = "transcribe"
}

variable "diarization_enabled" {
  description = "Enable pyannote diarization (requires full image + HF token). Off for cloud Transcribe path."
  type        = bool
  default     = false
}

variable "enable_vpc_endpoints" {
  description = "Create VPC endpoints (S3 gateway + interface endpoints for Bedrock, ECR, etc.). Safe with public IPs."
  type        = bool
  default     = true
}

variable "enable_no_egress_networking" {
  description = "Run ECS tasks without public IPs; require VPC endpoints for AWS APIs. UI calls API via Cloud Map. Requires enable_vpc_endpoints=true."
  type        = bool
  default     = true
}

check "no_egress_requires_vpc_endpoints" {
  assert {
    condition     = !var.enable_no_egress_networking || var.enable_vpc_endpoints
    error_message = "enable_no_egress_networking requires enable_vpc_endpoints = true (S3 gateway + ECR/Bedrock interface endpoints)."
  }
}
