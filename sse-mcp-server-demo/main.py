# sse_web_search.py
import httpx
import os

from mcp.server import FastMCP
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env
app = FastMCP('web-search', port=9000)


@app.tool()
async def web_search(query: str) -> str:
    """
    搜索互联网内容

    Args:
        query: 要搜索内容

    Returns:
        搜索结果的总结
    """
    api_key = os.getenv('BIGMODEL_API_KEY')
    async with httpx.AsyncClient() as client:
        response = await client.post(
            'https://open.bigmodel.cn/api/paas/v4/tools',
            headers={'Authorization': api_key},
            json={
                'tool': 'web-search-pro',
                'messages': [
                    {'role': 'user', 'content': query}
                ],
                'stream': False
            }
        )

        res_data = []
        for choice in response.json()['choices']:
            for message in choice['message']['tool_calls']:
                search_results = message.get('search_result')
                if not search_results:
                    continue
                for result in search_results:
                    res_data.append(result['content'])

        return '\n\n\n'.join(res_data)


@app.tool()
async def add(a: int, b: int) -> int:
    '''
    Add two numbers
    '''
    return a+b

if __name__ == "__main__":
    app.run(transport='sse')
