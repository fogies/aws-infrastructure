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
 * The actual DocumentDB.
 */
resource "aws_docdb_cluster" "docdb" {
  cluster_identifier      = "${var.name}-docdb"
  engine                  = "docdb"

  master_username         = var.admin_user
  master_password         = var.admin_password

  # TODO: make these configurable
  backup_retention_period = 7
  preferred_backup_window = "01:00-04:00"

  # TODO: enable encryption
  # storage_encrypted = true
  # TODO: determine how to store and manage snapshots
  skip_final_snapshot     = true

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
