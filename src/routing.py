import asyncio
from typing import List, Sequence, Callable, Awaitable

from src.requests import Request
from src.responses import Response
from src.types import Scope, Receive, Send, ASGIApp


RequestResponseEndpoint = Callable[[Request], Awaitable[Response]]


def request_response(func: RequestResponseEndpoint) -> ASGIApp:
    is_coroutine = asyncio.iscoroutinefunction(func)
    if not is_coroutine:
        raise

    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        request = Request(scope, receive, send)
        response = await func(request)
        await response(scope, receive, send)

    return app


class Route:
    def __init__(
            self,
            path: str,
            endpoint: Callable,
            methods: List[str]
    ) -> None:
        assert path.startswith("/"), "Routed paths must start with '/'"
        self.path = path
        self.endpoint = endpoint

        self.app = request_response(self.endpoint)

        self.methods = set(method.upper() for method in methods)

    def matches(self, scope: Scope) -> bool:
        if scope["path"] == self.path:
            return True
        return False

    async def handle(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["method"] not in self.methods:
            response = Response("Method Not Allowed", status_code=405)
            await response(scope, receive, send)
        else:
            await self.app(scope, receive, send)


class Router:
    def __init__(self, routes: Sequence[Route]) -> None:
        self.routes = [] if routes is None else list(routes)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        for route in self.routes:
            match = route.matches(scope)
            if match:
                await route.handle(scope, receive, send)
                return

        response = Response("Not Found", status_code=404)
        await response(scope, receive, send)

