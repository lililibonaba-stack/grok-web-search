# grok-web-search (Hermes Agent skill)

This is a custom Grok search skill built for Hermes. It leverages Grok’s powerful search engine — a capability that is not available through any public API. 
The skill supports real‑time web search with source links, and it can scrape and read the content of any URL it encounters. As a result,
search results are based on the actual content displayed on the pages, rather than solely on information stored in the model’s memory. 
It is particularly effective at retrieving the latest information from social media platforms such as X (formerly Twitter) or Reddit.

## When to use

- Built-in `web_search` results look stale, thin, or off-topic
- The question needs fresh, real-time grounding (news, prices, recent releases)
- You want search + page reading + summarization in a single call

Not for: bulk structured SERP data (use built-in search), full page text extraction (use an extract
tool), or anything where an LLM summarizing between you and the sources is unacceptable — output is
prose findings, not raw results.

## Install

Copy this folder into your Hermes skills directory:

```
<hermes-home>/skills/research/grok-web-search/
├── SKILL.md
└── scripts/
    └── grok_search.py
```

- Windows: `%LOCALAPPDATA%\hermes\skills\research\grok-web-search\`
- Linux / macOS: `~/.hermes/skills/research/grok-web-search/`

No secrets are stored in the skill files — the API key always lives in the environment.

## Setup

1. Get a cheapapis.net API key (looks like `apikey_...`) at https://cheapapis.net
   Get an API key from [cheapapis.net](https://cheapapis.net); see the repo's [get_apikey_tutorial.md](https://github.com/lililibonaba-stack/grok-search-mcp/blob/main/get_apikey_tutorial.md) for how to create one.
3. Export it as `CHEAPAPIS_API_KEY`, e.g. add to the Hermes `.env`
   (`~/.hermes/.env` on Linux/macOS, `%LOCALAPPDATA%\hermes\.env` on Windows):

   ```
   CHEAPAPIS_API_KEY=apikey_...
   ```

   Hermes loads `.env` into the session environment automatically.
4. Dependencies: Python 3 with `httpx` (`pip install httpx`). A `curl`-only fallback is documented
   in SKILL.md.

## Usage

Ask the agent to search — it runs:

```bash
python "<skills>/research/grok-web-search/scripts/grok_search.py" "your query here"
```

curl equivalent (same request the script makes):

```bash
source ~/.hermes/.env
curl -s --max-time 420 https://cheapapis.net/v1/chat/completions \
  -H "Authorization: Bearer $CHEAPAPIS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"grok-4.5-search","messages":[{"role":"user","content":"QUERY"}]}' \
  | python -c "import sys,json;print(json.load(sys.stdin)['choices'][0]['message']['content'])"
```

## Notes

- Real-time search can take 30–120 s; the script's HTTP timeout is 420 s (7 min). Don't kill it
  at 30 s and conclude it's broken.
- If your environment sets `ALL_PROXY` to a `socks5://` URL, httpx requires the `socksio` package
  (`pip install "httpx[socks]"`) or you can unset `ALL_PROXY` — `HTTP_PROXY`/`HTTPS_PROXY` alone
  work fine.
- Respect upstream rate limits: batch questions into one well-formed query.

## License

MIT. Upstream: [grok-search-mcp](https://github.com/lililibonaba-stack/grok-search-mcp) by the same author.
