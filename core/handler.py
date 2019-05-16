from abc import ABCMeta
from abc import abstractmethod

from core.client import ClientException


class ScannerHandler(metaclass=ABCMeta):
    @abstractmethod
    def create(self, name: str):
        raise NotImplementedError()

    @abstractmethod
    def delete(self, name: str):
        raise NotImplementedError()

    @abstractmethod
    def ip(self):
        raise NotImplementedError()

    @abstractmethod
    def port(self):
        raise NotImplementedError()


class OpenVASHandler:
    def __init__(self, client, ip=None, port=None) -> None:
        self.client = client
        self.ip = None
        self.port = None
        self.container_image = "mikesplain/openvas:9"
        self.container_port = 9390

    def create(self, name: str):
        if self.container_image is None:
            # Not support VM
            self.client.create(name)
            return

        try:
            return self.client.create(name, self.container_image, self.container_port)
        except ClientException as e:
            raise DeployException(e)

    def delete(self, name: str):
        try:
            self.client.delete(name)
        except ClientException as e:
            raise DeleteException(e)

    @property
    def ip(self):
        return self.__ip

    @ip.setter
    def ip(self, ip):
        self.__ip = ip

    @property
    def port(self):
        return self.__port

    @port.setter
    def port(self, port):
        self.__port = port

    @property
    def container_image(self):
        return self.__container_image

    @container_image.setter
    def container_image(self, container_image):
        self.__container_image = container_image

    @property
    def container_port(self):
        return self.__container_port

    @container_port.setter
    def container_port(self, container_port):
        self.__container_port = container_port


class HandlerException(Exception):
    pass


class DeployException(HandlerException):
    pass


class DeleteException(HandlerException):
    pass
