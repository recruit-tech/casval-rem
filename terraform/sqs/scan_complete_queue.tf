resource "aws_sqs_queue" "scan_complete_queue" {
  name                        = "ScanComplete"
  visibility_timeout_seconds  = 300
  message_retention_seconds   = 1209600
  provisioner "local-exec" {
    command = "echo SCAN_COMPLETE_QUEUE_URL = \\\"${aws_sqs_queue.scan_complete_queue.id}\\\" > ./chalicelib/env/scan_complete_queue.py"
  }
}