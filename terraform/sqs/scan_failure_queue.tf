resource "aws_sqs_queue" "scan_failure_queue" {
  name                        = "ScanFailure"
  visibility_timeout_seconds  = 1800
  message_retention_seconds   = 1209600
}