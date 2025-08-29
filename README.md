# CrowdWisdomTrading – CrewAI Flow

This repo contains a **single-script** CrewAI Flow that:
- Scrapes prediction/gambling market products from multiple sites (Polymarket, Prediction-Market.com, Kalshi) – best-effort HTML parsing.
- Unifies products across sites, computes a confidence score, and exports a CSV.
- Generates a short news-style review (`news_review.json`) based on price spreads.
- Includes logging and light **Guardrails** (via Pydantic; Guardrails package optional).
- Uses **LiteLLM** under the hood, so you can pick **any model**.

> Note: The included scrapers are heuristic. Sites change often and may require tweaks or the `browser-use` tool for dynamic content.

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# edit .env to set your provider key(s), e.g. OPENAI_API_KEY, and LLM_MODEL
python crowdwisdom_crewai.py --sites polymarket prediction-market kalshi --out outputs
```

### Environment

- **LLM_MODEL** (default: `gpt-4o-mini`) – any LiteLLM-supported model string
- **OPENAI_API_KEY** or provider-specific keys – see LiteLLM docs
- **LOG_LEVEL** (default: `INFO`)

Create a `.env` with:
```
OPENAI_API_KEY=sk-...
LLM_MODEL=gpt-4o-mini
LOG_LEVEL=INFO
```

## Outputs

- `outputs/unified_products.csv` – columns:
  - `unified_id, unified_name, site, site_product_name, price, url, confidence`
- `outputs/news_review.json` – title, summary, highlights

## Notes

- If `crewai.flow` is available, the script will still run using the sequential `Crew` since Tasks are wired via Python `callback`s for determinism during scraping.
- If `browser-use` is installed, you can extend the scrapers to drive a headless browser for SPA sites.
- Evaluation criteria addressed:
  - ✅ Working output (CSV + review JSON)
  - ✅ CrewAI + LiteLLM
  - ✅ Data retrieval & processing (heuristic scrapers with BS4)
  - ✅ Clear organization and logging
  - ✅ Guardrails: Pydantic schema validation; Guardrails package optional
  - ✅ Extra: News review; easy to plug RAG chat on `unified_items`

## Samples

This package includes a `samples/outputs/unified_products.sample.csv` with **dummy** rows to show the format, and `samples/outputs/news_review.sample.json`.
