---
name: grok-web-search
description: "Use when built-in web_search is weak; real-time Grok search."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [search, grok, web-search, research, cheapapis]
    related_skills: [grounded-citations, arxiv]
---

# Grok Web Search (grok-4.5-search via cheapapis.net)

## Overview

Port of https://github.com/lililibonaba-stack/grok-search-mcp (MIT) as a skill. Instead of
a fastmcp server exposing one tool, this is a plain script the agent runs from the terminal.

The upstream tool posts the query to cheapapis.net's OpenAI-compatible chat completions
endpoint with `model: "grok-4.5-search"`. That model has server-side real-time web search
(not available via any public Grok API) and returns grounded findings with source links; it
can also read the content of URLs it encounters, so answers reflect what pages actually say
rather than model memory.

Use it when:
- Built-in `web_search` results look stale, thin, or off-topic
- The question needs fresh, real-time grounding (news, prices, recent releases)
- You want one call that both searches and reads pages, returning a digested answer
  with source links

Don't use for:
- Bulk structured SERP data (use built-in `web_search`, which returns url/title/description)
- Extracting full page text (use built-in `web_extract`)
- Anything where you can't tolerate an LLM summarizing between you and the sources —
  this returns prose findings, not raw results

## Setup

Requires only: Python 3 with `httpx` (or just `curl`), and a cheapapis.net API key
(get one at https://cheapapis.net). The skill folder contains no secrets — the key
always lives in the environment, never in these files.

Standard setup on any machine — export the key as `CHEAPAPIS_API_KEY`, e.g. add to
Hermes `.env` (`~/.hermes/.env` on Linux/macOS, `%LOCALAPPDATA%\hermes\.env` on Windows):

```
CHEAPAPIS_API_KEY=apikey_...
```

Hermes loads `.env` into the session environment automatically, so scripts run from
the terminal already see it.

Host-specific note (this Windows machine): the key here is stored under a different
name, `HERMES_CUSTOM_CHEAPAPIS_NET_API_KEY`, in `$LOCALAPPDATA/hermes/.env`. Map it
before running:

```bash
export $(grep -E '^HERMES_CUSTOM_CHEAPAPIS_NET_API_KEY=' "$LOCALAPPDATA/hermes/.env" | xargs)
export CHEAPAPIS_API_KEY="$HERMES_CUSTOM_CHEAPAPIS_NET_API_KEY"
```

Dependencies: `httpx` only. Installed in the miniconda Python (user site-packages,
2026-09-05). If a fresh machine lacks it, fall back to `curl` (see below) — do not
pip install into the Hermes venv.

## Usage

Script is at `scripts/grok_search.py` inside this skill directory:

```bash
python "$HOME/.hermes/skills/research/grok-web-search/scripts/grok_search.py" "your query here"
```

curl equivalent, same request the script makes:

```bash
source ~/.hermes/.env
curl -s --max-time 120 https://cheapapis.net/v1/chat/completions \
  -H "Authorization: Bearer $CHEAPAPIS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"grok-4.5-search","messages":[{"role":"user","content":"QUERY"}]}' \
  | python -c "import sys,json;print(json.load(sys.stdin)['choices'][0]['message']['content'])"
```

Completion criteria: stdout contains non-empty findings text. An empty body or an
`Error:`/`HTTP error` prefix means failure — check the key, then retry once; if the
endpoint itself is down, fall back to built-in `web_search` and say so in your answer.

## Common Pitfalls

1. **API key not set or wrong prefix.** Keys look like `apikey_...`. A missing key makes
   the script return `Error: CHEAPAPIS_API_KEY is not set.` — check `.env` first.
2. **Slow endpoint.** Real-time search can take 30–120 s; the script's HTTP timeout
   is 420 s (7 min), so pass a generous `--max-time` (curl, ≥420) or tool timeout
   (≥480 s) to cover the script's full window. Don't kill it at 30 s and conclude it's broken.
3. **Env sourcing.** Hermes `.env` lines are `KEY=value`; `source` it before curl in the
   same shell invocation. In MSYS/git-bash on Windows, use `$HOME/.hermes/.env`.
4. **Network egress.** This host sometimes can't reach raw.githubusercontent.com but may
   still reach cheapapis.net; if curl hangs, test the endpoint before blaming the key.
5. **ALL_PROXY breaks httpx.** The Hermes `.env` sets `ALL_PROXY=socks5://127.0.0.1:7897`,
   and httpx then fails with "the 'socksio' package is not installed". Fix (either):
   `unset ALL_PROXY all_proxy` before running the script (HTTP_PROXY/HTTPS_PROXY still
   work for httpx), or `pip install --user "httpx[socks]"`.
6. **Output is prose, not data.** Don't pipe it into JSON parsers downstream; treat it as
   an already-digested briefing and cite the source links it contains.
7. **Respect upstream rate limits** — one query per question. Batch questions into one
   well-formed query instead of firing five calls.

## Verification Checklist

- [ ] Key exported: `HERMES_CUSTOM_CHEAPAPIS_NET_API_KEY` from `$LOCALAPPDATA/hermes/.env` → `CHEAPAPIS_API_KEY`
- [ ] Script path resolved (`$HOME/.hermes/skills/research/grok-web-search/scripts/grok_search.py`)
- [ ] First real query returned non-empty text with (ideally) source links
- [ ] On failure: retried once, then fell back to built-in `web_search` and disclosed it

## One-Shot Recipes

Fresh release check: `grok_search.py "latest stable version of X and what changed vs previous release, with links"`
News sweep: `grok_search.py "summarize today's news about TOPIC, top 5 items with dates and source links"`
