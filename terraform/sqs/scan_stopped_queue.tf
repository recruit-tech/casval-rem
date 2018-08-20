resource "aws_sqs_queue" "scan_stopped_queue" {
  name                        = "ScanStopped"
  message_retention_seconds   = 1209600
}