"""
Base Class with utils for data conversion
"""
from abc import abstractmethod, ABC
from typing import Dict
import json


class Mapper(ABC):
    """
    Base Class For converting FitBit datapoints to Google Fit
    """

    validated_data = {}

    @property
    @abstractmethod
    def data_type_name(self):
        """
        Entity's repr in Googe Fit
        """

    def to_nano(self, date_time: int) -> int:
        """
        Epoch to Nano Secs
        """
        return int(date_time * int(1e9))

    @abstractmethod
    def parse(self, data: dict) -> Dict:
        """
        Base Parser for FitBit -> Google Fit
        """
        self.validated_data = data

    def __repr__(self) -> str:
        return json.dumps(self.validated_data, indent=4)
