variable "subnet_primary" {}
variable "subnet_secondary" {}
variable "security_group" {}


resource "aws_rds_cluster_parameter_group" "tz" {
    family = "aurora5.6"
    parameter {
      name = "time_zone"
      value = "UTC"
     }
}

resource "aws_db_subnet_group" "default" {
  subnet_ids = ["${var.subnet_primary}", "${var.subnet_secondary}"]
}

resource "null_resource" "aurora-serverless" {
  depends_on = ["aws_rds_cluster_parameter_group.tz"]
  provisioner "local-exec" {
    command  = "aws rds create-db-cluster --db-cluster-identifier $CLUSTER_ID --engine aurora --engine-version 5.6.10a --engine-mode serverless --scaling-configuration MinCapacity=2,MaxCapacity=8,SecondsUntilAutoPause=1000,AutoPause=true --master-username $USER --master-user-password $PASSWORD --db-subnet-group-name $SUBNET_GROUP --vpc-security-group-ids $SECURITY_GROUP --db-cluster-parameter-group-name $PARAMETER_GROUP"
    environment {
      CLUSTER_ID = "casval-aurora-cluster"
      USER = "admin"
      PASSWORD = "admin123"
      SECURITY_GROUP = "${var.security_group}"
      SUBNET_GROUP = "${aws_db_subnet_group.default.id}"
      PARAMETER_GROUP = "${aws_rds_cluster_parameter_group.tz.name}"
    }
  }
}
