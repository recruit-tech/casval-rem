output "bucket" {
  value = "${module.s3.bucket}"
}

output "subnet_primary" {
  value = "${module.vpc.subnet_primary}"
}

output "subnet_secondary" {
  value = "${module.vpc.subnet_secondary}"
}

output "security_group" {
  value = "${module.vpc.security_group}"
}

provider "aws" {
}

module "s3" {
  source = "./s3"
}

module "sqs" {
  source = "./sqs"
}

module "vpc" {
  source = "./vpc"
}

module "aurora" {
  source = "./aurora"
  subnet_primary = "${module.vpc.subnet_primary}"
  subnet_secondary = "${module.vpc.subnet_secondary}"
  security_group = "${module.vpc.security_group}"
}
