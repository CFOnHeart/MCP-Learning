import os
import random

import pytest
from dotenv import load_dotenv
from pathlib import Path

from clients.mcp_client import MCPClient
from clients.config import (
    MCPClientConfig,
    MCPServerConfig,
    LLMRequestConfig,
    LLMClientConfig,
)

load_dotenv()
async def client():
    server_path = Path(__file__).parent / "../servers/math_server.py"
    server_name = "calculator"
    client = MCPClient(
        MCPClientConfig(
            mcpServers={
                server_name: MCPServerConfig(
                    command="uv",
                    args=["run", str(server_path)],
                )
            }
        ),
        LLMClientConfig(
            api_key=os.getenv("API_KEY"),
            base_url=os.environ["BASE_URL"],
        ),
        LLMRequestConfig(
            model=os.environ["MODEL_NAME"],
            # seed=42,
        ),
    )

    await client.connect_to_server(server_name)
    return client

import asyncio

async def main():
    llm_client = await client()
    messages = [{"role": "user", "content": "What is 2 + 2?"}]
    messages = await llm_client.process_messages(messages)
    print(messages[-1]["content"])

asyncio.run(main())
