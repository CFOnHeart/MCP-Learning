from fastapi import FastAPI, Request
from pydantic import BaseModel
import uvicorn
import asyncio
from clients.sse_client import SseMCPClient

fast_api = FastAPI()
mcp_client = SseMCPClient("http://127.0.0.1:9000/sse")

class QueryRequest(BaseModel):
    query: str

@fast_api.on_event("startup")
async def startup_event():
    await mcp_client.connect_to_sse_server()

@fast_api.on_event("shutdown")
async def shutdown_event():
    await mcp_client.cleanup()

@fast_api.get("/query")
async def handle_query(query: str):
    try:
        response = await mcp_client.process_query(query)
        return {"response": response}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run("app:fast_api", host="0.0.0.0", port=8000, reload=True)
