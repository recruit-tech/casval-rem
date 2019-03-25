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

    def on_push_message(self):
        return self.__on_push()

    def __on_push(self):
        # u mocking use k8s ip
        # return mock_address
        k8s = KubeDeploy()
        k8s.create_service()
        k8s.create_deployment()
        return k8s.get_service_ip_address()

    @staticmethod
    def delete_service(name, service_ip):
        k8s = KubeDeploy(service_ip)
        # ip_addrを取って渡す
        return k8s.delete_service(name)

    @staticmethod
    def delete_deployment(name, service_ip):
        k8s = KubeDeploy(service_ip)
        return k8s.delete_deployment(name)


class KubeDeploy(object):
    def __init__(self, service_ip="", namespace="default"):
        self.__service_ip = service_ip
        self.__namespace = namespace
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
            deployment_body = yaml.load(f)
            try:
                self.__k8s_core.create_namespaced_deployment(body=deployment_body, namespace=self.__namespace)
            except Exception as e:
                raise e

    def delete_deployment(self, name, namespace="default", **kwargs):
        body = client.V1DeleteOptions(**kwargs)
        resp = self.__k8s_beta.delete_namespaced_deployment(name, namespace, body, **kwargs)
        return resp

    def delete_all_deployment(self, namespace="default"):
        respd = self.__k8s_beta.delete_collection_namespaced_deployment(namespace)
        respr = self.__k8s_beta.delete_collection_namespaced_replica_set(namespace)
        respp = self.__k8s_core.delete_collection_namespaced_pod(namespace)

        return respd, respr, respp

    def create_service(self):
        with open(service_yaml_path) as f:
            service_body = yaml.load(f)
            try:
                resp = self.__k8s_core.create_namespaced_service(
                    body=service_body, namespace=self.__namespace
                )
                self.__service_ip = resp.status.load_balancer.ingress[0].ip
            except Exception as e:
                raise e

    def delete_service(self, name, namespace, **kwargs):
        resp = self.__k8s_core.delete_namespaced_service(name, namespace, **kwargs)
        return resp

    def get_ip_address(self):
        return self.service_ip

    def get_deployment_list(self):
        resp = self.__k8s_beta.list_deployment_for_all_namespaces()
        return resp
