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

# Test the complete pipeline
print("Testing complete pipeline...")

# 1. Search
search_results = tavily_search("人工智能发展趋势", max_results=1, fetch_full_page=True)
print(f"Search results type: {type(search_results)}")
print(f"Search results keys: {search_results.keys() if isinstance(search_results, dict) else 'Not a dict'}")

# 2. Format sources
formatted_sources = deduplicate_and_format_sources(search_results, 1000, fetch_full_page=True)
print(f"\nFormatted sources type: {type(formatted_sources)}")
print(f"Formatted sources length: {len(formatted_sources)}")
print(f"First 500 chars of formatted sources:")
print(repr(formatted_sources[:500]))

# 3. Check if HTML is present
if "<!DOCTYPE html>" in formatted_sources:
    print("\n❌ HTML DOCTYPE found in formatted sources!")
elif "<html" in formatted_sources:
    print("\n❌ HTML tags found in formatted sources!")
else:
    print("\n✅ No HTML tags found in formatted sources")

# 4. Test cleaning
cleaned_sources = clean_html_content(formatted_sources)
if "<!DOCTYPE html>" in cleaned_sources:
    print("\n❌ HTML DOCTYPE found in cleaned sources!")
elif "<html" in cleaned_sources:
    print("\n❌ HTML tags found in cleaned sources!")
else:
    print("\n✅ No HTML tags found in cleaned sources")
