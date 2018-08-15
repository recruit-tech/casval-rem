data "aws_availability_zones" "available" {}

output "subnet_primary" {
  value = "${aws_subnet.primary.id}"
}

output "subnet_secondary" {
  value = "${aws_subnet.secondary.id}"
}

output "security_group" {
  value = "${aws_security_group.default.id}"
}


resource "aws_vpc" "default" {
  cidr_block = "10.0.0.0/16"
  tags {
      Name = "CASVAL-VPC"
  }
}

resource "aws_subnet" "primary" {
  availability_zone = "${data.aws_availability_zones.available.names[0]}"
  vpc_id = "${aws_vpc.default.id}"
  cidr_block = "10.0.1.0/24"
}

resource "aws_subnet" "secondary" {
  availability_zone = "${data.aws_availability_zones.available.names[1]}"
  vpc_id = "${aws_vpc.default.id}"
  cidr_block = "10.0.2.0/24"
}

resource "aws_security_group" "default" {
  vpc_id = "${aws_vpc.default.id}"
  egress {
      from_port = 0
      to_port = 0
      protocol = "-1"
      cidr_blocks = ["0.0.0.0/0"]
  }
}
