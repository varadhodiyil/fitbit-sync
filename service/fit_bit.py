"""
"""
from base64 import b64encode
from datetime import datetime
import random
import string
from typing import Dict, List
from asyncio import run
import webbrowser

from authlib.integrations.httpx_client import AsyncOAuth2Client

from utils.api import API


class FitBit(API):

    """
    FitBit API interactor
    """

    _base_url = "https://api.fitbit.com"
    token = None
    user_id = None
    refresh_token = None

    @property
    def base_url(self):
        return self._base_url

    @property
    def headers(self):
        return {"Authorization": f"Bearer {self.token}"}

    code_verifier = None

    def __init__(self, client_id: str, client_secret: str) -> None:

        self.client_id = client_id
        self.client_secret = client_secret
        super().__init__()

        self.oauth = AsyncOAuth2Client(
            self.client_id,
            code_challenge_method="S256",
            response_type="code",
        )

    def init_oauth_session(self, scope=None) -> None:
        """
        Fetch token from FitBit
        """
        scope = scope or [
            "activity",
            "nutrition",
            "heartrate",
            "location",
            "nutrition",
            "profile",
            "settings",
            "sleep",
            "social",
            "weight",
        ]
        self.code_verifier = self.gen_code_verifer()
        url, _ = self.oauth.create_authorization_url(
            "https://www.fitbit.com/oauth2/authorize",
            code_verifier=self.code_verifier,
            scope=scope,
        )
        print(url)
        webbrowser.open(url)

    def gen_code_verifer(self, length: int = 50) -> str:
        """
        Generate `N` length code token
        """
        return "".join(
            random.SystemRandom().choice(string.ascii_uppercase + string.digits)
            for _ in range(length)
        )

    async def get_token(self, auth_code: str) -> str:
        """
        Fetch OAuth token
        """
        header_auth = f"{self.client_id}:{self.client_secret}".encode()
        header_auth = b64encode(header_auth).decode()

        return await self.oauth.fetch_token(
            url="https://api.fitbit.com/oauth2/token",
            code_verifier=self.code_verifier,
            response_type="code",
            grant_type="authorization_code",
            client_id=self.client_id,
            code=auth_code,
            method="POST",
            headers={"Authorization": f"Basic {header_auth}"},
        )

    def set_refresh_token(self, refresh_token) -> None:
        """
        Set Refresh token
        """
        self.refresh_token = refresh_token

    def set_token(self, token: str) -> None:
        """
        Set Access token
        """
        self.token = token

    def set_user_id(self, user_id: str) -> None:
        """
        User ID for Fitbit
        """
        self.user_id = user_id

    async def get_activities(self) -> List[Dict]:
        """
        Get Activitis logged in FitBit
        https://dev.fitbit.com/build/reference/web-api/activity/get-activity-log-list/
        """
        return await self.get(
            f"1/user/{self.user_id}/activities/list.json",
            params={
                "beforeDate": datetime.utcnow().strftime("%Y-%m-%d"),
                "sort": "desc",
                "limit": 100,
                "offset": 0,
            },
        )

    async def get_zone_minutes(
        self, date=datetime.today(), interval="1min"
    ) -> List[Dict]:
        """
        Zone Minutes for given day / interval
        https://dev.fitbit.com/build/reference/web-api/intraday/get-azm-intraday-by-date/
        """
        return await self.get(
            f"1/user/-/activities/active-zone-minutes/date/{date}/1d/{interval}.json"
        )

    async def get_sleep_log(self, date: str) -> Dict:
        """ "
        Sleep Log
        https://dev.fitbit.com/build/reference/web-api/sleep/get-sleep-log-by-date/
        """

        return await self.get(f"1.2/user/-/sleep/date/{date}.json")

    async def get_heart_rate(self, date: str, period: str = "1d"):
        """
        Heart rate
        https://dev.fitbit.com/build/reference/web-api/heartrate-timeseries/get-heartrate-timeseries-by-date/
        """

        return await self.get(
            f"/1/user/[user-id]/activities/heart/date/{date}/{period}.json"
        )
