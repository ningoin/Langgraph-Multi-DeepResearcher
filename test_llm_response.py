#!/usr/bin/env python3

import sys
import os
sys.path.append('src')

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from ollama_deep_researcher.utils import tavily_search, deduplicate_and_format_sources, clean_html_content
from ollama_deep_researcher.graph import summarize_sources
from ollama_deep_researcher.state import SummaryState
from ollama_deep_researcher.configuration import Configuration

# Test the complete pipeline
print("Testing complete pipeline...")

# 1. Search
search_results = tavily_search("人工智能发展趋势", max_results=1, fetch_full_page=True)
print(f"Search results type: {type(search_results)}")

# 2. Format sources
formatted_sources = deduplicate_and_format_sources(search_results, 1000, fetch_full_page=True)
print(f"Formatted sources length: {len(formatted_sources)}")

# 3. Create state
state = SummaryState(
    research_topic="人工智能发展趋势",
    web_research_results=[formatted_sources],
    running_summary=None
)

# 4. Test summarization
config = {"configurable": {}}
result = summarize_sources(state, config)
print(f"Summary type: {type(result)}")
print(f"Summary keys: {result.keys() if isinstance(result, dict) else 'Not a dict'}")

if isinstance(result, dict) and "running_summary" in result:
    summary = result["running_summary"]
    print(f"Summary length: {len(summary)}")
    print(f"First 500 chars of summary:")
    print(repr(summary[:500]))
    
    # Check if HTML is present
    if "<!DOCTYPE html>" in summary:
        print("\n❌ HTML DOCTYPE found in summary!")
    elif "<html" in summary:
        print("\n❌ HTML tags found in summary!")
    else:
        print("\n✅ No HTML tags found in summary")
