from aiohttp import web
from typing import Dict
from aiohttp.web_response import json_response


class AuthHandler(web.View):
    async def get(self) -> Dict:
        return json_response({"hello": "hello"})

    async def post(self) -> Dict:
        return json_response({"hello": "hi"})


def create_app():
    app = web.Application()
    app.router.add_routes([web.view("/api/auth", AuthHandler)])

    return app


def main():
    app = create_app()

    web.run_app(app)


if __name__ == "__main__":
    main()
