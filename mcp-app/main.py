# from mcp.server.fastmcp import FastMCP
# from fastapi import FastAPI
# from starlette.applications import Starlette
# from starlette.routing import Mount, Host
# import contextlib
#
# echo_mcp = FastMCP(name="EchoServer", stateless_http=True)
# math_mcp = FastMCP(name="MathServer", stateless_http=True)
#
#
# @echo_mcp.tool(description="A simple echo tool")
# def echo(message: str) -> str:
#     return f"Echo: {message}"
#
#
# @math_mcp.tool(description="A simple add tool")
# def add_two(n: int) -> int:
#     return n + 2
#
#
# # Create a combined lifespan to manage both session managers
# @contextlib.asynccontextmanager
# async def lifespan(app: FastAPI):
#     async with contextlib.AsyncExitStack() as stack:
#         await stack.enter_async_context(echo_mcp.session_manager.run())
#         await stack.enter_async_context(math_mcp.session_manager.run())
#         yield
#
#
# app = FastAPI(lifespan=lifespan)
# app.mount("/echo", echo_mcp.streamable_http_app())
# app.mount("/math", math_mcp.streamable_http_app())

from mcp.server.fastmcp import FastMCP
from fastapi import FastAPI
import contextlib

# 创建 MCP Agent
echo_mcp = FastMCP(name="EchoServer", stateless_http=True)

# 注册工具
@echo_mcp.tool(description="A simple echo tool")
def echo(message: str) -> str:
    return f"Echo: {message}"

# 生命周期管理
@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    async with contextlib.AsyncExitStack() as stack:
        await stack.enter_async_context(echo_mcp.session_manager.run())
        yield

# 创建 FastAPI 应用并挂载 MCP agent
app = FastAPI(lifespan=lifespan)


@app.get("/echo/health")
async def health_check():
    return {"status": "ok"}

from fastapi import Request

@app.post("/echo/test")
async def test_post(request: Request):
    data = await request.json()
    return {"received": data}


app.mount("/echo", echo_mcp.streamable_http_app())
