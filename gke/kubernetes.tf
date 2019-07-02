########################
### Kubernetes Cluster
########################

resource "google_container_cluster" "casval-cluster" {
  addons_config {
    http_load_balancing {
      disabled = false
    }

    kubernetes_dashboard {
      disabled = true
    }

    network_policy_config {
      disabled = true
    }

    horizontal_pod_autoscaling {
      disabled = true
    }
  }

  cluster_ipv4_cidr       = "10.52.0.0/14"
  enable_kubernetes_alpha = false
  enable_legacy_abac      = false
  initial_node_count      = "1"
  remove_default_node_pool = true

  ip_allocation_policy {
    cluster_ipv4_cidr_block  = "10.52.0.0/14"
    services_ipv4_cidr_block = "10.56.0.0/20"
    use_ip_aliases           = true
  }

  location        = "asia-northeast1-a"
  logging_service = "none"

  master_auth {
    username               = "admin"
  }

  monitoring_service = "none"
  name               = "casval-cluster"
  network            = "${google_compute_network.casval-cluster-nat-network.name}"

  network_policy {
    enabled = false
  }

  master_authorized_networks_config {
    cidr_blocks {
      cidr_block   = "{YOUR_IP}"
      display_name = "Description"
    }
  }

  private_cluster_config {
    enable_private_endpoint = false
    enable_private_nodes    = true
    master_ipv4_cidr_block  = "172.16.0.0/28"
  }

  subnetwork = "${google_compute_subnetwork.casval-cluster-nat-subnetwork.self_link}"
  project = "${var.project}"
}


/*
output "client_certificate" {
  value = "${google_container_cluster.primary.master_auth.0.client_certificate}"
}

output "client_key" {
  value = "${google_container_cluster.primary.master_auth.0.client_key}"
}

output "cluster_ca_certificate" {
  value = "${google_container_cluster.primary.master_auth.0.cluster_ca_certificate}"
}
*/
