from abc import ABC, abstractmethod
from typing import Dict, Optional
from aiohttp import ClientSession, client_exceptions

from utils.singelton import Singleton


class InvalidException(Exception):
    """
    Raise Invalid Exception when response is not 2XX
    """

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class AuthInvalid(Exception):
    """
    Raised when Auth is rejected by the API
    """


class API(ABC, metaclass=Singleton):

    """
    API connection class
    """

    def __init__(self) -> None:
        self.session = None

    @property
    @abstractmethod
    def base_url(self):
        """
        BASE url for endpoint
        """

    @property
    @abstractmethod
    def headers(self):
        """
        Set Headers
        """

    def get_session(self) -> ClientSession:
        """
        Returns Session if already init or creates one
        """
        if self.session is None or self.session.closed:
            self.session = ClientSession(headers=self.headers)
        return self.session

    async def get(
        self, path: Optional[str] = None, params: Optional[Dict] = None
    ) -> Dict:
        """
        GET Request
        """
        path = f"{self.base_url}/{path}" if path else self.base_url
        session = self.get_session()
        print(self.headers)
        async with session.get(path, params=params) as resp:
            if resp.status != 200:
                try:
                    body = await resp.json()
                except client_exceptions.ContentTypeError:
                    body = await resp.text()
                if resp.status == 401:
                    raise AuthInvalid(f"Failed with code {resp.status} and body {body}")
                raise InvalidException(
                    f"Failed with code {resp.status} and body {body}"
                )
            return await resp.json()

    async def post(self, path: str, data: Dict) -> Dict:
        """
        POST request
        """
        session = self.get_session()
        path = f"{self.base_url}/{path}"
        async with session.post(url=path, json=data) as resp:
            if resp.status == 200:
                return await resp.json()
            code = resp.status
            data = await resp.json()
            raise InvalidException(
                f"Failed to fetch {path} code: {code} with data: {data}"
            )

    async def delete(self, path: str, data: Optional[Dict] = None) -> Dict:
        """
        DELETE request
        """
        session = self.get_session()
        async with session.delete(url=f"{self.base_url}/{path}", json=data) as resp:
            return await resp.json()
