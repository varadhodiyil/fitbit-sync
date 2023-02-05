"""
App Web Server
"""
import os
from typing import Dict

from aiohttp import web
from aiohttp.web_response import json_response
from service.fit_bit import FitBit

fit_bit = FitBit(os.environ.get("CLIENT_ID"), os.environ.get("CLIENT_SECRET"))


class FitBitAuthHandler(web.View):
    """
    Fit Bit Token Handler Server
    """

    async def get(self) -> Dict:
        """
        Fetch Oauth Token & Refresh token Fom FitBit
        """
        token = await fit_bit.get_token(self.request.rel_url.query.get("code"))
        fit_bit.set_token(token["access_token"])
        fit_bit.set_refresh_token(token["refresh_token"])
        return json_response(token)


def create_app():
    """
    Init And run app
    """
    app = web.Application()
    app.router.add_routes([web.view("/api/auth", FitBitAuthHandler)])

    return app


def run_server():
    """
    Run server
    """
    app = create_app()

    web.run_app(app, port=8000)


if __name__ == "__main__":
    run_server()
