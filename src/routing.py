from inspect import iscoroutinefunction
from typing import List, Sequence, Callable, Awaitable, Tuple

from src.requests import Request
from src.responses import Response
from src.types import Scope, Receive, Send, ASGIApp
from src.utils import compile_path

RequestResponseEndpoint = Callable[[Request], Awaitable[Response]]
Endpoint = Callable


def request_response(func: RequestResponseEndpoint) -> ASGIApp:
    is_coroutine = iscoroutinefunction(func)
    if not is_coroutine:
        raise

    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        request = Request(scope, receive, send)
        response = await func(request)
        await response(scope, receive, send)

    return app


def get_request_handler(func: Endpoint) -> ASGIApp:
    is_coroutine = iscoroutinefunction(func)
    if not is_coroutine:
        raise

    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        request = Request(scope, receive, send)

        body = {}
        body_bytes = await request.body()
        if body_bytes:
            body = await request.json()

        query_params = request.query_params
        path_params = request.path_params
        body.update(query_params)
        body.update(path_params)

        raw_response = await func(**body)

        response = Response(raw_response)

        await response(scope, receive, send)

    return app


class Route:
    def __init__(
            self,
            path: str,
            endpoint: Endpoint,
            methods: List[str] = None
    ) -> None:
        assert path.startswith("/"), "Routed paths must start with '/'"
        self.path = path
        self.endpoint = endpoint

        # self.app = request_response(self.endpoint)
        self.app = get_request_handler(self.endpoint)

        if not methods:
            self.methods = ["GET"]
        else:
            self.methods = set(method.upper() for method in methods)

        self.path_regex, self.path_format, self.param_convertors = compile_path(path)

    def matches(self, scope: Scope) -> Tuple[bool, Scope]:
        # if self.path == scope["path"]:
        #     return True
        match = self.path_regex.match(scope["path"])
        if match:
            matched_params = match.groupdict()
            for key, value in matched_params.items():
                matched_params[key] = self.param_convertors[key].convert(value)
            child_scope = {"path_params": matched_params}
            return True, child_scope
        return False, {}

    async def handle(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["method"] not in self.methods:
            response = Response("Method Not Allowed", status_code=405)
            await response(scope, receive, send)
        else:
            await self.app(scope, receive, send)


class Router:
    def __init__(self, routes: Sequence[Route] = None) -> None:
        self.routes = routes or []

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        for route in self.routes:
            match, child_scope = route.matches(scope)
            if match:
                scope.update(child_scope)
                await route.handle(scope, receive, send)
                return

        response = Response("Not Found", status_code=404)
        await response(scope, receive, send)

    def add_route(self, path, method):
        def decorator(func):
            route = Route(path, func, method)
            self.routes.append(route)
            return func

        return decorator
