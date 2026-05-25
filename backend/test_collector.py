"""Debug: test what research_collector actually returns and how merge works"""
import asyncio
import json
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.utils.research_collector import research_collector
from app.services.market_research.service import MarketResearchService

async def test():
    # Step 1: collect raw data
    raw = await research_collector.collect_comprehensive_research_data("digital marketing trends", "technology")
    print("=== RAW DATA KEYS ===")
    for k, v in raw.items():
        if isinstance(v, list):
            print(f"  {k}: list of {len(v)} items")
        else:
            print(f"  {k}: {v}")
    
    wb = raw.get("world_bank", [])
    print(f"\n=== WORLD BANK ({len(wb)} entries) ===")
    for w in wb[:5]:
        print(f"  indicator={w.get('indicator')}, value={w.get('value')}, date={w.get('date')}")
    
    # Step 2: manually process like service does
    indicator_names = {
        "NY.GDP.MKTP.CD": ("GDP (current US$)", "market_size"),
        "FP.CPI.TOTL.ZG": ("Inflation (annual %)", "growth_rate"),
        "SL.UEM.TOTL.ZS": ("Unemployment (% of total labor force)", "unemployment_rate")
    }
    
    by_indicator = {}
    for w in wb:
        ind = w.get("indicator", "")
        if ind and w.get("value") is not None:
            date = w.get("date", "")
            if ind not in by_indicator or (date and date > by_indicator[ind]["date"]):
                by_indicator[ind] = w
    
    print(f"\n=== BY INDICATOR ({len(by_indicator)} indicators) ===")
    for ind, entry in sorted(by_indicator.items()):
        name, fb_key = indicator_names.get(ind, (ind, ind.lower().replace(".", "_")))
        print(f"  {ind} -> fb_key='{fb_key}', value={entry['value']}")
    
    # Step 3: Now test the LLM response vs collected stats merge
    # Simulate what the LLM might return
    llm_stats = {
        "market_size": "data not available",
        "growth_rate": "data not available",
        "key_players_count": "data not available",
        "market_leaders": "data not available",
        "regional_distribution": "data not available"
    }
    
    # collected stats from the actual data
    stats_dict = {}
    for ind, entry in sorted(by_indicator.items()):
        name, fb_key = indicator_names.get(ind, (ind, ind.lower().replace(".", "_")))
        val = entry["value"]
        stats_dict[fb_key] = str(val)
    
    print(f"\n=== COLLECTED STATS DICT ===")
    for k, v in stats_dict.items():
        print(f"  {k}: {v}")
    
    print(f"\n=== MERGE TEST ===")
    for k, v in stats_dict.items():
        if k not in llm_stats:
            print(f"  {k}: NOT IN llm_stats")
        else:
            current = llm_stats.get(k)
            is_empty = not current or current in ("data not available", "", None)
            print(f"  {k}: current={current!r}, is_empty={is_empty}")
            if is_empty:
                print(f"    -> WOULD REPLACE with {v}")

asyncio.run(test())
