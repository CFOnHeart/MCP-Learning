import asyncio
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from pathlib import Path
import openai
import os
import json
from dotenv import load_dotenv

load_dotenv()  # load environment variables from .env


class MCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        openai.api_key = os.getenv("OPENAI_API_KEY")
        self.openai_model = os.getenv("MODEL_NAME")

    async def connect_to_server(self, command: str, args: list[str]):
        """Connect to an MCP servers

        Args:
            :param command: command to run the servers script ["uv"]
            :param args: args for running servers script e.g., ["run", "server.py"]
        """
        # e.g., uv run servers.py
        server_params = StdioServerParameters(
            command=command,
            args=args,
            env=None
        )

        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))

        await self.session.initialize()

        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to servers with tools:", [tool.name for tool in tools])

    async def process_query(self, query: str) -> str:
        """Process a query using openai and available tools"""
        messages = [
            {
                "role": "user",
                "content": query
            }
        ]

        response = await self.session.list_tools()

        available_tools = [{
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema
            }
        } for tool in response.tools]

        # Initial Claude API call
        response = openai.chat.completions.create(
            model=self.openai_model,
            max_tokens=1000,
            messages=messages,
            tools=available_tools
        )

        # Process response and handle tool calls
        content = response.choices[0]
        if content.finish_reason == "tool_calls":
            tool_call = content.message.tool_calls[0]
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)

            result = await self.session.call_tool(tool_name, tool_args)
            print(f"\n\n[Calling tool {tool_name} with args {tool_args}]\n\n")
            print(f"\n\n[Tool Response]: {result.content[0].text}\n\n")
            messages.append(content.message.model_dump())
            messages.append({
                "role": "tool",
                "content": result.content[0].text,
                "tool_call_id": tool_call.id,
            })
            response = openai.chat.completions.create(
                model=self.openai_model,
                messages=messages,
            )
            return response.choices[0].message.content

        return content.message.content

    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() == 'quit':
                    break

                response = await self.process_query(query)
                print("\n" + response)

            except Exception as e:
                print(f"\nError: {str(e)}")

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()

async def startup_stdio_client():
    client = MCPClient()
    try:
        await client.connect_to_server("uv", ["run", "../servers/math_server.py"])
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    import sys
    asyncio.run(startup_stdio_client())