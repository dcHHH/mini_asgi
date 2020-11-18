from src.applications import MiniAsgi
from src.requests import Request
from src.responses import Response
from src.routing import Route


async def hello(requests: Request):
    return Response("hello world")


async def the(requests: Request):
    return Response("the world")

r1 = Route("/hello", hello, ["GET", "POST"])
r2 = Route("/the", the, ["GET", "POST"])

app = MiniAsgi([r1, r2])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8080)
