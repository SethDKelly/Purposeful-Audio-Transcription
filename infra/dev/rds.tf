resource "random_password" "db" {
  length  = 24
  special = false
}

resource "aws_secretsmanager_secret" "database" {
  name = "${local.name}/database"
}

resource "aws_secretsmanager_secret_version" "database" {
  secret_id = aws_secretsmanager_secret.database.id

  secret_string = jsonencode({
    username     = "rre"
    password     = random_password.db.result
    database     = "rre"
    database_url = "postgresql+psycopg://rre:${random_password.db.result}@${aws_db_instance.main.address}:5432/rre"
  })
}

resource "aws_security_group" "rds" {
  name        = "${local.name}-rds"
  description = "PostgreSQL for RRE dev"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description     = "PostgreSQL from ECS tasks"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs_tasks.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_db_subnet_group" "main" {
  name       = "${local.name}-db"
  subnet_ids = data.aws_subnets.default.ids
}

data "aws_rds_engine_version" "postgres" {
  engine  = "postgres"
  version = "16"
}

resource "aws_db_instance" "main" {
  identifier                 = "${local.name}-postgres"
  engine                     = data.aws_rds_engine_version.postgres.engine
  engine_version             = data.aws_rds_engine_version.postgres.version
  instance_class             = var.db_instance_class
  allocated_storage          = 20
  db_name                    = "rre"
  username                   = "rre"
  password                   = random_password.db.result
  db_subnet_group_name       = aws_db_subnet_group.main.name
  vpc_security_group_ids     = [aws_security_group.rds.id]
  publicly_accessible        = false
  skip_final_snapshot        = true
  deletion_protection        = false
  backup_retention_period    = 1
  auto_minor_version_upgrade = true
  storage_encrypted          = true

  tags = {
    Name = "${local.name}-postgres"
  }
}
