import json
from typing import Any, Dict

from src.types import Scope, Receive, Send


class Response:
    charset = "utf-8"

    def __init__(self, content: Any, status_code: int = 200, headers: Dict = None):
        self.status_code = status_code

        self.raw_headers = None

        self.body = self.render(content)
        self.init_headers(headers)

    def render(self, content: Any) -> bytes:
        return json.dumps(content).encode(self.charset)

    def init_headers(self, headers):
        self.raw_headers = [
            (b"content-length", str(len(self.body)).encode()),
            (b"content-type", b"application/json")
        ]

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        await send(
            {
                "type": "http.response.start",
                "status": self.status_code,
                "headers": self.raw_headers,
            }
        )
        await send({"type": "http.response.body", "body": self.body})

