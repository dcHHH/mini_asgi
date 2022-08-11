from typing import Sequence

from src.routing import Route, Router
from src.types import Scope, Receive, Send


class MiniAsgi:
    def __init__(self, routes: Sequence[Route] = None):
        routes = routes or []
        self.router = Router(routes)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        await self.router(scope, receive, send)

    def get(self, path):
        return self.route(path, ["GET"])

    def post(self, path):
        return self.route(path, ["POST"])

    def route(self, path, methods):
        return self.router.add_route(path, methods)
