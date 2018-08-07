provider "aws" {
}

module "dynamodb" {
  source = "./dynamodb"
}

module "sqs" {
  source = "./sqs"
}
