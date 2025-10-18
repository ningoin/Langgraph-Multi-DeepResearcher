#!/usr/bin/env python3

import sys
import os
sys.path.append('src')

from ollama_deep_researcher.utils import clean_html_content

# Test HTML cleaning
test_html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <link rel="icon" href="/logo.png" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>云雾 API </title>
</head>
<body>
  <div id="root">这是实际内容</div>
</body>
</html>"""

print("Original HTML:")
print(repr(test_html))
print("\nCleaned content:")
cleaned = clean_html_content(test_html)
print(repr(cleaned))
print("\nCleaned content (formatted):")
print(cleaned)
