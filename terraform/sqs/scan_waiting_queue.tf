resource "aws_sqs_queue" "scan_waiting_queue" {
  name                        = "ScanWaiting"
  visibility_timeout_seconds  = 60
  message_retention_seconds   = 1209600
}