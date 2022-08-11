import json
from typing import AsyncGenerator, Any, Dict

from src.types import Scope, Receive, Send


class HTTPConnection:
    def __init__(self, scope: Scope) -> None:
        self.scope = scope

        self._header = None
        self._query_params = None
        self._path_params = None

    @property
    def header(self) -> Dict[str, str]:
        if self._header is None:
            self._header = {
                k.decode(): v.decode()
                for k, v in self.scope["header"]
            }
        return self._header

    @property
    def query_params(self) -> dict:
        if self._query_params is None:
            self._query_params = {}
            for i in self.scope["query_string"].decode().split('&'):
                if i:
                    k, v = i.split("=", 1)
                    self._query_params[k] = v

        return self._query_params

    @property
    def path_params(self) -> dict:
        return self.scope.get("path_params", {})


class Request(HTTPConnection):
    def __init__(self, scope: Scope, receive: Receive, send: Send) -> None:
        super().__init__(scope)

        self.receive = receive
        self.send = send

        self._stream_consumed = False
        self._body = None
        self._json = None

    async def stream(self) -> AsyncGenerator[bytes, None]:
        if self._body is not None:
            yield self._body
            yield b""
            return

        if self._stream_consumed:
            raise RuntimeError("Stream consumed")

        self._stream_consumed = True
        while True:
            message = await self.receive()
            if message["type"] == "http.request":
                body = message.get("body", b"")
                if body:
                    yield body
                if not message.get("more_body", False):
                    break
        yield b""

    async def body(self) -> bytes:
        if self._body is None:
            chunks = [chunk async for chunk in self.stream()]
            self._body = b"".join(chunks)
        return self._body

    async def json(self) -> Any:
        if self._json is None:
            body = await self.body()
            self._json = json.loads(body)
        return self._json
