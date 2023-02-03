"""
    Sleep Parser
"""
import json
from enum import Enum
from typing import Dict
from datetime import timedelta

from dateutil.parser import parse

from utils.mapper import Mapper
from utils.api import API


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

    def parse(self, source_id: str, data: Dict):
        """
        Parse Sleep Activities to Google Fit Format
        https://developers.google.com/fit/scenarios/write-sleep-data#rest
        """
        parsed = []
        for entry in data["sleep"]:
            for state in entry["levels"]["data"]:
                parsed.append(self._build_point(state))

        return super().parse(source_id, {"dataSourceId": source_id, "point": parsed})

    def get_datasource(self, stream_name: str) -> Dict:

        return {
            "dataStreamName": stream_name,
            "type": "raw",
            "application": {
                "name": "FitBit Sync",
                "version": "1"
            },
            "dataType": {
                "name": "com.google.sleep.segment"
            }
        }


class SleepLogger(API):

    def __init__(self) -> None:
        self.parser = SleepMapper()

    async def step_one(self, name: str) -> str:

        params = self.parser.get_datasource(name)

    async def log_me(self, data) -> None:
        """
        """


if __name__ == "__main__":
    with open("sleep.json", encoding="utf-8") as r:

        _data = json.load(r)

    print(SleepMapper().parse("112", _data))
