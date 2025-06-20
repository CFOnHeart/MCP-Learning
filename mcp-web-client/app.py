from flask import Flask, render_template, request, Response, jsonify
import openai
import time
import os
import asyncio
from dotenv import load_dotenv

from clients.mcp_client import MCPClient
from clients.config import MCPClientConfig, MCPServerConfig, LLMClientConfig, LLMRequestConfig

load_dotenv()
app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

# 初始化 MCPClient（同步方式，Flask 推荐）
def init_mcp_client():
    server_path = os.path.join(os.path.dirname(__file__), "servers", "math_server.py")
    server_name = "calculator"
    client = MCPClient(
        MCPClientConfig(
            mcpServers={
                server_name: MCPServerConfig(
                    command="uv",
                    args=["run", server_path],
                )
            }
        ),
        LLMClientConfig(
            api_key=os.getenv("API_KEY"),
            base_url=os.environ["BASE_URL"],
        ),
        LLMRequestConfig(
            model=os.environ["MODEL_NAME"],
        ),
    )
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(client.connect_to_server(server_name))
    return client

mcp_client = init_mcp_client()

# MCP 上下文管理（简单实现）
conversation_history = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send', methods=['POST'])
def send():
    user_message = request.json.get('message')
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    # 添加用户消息到上下文
    conversation_history.append({"role": "user", "content": user_message})

    def event_stream():
        # 1. 先用 MCP 工具处理，流式返回
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            mcp_messages = loop.run_until_complete(
                mcp_client.process_messages(conversation_history.copy())
            )
            mcp_result = mcp_messages[-1]["content"]
            yield f"data: [MCP Tool] {mcp_result}\n\n"
            time.sleep(0.1)
        except Exception as e:
            yield f"data: [MCP ERROR] {str(e)}\n\n"

        # 2. 再用 OpenAI 继续流式返回
        try:
            response = openai.chat.completions.create(
                model="gpt-4",
                messages=conversation_history,
                stream=True
            )
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta and getattr(chunk.choices[0].delta, "content", None):
                    content = chunk.choices[0].delta.content
                    yield f"data: {content}\n\n"
                    time.sleep(0.01)
        except Exception as e:
            yield f"data: [OpenAI ERROR] {str(e)}\n\n"

    return Response(event_stream(), mimetype='text/event-stream')

@app.route('/reset', methods=['POST'])
def reset():
    global conversation_history
    conversation_history = []
    return jsonify({'status': 'reset'})

if __name__ == '__main__':
    app.run(debug=True, threaded=True)
