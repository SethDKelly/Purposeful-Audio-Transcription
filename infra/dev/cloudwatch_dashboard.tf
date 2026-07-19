# Ops dashboard for API / UI / worker (v1.1 Workstream G).

resource "aws_cloudwatch_dashboard" "rre_dev" {
  dashboard_name = "${local.name}-ops"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 8
        height = 6
        properties = {
          title   = "Queue depth"
          region  = var.aws_region
          view    = "timeSeries"
          stacked = false
          metrics = [
            ["RRE/Dev", "QueueDepth"]
          ]
          period = 60
          stat   = "Maximum"
        }
      },
      {
        type   = "metric"
        x      = 8
        y      = 0
        width  = 8
        height = 6
        properties = {
          title   = "Oldest queued job age (s)"
          region  = var.aws_region
          view    = "timeSeries"
          stacked = false
          metrics = [
            ["RRE/Dev", "OldestQueuedJobAgeSeconds"]
          ]
          period = 60
          stat   = "Maximum"
        }
      },
      {
        type   = "metric"
        x      = 16
        y      = 0
        width  = 8
        height = 6
        properties = {
          title   = "Worker in-flight / healthy"
          region  = var.aws_region
          view    = "timeSeries"
          stacked = false
          metrics = [
            ["RRE/Dev", "WorkerInFlight"],
            [".", "WorkerHealthy"]
          ]
          period = 60
          stat   = "Maximum"
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 6
        width  = 12
        height = 6
        properties = {
          title   = "ECS CPU utilization"
          region  = var.aws_region
          view    = "timeSeries"
          stacked = false
          metrics = [
            ["AWS/ECS", "CPUUtilization", "ServiceName", aws_ecs_service.api.name, "ClusterName", aws_ecs_cluster.main.name],
            ["...", aws_ecs_service.ui.name, ".", "."],
            ["...", aws_ecs_service.worker.name, ".", "."]
          ]
          period = 60
          stat   = "Average"
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 6
        width  = 12
        height = 6
        properties = {
          title   = "ECS memory utilization"
          region  = var.aws_region
          view    = "timeSeries"
          stacked = false
          metrics = [
            ["AWS/ECS", "MemoryUtilization", "ServiceName", aws_ecs_service.api.name, "ClusterName", aws_ecs_cluster.main.name],
            ["...", aws_ecs_service.ui.name, ".", "."],
            ["...", aws_ecs_service.worker.name, ".", "."]
          ]
          period = 60
          stat   = "Average"
        }
      }
    ]
  })
}
