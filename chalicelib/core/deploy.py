from kubernetes import client
from kubernetes import config

import os

base_path = os.path.abspath("..")


class Deploy(object):
    def __init__(self, target_host=None, target_name=None):
        self.host = target_host
        self.name = target_name

    def on_push_message(self):
        return self.__on_push()

    def __on_push(self, target):
        # u mocking use k8s ip
        # return mock_address
        k8s = KubeDeploy()
        k8s.create_service(target)
        k8s.create_deployment(target)
        return k8s.get_service_ip_address()

    @staticmethod
    def delete_service(name):
        k8s = KubeDeploy()
        # ip_addrを取って渡す
        return k8s.delete_service(name)

    @staticmethod
    def delete_deployment(name):
        k8s = KubeDeploy()
        return k8s.delete_deployment(name)


class KubeDeploy(object):
    def __init__(self, k8s_ip="", namespace="default"):
        self.__service_ip = ""
        self.__namespace = namespace
        # get k8s ip(use env value)
        self.k8s_ip = k8s_ip
        config.load_kube_config(os.path.join(base_path, ".kube/config"))

        # make api instance
        self.__k8s_core = client.CoreV1Api()
        self.__k8s_beta = client.ExtensionsV1beta1Api()

    def create_deployment(self, target=""):
        deployment_body = {
            "apiVersion": "apps/v1beta2",
            "kind": "Deployment",
            "metadata": {
                "name": f"{target}_deployment",
                "labels": {"app.kubernetes.io/name": f"{target}_deployment"},
            },
            "spec": {
                "replicas": 1,
                "selector": {
                    "matchLabels": {
                        "app.kubernetes.io/name": "casval_openvas",
                        "app.kubernetes.io/instance": "casval_openvas",
                        "role": "casval_openvas",
                    }
                },
                "template": {
                    "metadata": {
                        "labels": {
                            "app.kubernetes.io/name": "casval_openvas",
                            "app.kubernetes.io/instance": "casval",
                            "role": "casval_openvas",
                        }
                    },
                    "spec": {
                        "containers": [
                            {
                                "name": "openvas",
                                "image": "mikesplain/openvas:9",
                                "imagePullPolicy": "Always",
                                "ports": [
                                    {"name": f"{target}_omp", "containerPort": 9390, "protocol": "TCP"},
                                    {"name": f"{target}_http", "containerPort": 443, "protocol": "TCP"},
                                ],
                            }
                        ]
                    },
                },
            },
        }
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

    def create_service(self, target=""):
        service_body = {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": f"{target}_service",
                "labels": {"app.kubernetes.io/name": f"{target}_service"},
            },
            "spec": {
                "type": "NodePort",
                "ports": [
                    {"name": "omp", "port": 9390, "targetPort": 9390, "protocol": "TCP", "nodePort": 30000}
                ],
                "selector": {"app.kubernetes.io/name": f"{target}_deployment"},
            },
        }
        try:
            resp = self.__k8s_core.create_namespaced_service(body=service_body, namespace=self.__namespace)
            self.__service_ip = resp.status.load_balancer.ingress[0].ip
        except Exception as e:
            raise e

    def delete_service(self, name, namespace="default", **kwargs):
        resp = self.__k8s_core.delete_namespaced_service(name, namespace, **kwargs)
        return resp

    def get_ip_address(self):
        return self.service_ip

    def get_deployment_list(self):
        resp = self.__k8s_beta.list_deployment_for_all_namespaces()
        return resp
