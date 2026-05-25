import httpx
import asyncio
import json

async def test():
    async with httpx.AsyncClient(timeout=180.0) as client:
        resp = await client.post(
            'http://127.0.0.1:8000/api/v1/market-research/conduct',
            json={'topic': 'AI marketing', 'industry': 'technology'}
        )
        data = resp.json()
        research = data.get('data', {}).get('research', {})
        print(json.dumps(research, indent=2, ensure_ascii=False)[:2000])

asyncio.run(test())
