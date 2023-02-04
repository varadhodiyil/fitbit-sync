"""
Base Class to Sync with Google Fit
"""
from abc import ABC, abstractmethod
from typing import Dict
from utils.api import API
from utils.mapper import Mapper


class DataSync(API, ABC):
    """
    Base class to Sync data to Google Fit
    """

    @property
    @abstractmethod
    def stream_name(self) -> str:
        """
        set's the stream
        """

    @property
    def data_type(self) -> str:
        """
        Return data type
        """
        return self.mapper.data_type_name

    @property
    @abstractmethod
    def mapper(self) -> Mapper:
        """
        Mapper clas
        """

    @property
    def base_url(self):
        """
        Base URL for Google auth
        """
        return "https://www.googleapis.com/fitness/v1/users/me"

    @property
    def headers(self):
        """
        Auth headers
        """
        return ""

    def __init__(self, step_one_route: str, step_two_route: str) -> None:
        self.step_one_route = step_one_route
        self.step_two_route = step_two_route

        super().__init__()

    def get_data_source(self) -> Dict:
        """
        Returns DataSource for Sync
        """
        return {
            "dataStreamName": self.stream_name,
            "type": "raw",
            "application": {"name": "FitBit Sync", "version": "1"},
            "dataType": {"name": self.data_type},
        }

    async def _step_one(self) -> str:
        """
        Step One
        """
        return (await self.post(self.step_one_route, self.get_data_source()))["id"]

    async def _step_two(self, source_id: str, data: Dict) -> Dict:
        """
        Stage 2
        """
        data = {"dataSourceId": source_id, "point": data}
        return await self.post(self.step_two_route, data)

    async def sync(self, data: Dict) -> Dict:
        """
        Sync data to Google Fit
        """

        source_id = await self._step_one()
        self.mapper.parse(data)
        data = self.mapper.validated_data
        return await self._step_two(source_id, data)
