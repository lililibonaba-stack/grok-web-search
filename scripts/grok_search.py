#!/usr/bin/env python3
"""Grok real-time web search via cheapapis.net OpenAI-compatible endpoint.

Ported from https://github.com/lililibonaba-stack/grok-search-mcp (MIT).
Usage: python grok_search.py "query text"

Reads CHEAPAPIS_API_KEY from the environment (Hermes .env is loaded by the
session, or source it manually before calling).
"""
import json
import os
import sys

import httpx

API_URL = "https://cheapapis.net/v1/chat/completions"
MODEL = "grok-4.5-search"
TIMEOUT = 420.0  # 7 minutes — endpoint can be slow (30-120s observed, allow headroom)


def search_by_grok(query: str) -> str:
    """Search the live web with grok-4.5-search; returns findings with links."""
    api_key = os.environ.get("CHEAPAPIS_API_KEY")
    if not api_key:
        return "Error: CHEAPAPIS_API_KEY is not set."

    try:
        resp = httpx.post(
            API_URL,
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": MODEL,
                "messages": [{"role": "user", "content": query}],
            },
            timeout=TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]
    except httpx.HTTPStatusError as e:
        return f"HTTP error {e.response.status_code}: {e.response.text[:500]}"
    except (KeyError, IndexError):
        return f"Unexpected response structure: {json.dumps(data)[:500]}"
    except Exception as e:
        return f"Search failed: {e}"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python grok_search.py \"query\"")
        sys.exit(1)
    print(search_by_grok(" ".join(sys.argv[1:])))
