"""Test full market research service flow"""
import sys
sys.path.insert(0, '.')
import asyncio
import json
from collections import defaultdict
from app.utils.research_collector import research_collector
from app.utils.llm_client import llm_client


async def test():
    # 1. Collect data
    print('=== Phase 1: Collect data ===')
    data = await research_collector.collect_comprehensive_research_data('digital marketing trends', 'technology')
    print(f'World Bank: {len(data["world_bank"])} | Google Trends: {len(data["google_trends"])} | arXiv: {len(data["arxiv"])} | Reddit: {len(data["reddit"])}')
    
    # 2. Format data for LLM
    print('\n=== Phase 2: Format data context ===')
    wb = data['world_bank']
    stats_context = []
    for w in wb:
        indicator_names = {
            'NY.GDP.MKTP.CD': 'GDP (current US$)',
            'FP.CPI.TOTL.ZG': 'Inflation (annual %)',
            'SL.UEM.TOTL.ZS': 'Unemployment (% of total labor force)'
        }
        name = indicator_names.get(w['indicator'], w['indicator'])
        stats_context.append(f"  - {name}: {w['value']} ({w['country']}, {w['date']})")
    
    arxiv = data['arxiv']
    cases_context = []
    for p in arxiv[:3]:
        cases_context.append(f"  - {p['title']} ({p.get('published', '')[:4]})")
    
    context = f"""
COLLECTED DATA:
Statistics:
{chr(10).join(stats_context[:10])}

Research Papers:
{chr(10).join(cases_context)}

Google Trends:
{chr(10).join([f"  - {t}" for gt in data['google_trends'] for t in gt.get('trends', [])][:5])}
"""
    
    print(context[:500])
    
    # 3. Test LLM with this context
    print('\n=== Phase 3: Test LLM call ===')
    prompt = f"""Conduct a market research on "digital marketing trends" (industry: technology). 
Use the provided data and your knowledge. Return ONLY valid JSON.

DATA FOR ANALYSIS:
{context}

Return JSON with:
- statistics: {{market_size, growth_rate, key_players_count, market_leaders, regional_distribution}}
- cases: [{{company, challenge, solution, result, timeframe, budget}}]
- strategies: [{{name, description, best_for, implementation_steps, expected_roi}}]
- examples: [{{type, description}}]
- trends: [strings]
- benchmarks: {{metric: value}}
- sources: [strings]"""

    result = await llm_client.chat_json(
        prompt=prompt,
        system_prompt="You are a market research expert. Return ONLY valid JSON.",
        temperature=0.3
    )
    
    if 'error' in result:
        print('LLM ERROR:', result.get('error'))
        print('Raw:', result.get('raw_response', '')[:500])
    else:
        print('LLM OK! Keys:', list(result.keys()))
        print('Statistics:', json.dumps(result.get('statistics', {}), indent=2, ensure_ascii=False)[:300])
        print('Cases:', len(result.get('cases', [])))
        print('Trends:', len(result.get('trends', [])))


asyncio.run(test())
