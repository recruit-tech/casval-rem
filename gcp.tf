variable "db_name" {
  default = "casval"
}

variable "db_user" {
  default = "root"
}

variable "db_password" {
  default = "admin123"
}

variable "db_tier" {
  default = "db-n1-standard-1"
}

output "DB_NAME" {
  value = "${google_sql_database.casval.name}"
}

output "DB_USER" {
  value = "${google_sql_user.user.name}"
}

output "DB_PASSWORD" {
  value = "${google_sql_user.user.password}"
}

output "DB_INSTANCE_NAME" {
  value = "${google_sql_database_instance.master.connection_name}"
}

provider "google" {
  project = "frank1"
  region  = "asia-east2"
}

resource "google_sql_database_instance" "master" {
  database_version = "MYSQL_5_7"

  settings {
    tier = "${var.db_tier}"

    database_flags {
      name  = "character_set_server"
      value = "utf8mb4"
    }

    database_flags {
      name  = "default_time_zone"
      value = "+00:00"
    }
  }
}

resource "google_sql_user" "user" {
  name     = "${var.db_user}"
  instance = "${google_sql_database_instance.master.name}"
  password = "${var.db_password}"
}

resource "google_sql_database" "casval" {
  name      = "${var.db_name}"
  instance  = "${google_sql_database_instance.master.name}"
  charset   = "utf8mb4"
  collation = "utf8mb4_unicode_ci"
}
