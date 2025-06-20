### Prerequisites
1. create .env locally
2. add `OPENAI_API_KEY=sk...` in the .env. I use the Openai to implement my mcp client.
3. add model name like `MODEL_NAME=gpt-4` in the .env

### How to run
`uv run client.py`

#### Run SSE server
1. You should start a sse transport server locally or remote. Here's an example in "../sse-mcp-server-demo"
2. switch to `startup_sse_client()` in `client.py`

### Reference
1. https://github.com/liaokongVFX/MCP-Chinese-Getting-Started-Guide
2. https://modelcontextprotocol.io/quickstart/client