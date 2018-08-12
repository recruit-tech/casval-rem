output "subnet" {
  value = "${module.vpc.subnet}"
}

output "security_group" {
  value = "${module.vpc.security_group}"
}

provider "aws" {
}

module "sqs" {
  source = "./sqs"
}

module "vpc" {
  source = "./vpc"
}
