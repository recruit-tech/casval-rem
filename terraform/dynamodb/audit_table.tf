resource "aws_dynamodb_table" "audit_table" {
  name           = "Audit"
  read_capacity  = 10
  write_capacity = 5
  hash_key       = "id"

  attribute = [{
    name = "id"
    type = "S"
  }, {
    name = "status"
    type = "S"
  }, {
    name = "updated_at"
    type = "S"
  }]

  point_in_time_recovery {
    enabled = true
  }

  global_secondary_index {
    name               = "UpdatedAtIndex"
    hash_key           = "status"
    range_key          = "updated_at"
    write_capacity     = 10
    read_capacity      = 5
    projection_type    = "ALL"
  }
}

resource "aws_appautoscaling_target" "audit_table_read_target" {
  max_capacity       = 100
  min_capacity       = 5
  resource_id        = "table/Audit"
  scalable_dimension = "dynamodb:table:ReadCapacityUnits"
  service_namespace  = "dynamodb"
}

resource "aws_appautoscaling_target" "audit_table_write_target" {
  max_capacity       = 100
  min_capacity       = 5
  resource_id        = "table/Audit"
  scalable_dimension = "dynamodb:table:WriteCapacityUnits"
  service_namespace  = "dynamodb"
}

resource "aws_appautoscaling_target" "audit_table_updated_at_index_read_target" {
  max_capacity       = 100
  min_capacity       = 5
  resource_id        = "table/Audit/index/UpdatedAtIndex"
  scalable_dimension = "dynamodb:index:ReadCapacityUnits"
  service_namespace  = "dynamodb"
}

resource "aws_appautoscaling_target" "audit_table_updated_at_index_write_target" {
  max_capacity       = 100
  min_capacity       = 5
  resource_id        = "table/Audit/index/UpdatedAtIndex"
  scalable_dimension = "dynamodb:index:WriteCapacityUnits"
  service_namespace  = "dynamodb"
}

resource "aws_appautoscaling_policy" "audit_table_read_policy" {
  name               = "DynamoDBReadCapacityUtilization:${aws_appautoscaling_target.audit_table_read_target.resource_id}"
  policy_type        = "TargetTrackingScaling"
  resource_id        = "${aws_appautoscaling_target.audit_table_read_target.resource_id}"
  scalable_dimension = "${aws_appautoscaling_target.audit_table_read_target.scalable_dimension}"
  service_namespace  = "${aws_appautoscaling_target.audit_table_read_target.service_namespace}"
  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "DynamoDBReadCapacityUtilization"
    }
    target_value = 70
  }
}

resource "aws_appautoscaling_policy" "audit_table_write_policy" {
  name               = "DynamoDBWriteCapacityUtilization:${aws_appautoscaling_target.audit_table_write_target.resource_id}"
  policy_type        = "TargetTrackingScaling"
  resource_id        = "${aws_appautoscaling_target.audit_table_write_target.resource_id}"
  scalable_dimension = "${aws_appautoscaling_target.audit_table_write_target.scalable_dimension}"
  service_namespace  = "${aws_appautoscaling_target.audit_table_write_target.service_namespace}"
  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "DynamoDBWriteCapacityUtilization"
    }
    target_value = 70
  }
}

resource "aws_appautoscaling_policy" "audit_table_updated_at_index_read_policy" {
  name               = "DynamoDBReadCapacityUtilization:${aws_appautoscaling_target.audit_table_updated_at_index_read_target.resource_id}"
  policy_type        = "TargetTrackingScaling"
  resource_id        = "${aws_appautoscaling_target.audit_table_updated_at_index_read_target.resource_id}"
  scalable_dimension = "${aws_appautoscaling_target.audit_table_updated_at_index_read_target.scalable_dimension}"
  service_namespace  = "${aws_appautoscaling_target.audit_table_updated_at_index_read_target.service_namespace}"
  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "DynamoDBReadCapacityUtilization"
    }
    target_value = 70
  }
}

resource "aws_appautoscaling_policy" "audit_table_updated_at_index_write_policy" {
  name               = "DynamoDBWriteCapacityUtilization:${aws_appautoscaling_target.audit_table_updated_at_index_write_target.resource_id}"
  policy_type        = "TargetTrackingScaling"
  resource_id        = "${aws_appautoscaling_target.audit_table_updated_at_index_write_target.resource_id}"
  scalable_dimension = "${aws_appautoscaling_target.audit_table_updated_at_index_write_target.scalable_dimension}"
  service_namespace  = "${aws_appautoscaling_target.audit_table_updated_at_index_write_target.service_namespace}"
  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "DynamoDBWriteCapacityUtilization"
    }
    target_value = 70
  }
}