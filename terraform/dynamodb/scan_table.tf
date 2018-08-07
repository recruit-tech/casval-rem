resource "aws_dynamodb_table" "scan_table" {
  name           = "Scan"
  read_capacity  = 10
  write_capacity = 5
  hash_key       = "id"

  attribute = [{
    name = "id"
    type = "S"
  }, {
    name = "audit_id"
    type = "S"
  }, {
    name = "created_at"
    type = "S"
  }]

  point_in_time_recovery {
    enabled = true
  }

  global_secondary_index {
    name               = "AuditIdIndex"
    hash_key           = "audit_id"
    range_key          = "created_at"
    write_capacity     = 10
    read_capacity      = 5
    projection_type    = "ALL"
  }
}

resource "aws_appautoscaling_target" "scan_table_read_target" {
  max_capacity       = 100
  min_capacity       = 5
  resource_id        = "table/Scan"
  scalable_dimension = "dynamodb:table:ReadCapacityUnits"
  service_namespace  = "dynamodb"
}

resource "aws_appautoscaling_target" "scan_table_write_target" {
  max_capacity       = 100
  min_capacity       = 5
  resource_id        = "table/Scan"
  scalable_dimension = "dynamodb:table:WriteCapacityUnits"
  service_namespace  = "dynamodb"
}

resource "aws_appautoscaling_target" "scan_table_audit_id_index_read_target" {
  max_capacity       = 100
  min_capacity       = 5
  resource_id        = "table/Scan/index/AuditIdIndex"
  scalable_dimension = "dynamodb:index:ReadCapacityUnits"
  service_namespace  = "dynamodb"
}

resource "aws_appautoscaling_target" "scan_table_audit_id_index_write_target" {
  max_capacity       = 100
  min_capacity       = 5
  resource_id        = "table/Scan/index/AuditIdIndex"
  scalable_dimension = "dynamodb:index:WriteCapacityUnits"
  service_namespace  = "dynamodb"
}

resource "aws_appautoscaling_policy" "scan_table_read_policy" {
  name               = "DynamoDBReadCapacityUtilization:${aws_appautoscaling_target.scan_table_read_target.resource_id}"
  policy_type        = "TargetTrackingScaling"
  resource_id        = "${aws_appautoscaling_target.scan_table_read_target.resource_id}"
  scalable_dimension = "${aws_appautoscaling_target.scan_table_read_target.scalable_dimension}"
  service_namespace  = "${aws_appautoscaling_target.scan_table_read_target.service_namespace}"
  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "DynamoDBReadCapacityUtilization"
    }
    target_value = 70
  }
}

resource "aws_appautoscaling_policy" "scan_table_write_policy" {
  name               = "DynamoDBWriteCapacityUtilization:${aws_appautoscaling_target.scan_table_write_target.resource_id}"
  policy_type        = "TargetTrackingScaling"
  resource_id        = "${aws_appautoscaling_target.scan_table_write_target.resource_id}"
  scalable_dimension = "${aws_appautoscaling_target.scan_table_write_target.scalable_dimension}"
  service_namespace  = "${aws_appautoscaling_target.scan_table_write_target.service_namespace}"
  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "DynamoDBWriteCapacityUtilization"
    }
    target_value = 70
  }
}

resource "aws_appautoscaling_policy" "scan_table_audit_id_index_read_policy" {
  name               = "DynamoDBReadCapacityUtilization:${aws_appautoscaling_target.scan_table_audit_id_index_read_target.resource_id}"
  policy_type        = "TargetTrackingScaling"
  resource_id        = "${aws_appautoscaling_target.scan_table_audit_id_index_read_target.resource_id}"
  scalable_dimension = "${aws_appautoscaling_target.scan_table_audit_id_index_read_target.scalable_dimension}"
  service_namespace  = "${aws_appautoscaling_target.scan_table_audit_id_index_read_target.service_namespace}"
  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "DynamoDBReadCapacityUtilization"
    }
    target_value = 70
  }
}

resource "aws_appautoscaling_policy" "scan_table_audit_id_index_write_policy" {
  name               = "DynamoDBWriteCapacityUtilization:${aws_appautoscaling_target.scan_table_audit_id_index_write_target.resource_id}"
  policy_type        = "TargetTrackingScaling"
  resource_id        = "${aws_appautoscaling_target.scan_table_audit_id_index_write_target.resource_id}"
  scalable_dimension = "${aws_appautoscaling_target.scan_table_audit_id_index_write_target.scalable_dimension}"
  service_namespace  = "${aws_appautoscaling_target.scan_table_audit_id_index_write_target.service_namespace}"
  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "DynamoDBWriteCapacityUtilization"
    }
    target_value = 70
  }
}