### First Creaetd this project
1. uv init sse-mcp-server-demo 
2. cd sse-mcp-server-demo
3. uv venv
4. .venv\Scripts\activate
5. uv add mcp[cli] httpx
6. uv run ./main.py

### How to run this project
1. .venv\Scripts\activate
2. uv run ./main.py
3. Add the following configuration into your mcp client settings. e.g., VS Code Agent
```json
"mcp": {
    "servers": {
        "sse-local-demo": {
        "url": "http://127.0.0.1:9000/sse"
        }
    }
}
```
4. Open the MCP client in VSCode, and you should see the SSE server is connected.
5. Send a message to the agent, and the agent will select the tool for you.
![](./images/sse_server_vscode_copilot.png)

## References
- [MCP Server for developers](https://modelcontextprotocol.io/quickstart/server)
- [MCP-Chinese-Getting-Started-Guide
](https://github.com/liaokongVFX/MCP-Chinese-Getting-Started-Guide)