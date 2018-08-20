resource "aws_sqs_queue" "scan_pending_queue" {
  name                        = "ScanPending"
  message_retention_seconds   = 1209600
}