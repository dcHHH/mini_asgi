from typing import Sequence

from src.routing import Route, Router
from src.types import Scope, Receive, Send


class MiniAsgi:
    def __init__(self, routes: Sequence[Route]):
        self.router = Router(routes)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        await self.router(scope, receive, send)
