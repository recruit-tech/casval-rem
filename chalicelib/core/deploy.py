from kubernetes import client

import os
import yaml

path = os.path.abspath("..")
yaml_path = path + "/deployment_rep/openvas.yaml"

mock_address = "10.0.0.1"


class Deploy(object):
    def __init__(self, target_host=None, target_name=None):
        self.host = target_host
        self.name = target_name
        self.host = self.__on_push()

    def on_push_message(self):
        return self.host

    def __on_push(self):
        # u mocking use k8s ip
        return mock_address
        # k8s = K8sModel()
        # k8s.make_pod()
        # return k8s.get_ip_address()


class K8sModel(object):
    def __init__(self):
        self.pod_ip = ""
        self.k8s_ip = ""

    def make_deployment(self):
        configuration = client.Configuration()

        configuration.api_key["authorization"] = "<bearer_token>"
        configuration.api_key_prefix["authorization"] = "Bearer"

        configuration.host = "https://" + self.k8s_ip

        configuration.ssl_ca_cert = "<path_to_cluster_ca_certificate>"

        # make api instance
        client.CoreV1Api(client.ApiClient(configuration))

        deploy_api = client.ExtensionsV1beta1Api(client.ApiClient(configuration))

        # use make yaml deployment
        with open(yaml_path) as f:
            deploy_body = yaml.load(f)
            try:
                req = deploy_api.create_namespaced_deployment(body=deploy_body, namespace="casval-rem")
                self.pod_ip = req.status.pod_ip
            except Exception as e:
                raise e

    def get_ip_address(self):
        return self.pod_ip
