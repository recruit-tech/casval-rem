module "aws" {
  source = "./terraform"
}

resource "null_resource" "chalice" {
  provisioner "local-exec" {
    command = "chalice deploy --stage dev"
  }
}
