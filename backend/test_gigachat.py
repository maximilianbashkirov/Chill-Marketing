"""Test GigaChat API"""
import sys
sys.path.insert(0, '.')
import asyncio
from app.utils.llm_client import llm_client


async def test():
    try:
        result = await llm_client.chat_json(
            prompt='Say hello in Russian. Return JSON with field "message" containing greeting',
            system_prompt='You are a helpful assistant',
            temperature=0.3
        )
        print('GigaChat response:', result)
    except Exception as e:
        print('GigaChat error:', type(e).__name__, str(e))
        import traceback
        traceback.print_exc()


asyncio.run(test())
