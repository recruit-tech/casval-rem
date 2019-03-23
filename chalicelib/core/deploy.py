from kubernetes import client

import os
import yaml

base_path = os.path.abspath("..")
deployment_yaml_path = base_path + "/k8s_config/openvas_deployment.yaml"
service_yaml_path = base_path + "/k8s_config/openvas_service.yaml"

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
        # return mock_address
        k8s = KubeDeployer()
        k8s.create_deployment()
        return k8s.get_ip_address()


class KubeDeployer(object):
    def __init__(self):
        self.pod_ip = ""

        # get k8s ip(use env value)
        self.k8s_ip = ""
        self.configuration = client.Configuration()

        self.configuration.api_key["authorization"] = "<bearer_token>"
        self.configuration.api_key_prefix["authorization"] = "Bearer"

        self.configuration.host = "https://" + self.k8s_ip

        self.configuration.ssl_ca_cert = "<path_to_cluster_ca_certificate>"
        # make api instance

        self.__k8s_core = client.CoreV1Api(client.ApiClient(self.configuration))
        self.__k8s_beta = client.ExtensionsV1beta1Api(client.ApiClient(self.configuration))

    def create_deployment(self):
        # use make yaml deployment
        with open(deployment_yaml_path) as f:
            deploy_body = yaml.load(f)
            try:
                req = self.____k8s_beta.create_namespaced_deployment(body=deploy_body, namespace="casval")
                self.pod_ip = req.status.pod_ip
            except Exception as e:
                raise e

    def delete_deployment(self, name, namespace="casval", **kwargs):
        body = client.V1DeleteOptions(**kwargs)
        resp = self.__k8s_beta.delete_namespaced_deployment(name, namespace, body, **kwargs)
        return resp

    def delete_all_deployment(self, namespace="casval"):
        respd = self.__k8s_beta.delete_collection_namespaced_deployment(namespace)
        respr = self.__k8s_beta.delete_collection_namespaced_replica_set(namespace)
        respp = self.__k8s_core.delete_collection_namespaced_pod(namespace)

        return respd, respr, respp

    def create_service(self, namespace="casval"):
        with open(service_yaml_path) as f:
            svc = yaml.load(f)
            try:
                resp = self.__k8s_core.create_namespaced_service(body=svc, namespace=namespace)
                return resp
            except Exception as e:
                raise e

    def get_ip_address(self):
        return self.pod_ip

    def get_deployment_list(self):
        resp = self.__k8s_beta.list_deployment_for_all_namespaces()
        return resp
