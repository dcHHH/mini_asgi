from src import MiniAsgi, Request, Response, Route

# v0
async def app(scope, receive, send):
    await send({
        "type": "http.response.start",
        "status": 200
    })
    await send({
        "type": "http.response.body",
        "body": b"hello world"
    })

# # v1
# async def hello(requests: Request):
#     return Response("hello world")
#
#
# async def the(requests: Request):
#     return Response("the world")
#
# r1 = Route("/hello", hello, ["GET", "POST"])
# r2 = Route("/the", the, ["GET", "POST"])

# app = MiniAsgi([r1, r2])


# # v2
# app = MiniAsgi()
#
#
# @app.post("/hello")
# async def hello(request: Request):
#     input_data = await request.json()
#     name = input_data.get('name')
#     return Response(f'Hello, {name}!')
#
#
# @app.get("/")
# async def the(request: Request):
#     return Response("hello world")

# # v3
# app = MiniAsgi()
#
#
# @app.post("/hello")
# async def hello(name):
#     return f'Hello, {name}!'
#
#
# @app.get("/")
# async def the():
#     return "hello world"
#
#
# @app.route("/hi", methods=["post", "get"])
# async def the(name):
#     return f"hi {name}"
#
#
# # v4
# @app.route("/bonjour/{name}", methods=["post", "get"])
# async def the(name):
#     return f"hi {name}"


# run_in_threadpool


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8080)


