resource "aws_sqs_queue" "scan_ongoing_queue" {
  name                        = "ScanOngoing"
  visibility_timeout_seconds  = 60
  message_retention_seconds   = 1209600
  provisioner "local-exec" {
    command = "echo SCAN_ONGOING_QUEUE_URL = \\\"${aws_sqs_queue.scan_ongoing_queue.id}\\\" > ./chalicelib/env/scan_ongoing_queue.py"
  }
}