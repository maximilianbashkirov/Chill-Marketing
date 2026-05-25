"""Test market research module"""
import sys
sys.path.insert(0, '.')

import asyncio
from collections import defaultdict
from app.utils.research_collector import research_collector


async def test_collector():
    print('=== Testing research data collection ===')
    data = await research_collector.collect_comprehensive_research_data('digital marketing trends', 'technology')
    
    print(f'World Bank: {len(data.get("world_bank", []))} entries')
    print(f'Google Trends: {len(data.get("google_trends", []))} entries')
    print(f'arXiv: {len(data.get("arxiv", []))} papers')
    print(f'Reddit: {len(data.get("reddit", []))} posts')
    
    wb = data.get('world_bank', [])
    by_indicator = defaultdict(list)
    for w in wb:
        by_indicator[w['indicator']].append(w)
    
    indicator_names = {
        'NY.GDP.MKTP.CD': 'ВВП',
        'FP.CPI.TOTL.ZG': 'Инфляция',
        'SL.UEM.TOTL.ZS': 'Безработица'
    }
    
    for ind, entries in by_indicator.items():
        latest = sorted(entries, key=lambda x: x['date'], reverse=True)[0]
        print(f'  {indicator_names.get(ind, ind)}: {latest["value"]} ({latest["country"]}, {latest["date"]})')
    
    return data


if __name__ == '__main__':
    data = asyncio.run(test_collector())
    print()
    print('=== Collector test PASSED ===')
