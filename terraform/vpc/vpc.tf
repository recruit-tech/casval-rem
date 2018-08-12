output "subnet" {
  value = "${aws_subnet.default.id}"
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

resource "aws_subnet" "default" {
    vpc_id = "${aws_vpc.default.id}"
    cidr_block = "10.0.1.0/24"
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
