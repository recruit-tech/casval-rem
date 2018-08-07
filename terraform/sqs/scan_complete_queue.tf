resource "aws_sqs_queue" "scan_complete_queue" {
  name                        = "ScanComplete"
  visibility_timeout_seconds  = 300
  message_retention_seconds   = 1209600
}