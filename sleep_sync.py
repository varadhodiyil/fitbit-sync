"""
    Sleep Parser
"""

from enum import Enum
from typing import Dict
from datetime import timedelta

from dateutil.parser import parse
from utils.data_sync import DataSync

from utils.mapper import Mapper


class Sleep(Enum):
    """
    Enum to hold Sleep Activities
    """

    DEEP = 5
    LIGHT = 4
    REM = 6
    WAKE = 1
    ASLEEP = 2
    RESTLESS = 4


class SleepMapper(Mapper):
    """
    FitBit -> Google Fit Sleep Mapper
    """

    data_type_name = "com.google.sleep.segment"

    def _build_point(self, point: Dict):
        start_time = parse(point["dateTime"])
        end_time = start_time + timedelta(seconds=point["seconds"])
        return {
            "dataTypeName": self.data_type_name,
            "startTimeNanos": self.to_nano(start_time.timestamp()),
            "endTimeNanos": self.to_nano(end_time.timestamp()),
            "value": [{"intVal": Sleep[point["level"].upper()].value}],
        }

    def parse(self, data: Dict):
        """
        Parse Sleep Activities to Google Fit Format
        https://developers.google.com/fit/scenarios/write-sleep-data#rest
        """
        parsed = []
        for entry in data["sleep"]:
            for state in entry["levels"]["data"]:
                parsed.append(self._build_point(state))

        super().parse(parsed)


class SleepLogger(DataSync):
    """
    Logs Sleep data to Google Fit
    """

    mapper = SleepMapper()
    stream_name = "FitBit - Sleep Stream"

    def __init__(self) -> None:
        self.mapper = SleepMapper()
        self.stream_name = "FitBit - Sleep Stream"
        super().__init__("dataSources", "dataSources/dataSourceId/datasets/datasetId")

    async def sync(self, data: Dict) -> Dict:
        """
        Parse & Sync data to google Fit
        """
        return await super().sync(data)
