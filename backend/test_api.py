"""Test market-research API on port 8000"""
import httpx
import asyncio
import json


async def test():
    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(
            'http://127.0.0.1:8000/api/v1/market-research/conduct',
            json={'topic': 'digital marketing trends', 'industry': 'technology'}
        )
        print('Status:', resp.status_code)
        if resp.status_code != 200:
            print('Error:', resp.text[:500])
            return

        result = resp.json()
        research = result.get('data', {}).get('research', {})

        print('\n=== STATISTICS ===')
        for k, v in research.get('statistics', {}).items():
            print(f'  {k}: {v}')

        print(f'\n=== CASES ({len(research.get("cases", []))}) ===')
        for c in research.get('cases', [])[:3]:
            print(f'  - {c.get("company", "")}: {c.get("result", "")[:60]}')

        print(f'\n=== TRENDS ({len(research.get("trends", []))}) ===')
        for t in research.get('trends', [])[:3]:
            print(f'  - {t}')

        print(f'\n=== STRATEGIES ({len(research.get("strategies", []))}) ===')
        for s in research.get('strategies', [])[:2]:
            print(f'  - {s.get("name", "")}: {s.get("description", "")[:60]}')

        print(f'\n=== SOURCES ===')
        print(f'  {research.get("sources", [])}')

        print('\n=== TEST PASSED ===')


asyncio.run(test())
