# Queue / worker operational alarms (v1.1 Workstream E).
# Metrics are published by the worker process to namespace RRE/Dev.

resource "aws_cloudwatch_metric_alarm" "queue_oldest_age" {
  alarm_name          = "${local.name}-queue-oldest-age"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "OldestQueuedJobAgeSeconds"
  namespace           = "RRE/Dev"
  period              = 60
  statistic           = "Maximum"
  threshold           = 1800
  treat_missing_data  = "notBreaching"
  alarm_description   = "Oldest queued workflow job age exceeded 30 minutes"
}

resource "aws_cloudwatch_metric_alarm" "queue_depth" {
  alarm_name          = "${local.name}-queue-depth"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 3
  metric_name         = "QueueDepth"
  namespace           = "RRE/Dev"
  period              = 60
  statistic           = "Maximum"
  threshold           = 20
  treat_missing_data  = "notBreaching"
  alarm_description   = "Workflow queue depth is high"
}

resource "aws_cloudwatch_metric_alarm" "worker_healthy_missing" {
  alarm_name          = "${local.name}-worker-heartbeat-missing"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 3
  metric_name         = "WorkerHealthy"
  namespace           = "RRE/Dev"
  period              = 60
  statistic           = "Sum"
  threshold           = 1
  treat_missing_data  = "breaching"
  alarm_description   = "Worker has not published a healthy heartbeat recently"
}
