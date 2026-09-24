from src.core.api_client import APIClient
from src.core.logger import get_logger

class BaseEndpoint:
    PATH:str=""

    def __init__(self,client:APIClient):
        self.client=client
        self.log=get_logger(self.__class__.__name__)

    def url(self,*parts)->str:
        segments=[str(p).strip("/") for p in parts if p is not None and p!=""]
        return "/".join([self.PATH.strip("/"),*segments]) if segments else self.PATH.strip("/")


