######################
## Master Node Pool
######################


resource "google_container_node_pool" "casval-cluster-master-node-pool" {
  provider = "google-beta"
  cluster            = "${google_container_cluster.casval-cluster.name}"
  initial_node_count = "1"
<<<<<<< HEAD
  location           = "asia-northeast1-a"
=======
  location = "${var.region}"
>>>>>>> 2f8d626... Add terraform

  management {
    auto_repair  = true
    auto_upgrade = false
  }

  name = "master-node-pool"

  autoscaling {
    min_node_count = 1
    max_node_count = 2
  }

  node_config {
    disk_size_gb    = "50"
    disk_type       = "pd-standard"
    image_type      = "COS"
    labels          {}
    local_ssd_count = "0"
    machine_type    = "g1-small"
    metadata        {}
    oauth_scopes    = ["https://www.googleapis.com/auth/cloud-platform"]
    preemptible     = false
    service_account = "default"
    taint {
      key = "CriticalAddonsOnly"
      value = "true"
      effect = "NO_SCHEDULE"
    }
  }

  project = "${var.project}"
}

######################
## Worker Node Pool
######################

resource "google_container_node_pool" "casval-cluster-worker-node-pool" {
  provider = "google-beta"
  cluster            = "${google_container_cluster.casval-cluster.name}"
  initial_node_count = "0"
  location = "${var.region}"

  management {
    auto_repair  = true
    auto_upgrade = false
  }

  name = "worker-node-pool"

  autoscaling {
    min_node_count = 0
    max_node_count = 5
  }

  node_config {
    disk_size_gb    = "50"
    disk_type       = "pd-standard"
    image_type      = "COS"
    labels          {}
    local_ssd_count = "0"
    machine_type    = "n1-standard-1"
    metadata        {}
    oauth_scopes    = ["https://www.googleapis.com/auth/cloud-platform"]
    preemptible     = false
    service_account = "default"
    taint {
      key = "Scanners"
      value = "true"
      effect = "NO_SCHEDULE"
    }
  }


  project = "${var.project}"
}
