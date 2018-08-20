resource "aws_sqs_queue" "scan_running_queue" {
  name                        = "ScanRunning"
  message_retention_seconds   = 1209600
}