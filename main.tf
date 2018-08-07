variable "aws_access_key" {}
variable "aws_secret_key" {}
variable "aws_region" {
  default = "ap-northeast-1"
}
 
module "aws" {
  source = "./terraform"
  aws_access_key = "${var.aws_access_key}"
  aws_secret_key = "${var.aws_secret_key}"
  aws_region = "${var.aws_region}"
}

resource "null_resource" "chalice" {
  provisioner "local-exec" {
    command = "chalice deploy --stage dev"
  }
}