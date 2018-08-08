resource "aws_sqs_queue" "scan_ongoing_queue" {
  name                        = "ScanOngoing"
  visibility_timeout_seconds  = 60
  message_retention_seconds   = 1209600
}