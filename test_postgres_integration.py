#!/usr/bin/env python3
"""
Quick test of PostgreSQL integration by calling ai_agent.py directly
"""

import subprocess
import sys

test_queries = [
    "What computer science courses do I need for UC Berkeley?",
    "What math courses do I need for UC Davis?",
    "What science courses do I need for UC San Diego?",
]

print("=== Testing PostgreSQL Integration ===\n")

for i, query in enumerate(test_queries, 1):
    print(f"Test {i}: {query}")
    print("-" * 60)
    
    result = subprocess.run(
        [sys.executable, "backend/ai_agent.py", query],
        capture_output=True,
        text=True,
        cwd="."
    )
    
    # Filter out stderr (logs) and only show stdout (response)
    if result.stdout:
        print(result.stdout)
    
    if result.returncode != 0:
        print(f"❌ Error: {result.stderr}")
    else:
        print("✅ Success\n")

print("=== All Tests Complete ===")
