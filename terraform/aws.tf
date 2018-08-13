output "bucket" {
  value = "${module.s3.bucket}"
}

output "subnet" {
  value = "${module.vpc.subnet}"
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
