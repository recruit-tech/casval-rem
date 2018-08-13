module "aws" {
  source = "./terraform"
}

resource "null_resource" "chalice" {
  depends_on = ["module.aws"]
  provisioner "local-exec" {
    command = "cp terraform.tfstate ./chalicelib/batches/ && chalice deploy --stage dev"
  }
  provisioner "local-exec" {
    when = "destroy"
    command = "chalice delete && cp terraform.tfstate ./chalicelib/batches/"
  }
}

resource "null_resource" "lambda-vpc" {
  depends_on = ["null_resource.chalice"]
  provisioner "local-exec" {
    interpreter = ["python", "-c"]
    command  = <<SCRIPT
import os
import json
import logging

file_path = ".chalice/deployed/{stage}.json".format(stage=os.environ["STAGE"])
with open(file_path, "r") as file:
    try:
        chalice_config = json.load(file)
        for resource in chalice_config["resources"]:
            if resource["resource_type"] == "lambda_function":
                print(resource)
                cmd = "aws lambda update-function-configuration --function-name {f} --vpc-config SubnetIds=[\"{subnet}\"],SecurityGroupIds=[\"{sg}\"]".format(f=resource["lambda_arn"], subnet=os.environ["SUBNET"], sg=os.environ["SECURITY_GROUP"])
                os.system(cmd)
    except Exception as e:
        logging.error(e)
SCRIPT
    environment {
      STAGE = "dev"
      SUBNET="${module.aws.subnet}"
      SECURITY_GROUP="${module.aws.security_group}"
    }
  }
}
