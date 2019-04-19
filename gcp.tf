variable "secret_key" {
  default = "5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a5a"
}

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

resource "google_sql_user" "users" {
  name     = "root"
  instance = "${google_sql_database_instance.master.name}"
  password = "admin123"
}

resource "google_sql_database" "casval" {
  name      = "casval"
  instance  = "${google_sql_database_instance.master.name}"
  charset   = "utf8mb4"
  collation = "utf8mb4_unicode_ci"
}

resource "null_resource" "generate-config" {
  depends_on = ["google_sql_database_instance.master"]

  provisioner "local-exec" {
    command = <<SCRIPT
echo "
env_variables:
  SECRET_KEY: '$SECRET_KEY'
  DB_NAME: '$DB_NAME'
  DB_USER: '$DB_USER'
  DB_PASSWORD: '$DB_PASSWORD'
  DB_INSTANCE_NAME: '$DB_INSTANCE_NAME'
" > ./config.yaml
SCRIPT

    environment {
      SECRET_KEY       = "${var.secret_key}"
      DB_NAME          = "${var.db_name}"
      DB_USER          = "${var.db_user}"
      DB_PASSWORD      = "${var.db_password}"
      DB_INSTANCE_NAME = "${google_sql_database_instance.master.connection_name}"
    }
  }

  provisioner "local-exec" {
    when    = "destroy"
    command = "echo '' > ./config.yaml"
  }
}
