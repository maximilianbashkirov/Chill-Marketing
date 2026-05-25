"""Test improved LLM prompt"""
import sys
sys.path.insert(0, '.')
import asyncio
import json
from app.utils.llm_client import llm_client


async def test():
    prompt = """Conduct a market research on "digital marketing" (industry: technology). 
Use the data below and your knowledge. Return ONLY valid JSON without any additional text.

DATA:
- Russia GDP 2024: $2.17 trillion
- Russia Inflation 2024: 8.4%
- Academic research papers available on topic

Return EXACTLY this JSON structure with ALL fields filled:
{
  "statistics": {
    "market_size": "estimate in USD with source",
    "growth_rate": "growth rate percentage with timeframe",
    "key_players_count": "number of major players",
    "market_leaders": "comma-separated list of top companies",
    "regional_distribution": "breakdown by region"
  },
  "cases": [
    {
      "company": "company name",
      "challenge": "what challenge they faced",
      "solution": "how they solved it",
      "result": "measurable results",
      "timeframe": "when this happened",
      "budget": "budget range if known"
    }
  ],
  "strategies": [
    {
      "name": "strategy name",
      "description": "what it involves",
      "best_for": "who it suits",
      "implementation_steps": ["step1", "step2"],
      "expected_roi": "ROI estimate"
    }
  ],
  "examples": [
    {"type": "example type", "description": "what happened", "metrics": "results achieved"}
  ],
  "trends": ["trend 1", "trend 2", "trend 3"],
  "benchmarks": {
    "metric_name": "typical value",
    "another_metric": "another value"
  },
  "sources": ["source 1", "source 2"]
}"""

    result = await llm_client.chat_json(
        prompt=prompt,
        system_prompt="You are a market research expert. Return ONLY valid JSON with ALL fields. Never leave fields empty.",
        temperature=0.2
    )
    
    if 'error' in result:
        print('ERROR:', result.get('error'))
        print('Raw:', result.get('raw_response', '')[:500])
    else:
        print('KEYS:', list(result.keys()))
        for k in ['statistics', 'cases', 'strategies', 'examples', 'trends', 'benchmarks', 'sources']:
            v = result.get(k)
            if v:
                if isinstance(v, dict):
                    print(f'{k}: {json.dumps(v, indent=2, ensure_ascii=False)[:200]}')
                elif isinstance(v, list):
                    print(f'{k}: {len(v)} items')
                    if v:
                        print(f'  first: {json.dumps(v[0], ensure_ascii=False)[:100]}')
                else:
                    print(f'{k}: {v}')
            else:
                print(f'{k}: EMPTY')


asyncio.run(test())
