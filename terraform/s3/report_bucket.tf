output "bucket" {
  value = "${aws_s3_bucket.report-bucket.id}"
}

resource "aws_s3_bucket" "report-bucket" {
  bucket_prefix = "casval-"
}