variable "stage" {
  type = "string"
  default = "dev"
}

variable "db_username" {
  type = "string"
  default = "admin"
}

variable "db_password" {
  type = "string"
  default = "admin123"
}

output "stage" {
  value = "${var.stage}"
}

output "bucket" {
  value = "${aws_s3_bucket.report_bucket.id}"
}

output "subnet_primary" {
  value = "${aws_subnet.sn_primary.id}"
}

output "subnet_secondary" {
  value = "${aws_subnet.sn_secondary.id}"
}

output "security_group" {
  value = "${aws_security_group.sg.id}"
}

output "database_username" {
  value = "${aws_rds_cluster.db.master_username}"
}

output "database_password" {
  value = "${aws_rds_cluster.db.master_password}"
}

output "database_name" {
  value = "${aws_rds_cluster.db.database_name}"
}

# null resource for building chalice's config.json from tfstate

resource "null_resource" "generate-config" {
  depends_on = ["aws_rds_cluster.db",
                "aws_s3_bucket.report_bucket",
                "aws_sqs_queue.pending_queue",
                "aws_sqs_queue.running_queue",
                "aws_sqs_queue.stopped_queue"]
  provisioner "local-exec" {
    command = "python .chalice/config_gen.py"
  }
  provisioner "local-exec" {
    when = "destroy"
    command = "rm .chalice/config.json"
  }
}

# aws

provider "aws" {
  region = "us-east-1"
}

# vpc

data "aws_availability_zones" "az" {
}

resource "aws_vpc" "vpc" {
  cidr_block = "10.0.0.0/16"
  tags {
      Name = "CASVAL-VPC"
  }
}

resource "aws_subnet" "sn_primary" {
  availability_zone = "${data.aws_availability_zones.az.names[0]}"
  vpc_id = "${aws_vpc.vpc.id}"
  cidr_block = "10.0.1.0/24"
  tags {
    Name = "CASVAL-SUBNET-PRIMARY"
  }
}

resource "aws_subnet" "sn_secondary" {
  availability_zone = "${data.aws_availability_zones.az.names[1]}"
  vpc_id = "${aws_vpc.vpc.id}"
  cidr_block = "10.0.2.0/24"
  tags {
    Name = "CASVAL-SUBNET-SECONDARY"
  }
}

resource "aws_subnet" "sn_public" {
  availability_zone = "${data.aws_availability_zones.az.names[2]}"
  vpc_id = "${aws_vpc.vpc.id}"
  cidr_block = "10.0.0.0/24"
  tags {
    Name = "CASVAL-SUBNET-PUBLIC"
  }
}

resource "aws_eip" "eip" {
}

resource "aws_nat_gateway" "ngw" {
  allocation_id = "${aws_eip.eip.id}"
  subnet_id     = "${aws_subnet.sn_public.id}"

  tags {
    Name = "CASVAL-NAT-GATEWAY"
  }
}

resource "aws_internet_gateway" "igw" {
  vpc_id = "${aws_vpc.vpc.id}"

  tags {
    Name = "CASVAL-INTERNET-GATEWAY"
  }
}

resource "aws_route_table" "sn_public" {
  vpc_id = "${aws_vpc.vpc.id}"

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = "${aws_internet_gateway.igw.id}"
  }
  tags {
    Name = "CASVAL-PUBLIC-SUBNET-ROUTE-TABLE"
  }
}

resource "aws_route_table" "sn_private" {
  vpc_id = "${aws_vpc.vpc.id}"

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = "${aws_nat_gateway.ngw.id}"
  }
  tags {
    Name = "CASVAL-PRIVATE-SUBNET-ROUTE-TABLE"
  }
}

resource "aws_route_table_association" "public_sn_route" {
  subnet_id      = "${aws_subnet.sn_public.id}"
  route_table_id = "${aws_route_table.sn_public.id}"
}

resource "aws_route_table_association" "private_p_sn_route" {
  subnet_id      = "${aws_subnet.sn_primary.id}"
  route_table_id = "${aws_route_table.sn_private.id}"
}

resource "aws_route_table_association" "priavte_s_sn_route" {
  subnet_id      = "${aws_subnet.sn_secondary.id}"
  route_table_id = "${aws_route_table.sn_private.id}"
}

resource "aws_security_group" "sg" {
  vpc_id = "${aws_vpc.vpc.id}"
  ingress {
    cidr_blocks = ["0.0.0.0/0"]
    from_port = 3306
    to_port = 3306
    protocol = "tcp"
  }
  egress {
    cidr_blocks = ["0.0.0.0/0"]
    from_port = 0
    to_port = 0
    protocol = "-1"
  }
  tags {
   Name = "CASVAL-SECURITY-GROUP"
  }
}

resource "aws_db_subnet_group" "sn_group" {
  subnet_ids = ["${aws_subnet.sn_primary.id}", "${aws_subnet.sn_secondary.id}"]
}

# rds

resource "aws_rds_cluster_parameter_group" "params" {
    name = "rds-cluster-pg"
    family = "aurora5.6"
    parameter {
      name = "time_zone"
      value = "UTC"
     }
    parameter {
      name = "character_set_server"
      value = "utf8mb4"
     }
}

resource "aws_rds_cluster" "db" {
  depends_on = ["aws_rds_cluster_parameter_group.params"]
  engine = "aurora"
  engine_version = "5.6.10a"
  engine_mode = "serverless"
  cluster_identifier = "casval-aurora-cluster"
  vpc_security_group_ids = ["${aws_security_group.sg.id}"]
  db_subnet_group_name = "${aws_db_subnet_group.sn_group.id}"
  db_cluster_parameter_group_name = "${aws_rds_cluster_parameter_group.params.name}"
  database_name = "casval_dev"
  master_username = "${var.db_username}"
  master_password = "${var.db_password}"
  final_snapshot_identifier = "casval-dev-final-snapshot"
  backup_retention_period = 3
  preferred_backup_window = "17:00-19:00"

#  lifecycle {
#    prevent_destroy = true
#  }

#  scaling_configuration {
#    auto_pause = true
#    max_capacity = 8
#    min_capacity = 2
#    seconds_until_auto_pause = 900
#  }

}

# s3

resource "aws_s3_bucket" "report_bucket" {
  bucket_prefix = "casval-dev"
}

# sqs

resource "aws_sqs_queue" "pending_queue" {
  name = "ScanPending"
  message_retention_seconds = 1209600
}

resource "aws_sqs_queue" "running_queue" {
  name = "ScanRunning"
  message_retention_seconds = 1209600
}

resource "aws_sqs_queue" "stopped_queue" {
  name  = "ScanStopped"
  message_retention_seconds = 1209600
}
