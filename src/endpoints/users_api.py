from typing import Any,Dict,Optional
import requests
from src.endpoints.base_endpoint import BaseEndpoint

class UsersAPI(BaseEndpoint):
    PATH="/users"

    def get_all(self,params:Optional[Dict[str,Any]]=None)->requests.Response:
        self.log.info("Fetching all users (params=%s)",params)
        return self.client.get(self.url(),params=params)

    def get_by_id(self,user_id:Any)->requests.Response:
        self.log.info("Fetching user_id=%s",user_id)
        return self.client.get(self.url(user_id))

    def search(self,**filters)->requests.Response:
        self.log.info("Searching users with %s",filters)
        return self.client.get(self.url(),params=filters)

    def create(self,payload:Dict[str,Any])->requests.Response:
        self.log.info("Creating user: %s",payload.get("username",payload))
        return self.client.post(self.url(),json=payload)

    def update(self,user_id:Any,payload:Dict[str,Any])->requests.Response:
        self.log.info("Replacing user id=%s",user_id)
        return self.client.put(self.url(user_id),json=payload)

    def partial_update(self,user_id:Any,payload:Dict[str,Any])->requests.Response:
        self.log.info("Patching user id=%s with %s",user_id,payload)
        return self.client.patch(self.url(user_id),json=payload)

    def delete(self,user_id:Any)->requests.Response:
        self.log.info("Deleting user id=%s",user_id)
        return self.client.delete(self.url(user_id))



