from flask import Flask, render_template, request, Response, jsonify
import openai
import time
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env
app = Flask(__name__)
# 设置你的 OpenAI API 密钥
openai.api_key = os.getenv("OPENAI_API_KEY")  # 推荐使用环境变量管理

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

    # 新版 openai 包的用法
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=conversation_history,
        stream=True
    )

    def event_stream():
        try:
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta and getattr(chunk.choices[0].delta, "content", None):
                    content = chunk.choices[0].delta.content
                    yield f"data: {content}\n\n"
                    time.sleep(0.01)
        except Exception as e:
            yield f"data: [ERROR] {str(e)}\n\n"

    return Response(event_stream(), mimetype='text/event-stream')

@app.route('/reset', methods=['POST'])
def reset():
    global conversation_history
    conversation_history = []
    return jsonify({'status': 'reset'})

if __name__ == '__main__':
    app.run(debug=True, threaded=True)
