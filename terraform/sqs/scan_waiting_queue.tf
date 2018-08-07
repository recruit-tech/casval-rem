resource "aws_sqs_queue" "scan_waiting_queue" {
  name                        = "ScanWaiting"
  visibility_timeout_seconds  = 60
  message_retention_seconds   = 1209600
  provisioner "local-exec" {
    command = "echo SCAN_WAITING_QUEUE_URL = \\\"${aws_sqs_queue.scan_waiting_queue.id}\\\" > ./chalicelib/env/scan_waiting_queue.py"
  }
}