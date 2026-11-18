# AI-Powered Website Link Analysis API

FastAPI service that fetches a public website, extracts visible content, and uses an LLM to return structured business, competitor, search-query, SEO, service, and audience insights.

## Features

- `POST /link-analysis` accepts a website URL.
- HTTPX + BeautifulSoup extraction of title, meta description, headings, visible text and links.
- Five structured analysis sections validated with Pydantic.
- Gemini structured JSON output; optional OpenAI provider.
- URL validation, DNS/IP checks, redirect re-validation, response-size and timeout limits.
- In-memory result cache.
- Swagger docs at `/docs`; health endpoint at `/health`.

## Important accuracy boundary

This project does not claim to measure Google/social search volume or rankings. It does not independently verify competitor facts. Without a search/research data provider, competitor entries are labelled `ai_suggested_unverified`; do not represent them as verified research. Services are labelled as found on the website or inferred. LLM outputs are recommendations and should be reviewed before business use.

## Setup

Python 3.11 or later is recommended.

```bash
git clone https://github.com/YOUR_USERNAME/ai-link-analysis.git
cd ai-link-analysis
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Add your API key to `.env`. For Gemini, create a key in Google AI Studio and set `GEMINI_API_KEY`. Do not commit `.env`.

Run:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 4000 --reload
```

Open http://localhost:4000/docs.

## Request

```bash
curl -X POST "http://localhost:4000/link-analysis" \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com"}'
```

## Response shape

The response contains:
- `brand`: extracted brand name, category and summary.
- `analysis.competitor_analysis`: business overview, competitor candidates, strengths and positioning opportunities.
- `analysis.target_search_queries`: exactly five queries with platforms, intent, relevance and audience.
- `analysis.seo_improvements`: primary/secondary/long-tail keywords, title, meta description and supporting content.
- `analysis.top_services`: exactly five service entries, each tagged as website-found or inferred.
- `analysis.target_audience`: primary/secondary audience, industries, business types, customer needs and segments.
- `extraction` and `llm`: extraction metadata, provider/model, latency and token usage when supplied by the provider.

The full response is dynamic and depends on the submitted website; no static sample is passed off as a real analysis.

## Provider selection

Default:
```env
LLM_PROVIDER=gemini
GEMINI_MODEL=gemini-3.7-flash
GEMINI_API_KEY=...
```

Optional OpenAI:
```env
LLM_PROVIDER=openai
OPENAI_MODEL=gpt-6-luna
OPENAI_API_KEY=...
```

The code uses a single provider per request. Select the provider/model after testing on a representative set of websites. The model name is configurable because provider model availability changes.

## LLM pricing comparison (USD, per 1M tokens)

Pricing checked against official provider pages on 18 Nov 2026. Prices can change; confirm before deployment.

| Provider / model | Input | Output | Notes |
|---|---:|---:|---|
| Google Gemini 3.7 Flash | $0.75 | $3.75 | Standard paid tier, listed through Dec 31 2026 |
| OpenAI GPT-6 Luna | $0.05 | $0.25 | Standard pricing shown on official pricing page |
| Anthropic Claude Haiku 5.5 | $0.10 | $0.50 | Prompt up to 100K tokens; official page currently lists promotional availability/pricing |

Official references:
- Google: https://ai.google.dev/gemini-api/docs/pricing
- OpenAI: https://developers.openai.com/api/docs/pricing
- Anthropic: https://platform.claude.com/docs/en/about-claude/pricing

**Recommendation:** Start with Gemini 3.7 Flash for its structured JSON mode and balanced capability, then benchmark it against GPT-6 Luna and Claude Haiku 5.5 on the same website set. This is an engineering recommendation, not a claim that it is the most accurate model. Pricing alone does not establish quality or latency.

### Illustrative cost estimate

Assume 8,000 input tokens and 2,000 output tokens per analysis (an estimate; measure actual provider usage). Approximate model cost:

| Model | Estimated cost / analysis |
|---|---:|
| Gemini 3.7 Flash | $0.0135 |
| GPT-6 Luna | $0.0009 |
| Claude Haiku 5.5 | $0.0018 |

Formula: `(input_tokens × input_price + output_tokens × output_price) / 1,000,000`.

These estimates exclude retries, caching, tools/search grounding, taxes and infrastructure. Actual token counts are returned in `llm` when available.

### Speed and accuracy methodology

Do not invent latency or accuracy numbers. Benchmark 20–50 representative sites (different industries, page sizes and languages), run each model at least three times, and record:
- p50/p95 end-to-end latency;
- schema-valid response rate;
- factual consistency against manually reviewed source evidence;
- competitor precision (verified only when supported by independent sources);
- cost per successful analysis.

## Security notes and production hardening

- Rejects non-HTTP(S), credentials, local/private/reserved IPs and non-standard ports.
- Redirect targets are validated and response size/time are limited.
- For production, place the service behind an outbound network policy/proxy that blocks private, loopback, link-local and cloud metadata ranges. DNS pre-checks alone cannot completely prevent DNS rebinding.
- Add persistent cache (Redis), rate limiting, authentication, structured logging, request IDs and monitoring before public high-volume use.
- Some websites block automated fetchers, require JavaScript, or expose only partial content. A fetch failure is reported instead of fabricating an analysis.
- Website content is untrusted input. The prompt explicitly treats it as data, not instructions.

## Tests

```bash
pytest -q
```

Tests cover basic health, request validation and unsafe URL cases. LLM integration tests require a configured API key and should be added to CI as mocked tests.

## Deploy on Render

1. Push this repository to a public GitHub repository.
2. In Render, create a new Web Service from the repository.
3. Render detects `render.yaml`; set `GEMINI_API_KEY` in the service environment.
4. Deploy and verify `/health`, `/docs`, and `POST /link-analysis`.
5. Submit the live base URL, endpoint URL and docs URL.

The service listens on Render's `$PORT`.

## Suggested next production improvements

- Add an independent search provider (e.g. a search API) to verify competitor candidates and attach source URLs.
- Add robots.txt policy checks and a clear crawl policy.
- Crawl selected same-domain service/about pages with strict page/depth limits.
- Add Redis caching and rate limiting.
- Add a benchmark dataset and quality evaluation report.
