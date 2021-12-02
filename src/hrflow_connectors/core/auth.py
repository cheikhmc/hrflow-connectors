import requests
from typing import Union, Dict, Optional
from pydantic import BaseModel, validator


class Auth(BaseModel):
    def update(
        self,
        params: Union[Dict[str, str], None] = None,
        headers: Union[Dict[str, str], None] = None,
        payload: Union[Dict[str, str], None] = None,
        cookies: Union[Dict[str, str], None] = None,
    ):
        pass


class NoAuth(Auth):
    pass


class OAuth2PasswordCredentialsBody(Auth):
    access_token_url: str
    client_id: str
    client_secret: str
    username: str
    password: str

    access_token: Optional[str] = None

    def __init__(
        self,
        access_token_url: str,
        client_id: str,
        client_secret: str,
        username: str,
        password: str,
        *args,
        **kwargs,
    ):
        super().__init__(
            access_token_url=access_token_url,
            client_id=client_id,
            client_secret=client_secret,
            username=username,
            password=password,
            *args,
            **kwargs,
        )
        payload = dict()
        payload["grant_type"] = "password"
        payload["client_id"] = client_id
        payload["client_secret"] = client_secret
        payload["username"] = username
        payload["password"] = password

        response = requests.post(access_token_url, data=payload)
        if response.status_code != 200:
            raise ConnectionError(
                "OAuth2 failed ! Reason : `{}`".format(response.content)
            )
        self.access_token = response.json()["access_token"]


    def update(
        self,
        params: Union[Dict[str, str], None] = None,
        headers: Union[Dict[str, str], None] = None,
        payload: Union[Dict[str, str], None] = None,
        cookies: Union[Dict[str, str], None] = None,
    ):
        if headers is not None:
            headers.update({"Authorization": "OAuth {}".format(self.access_token)})
    