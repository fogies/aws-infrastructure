/*
 * Indicate which subnets to use for DocumentDB instances.
 *
 * Use any in the provided VPC.
 */
resource "aws_docdb_subnet_group" "subnets" {
  name = "${var.name}-subnets"
  subnet_ids = var.subnet_ids

  tags = local.module_tags
}

/*
 * Paramters for the DocumentDB cluster.
 */
resource "aws_docdb_cluster_parameter_group" "docdb_parameters" {
  family = "docdb4.0"
  name = "${var.name}-docdb-parameters"

  parameter {
    name = "audit_logs"
    value = "enabled"
  }

  tags = local.module_tags
}

/*
 * The actual DocumentDB cluster.
 */
resource "aws_docdb_cluster" "docdb" {
  cluster_identifier      = "${var.name}-docdb"
  engine                  = "docdb"

  master_username         = var.admin_user
  master_password         = var.admin_password

  apply_immediately = var.apply_immediately
  deletion_protection = var.deletion_protection

  backup_retention_period = 35
  enabled_cloudwatch_logs_exports = ["audit"]
  final_snapshot_identifier = "${var.name}-docdb-final-snapshot"
  preferred_backup_window = "00:00-03:00"
  storage_encrypted = true

  db_cluster_parameter_group_name = aws_docdb_cluster_parameter_group.docdb_parameters.name
  db_subnet_group_name = aws_docdb_subnet_group.subnets.id

  tags = local.module_tags
}

/*
 * Instances to power the DocumentDB.
 */
resource "aws_docdb_cluster_instance" "instances" {
  count              = var.instance_count
  identifier         = "${var.name}-instance-${count.index}"
  cluster_identifier = aws_docdb_cluster.docdb.id
  instance_class     = var.instance_class

  tags = local.module_tags
}
