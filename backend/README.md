# Product Intelligence Engine — Backend

Django REST API that powers the Product Intelligence Platform — a system for searching live web sources, extracting structured product data, and generating comparison insights.

## Architecture

The backend is organized around a modular, provider-abstracted pipeline:

```
Search Provider  →  Crawling  →  Markdown Storage  →  Parser Agent  →  Structured JSON
(Firecrawl/Exa)     (Firecrawl)    (SQLite/PostgreSQL)    (Gemini LLM)     (Unified Schema)
```

### Provider Abstraction

All external services implement abstract interfaces defined in `search/providers/base.py`:

- **`SearchProvider`** — Web search (currently Firecrawl)
- **`CrawlerProvider`** — Page content extraction
- **`LLMProvider`** — Structured generation (currently Gemini)

New providers can be swapped in via environment config without touching pipeline code.

## Tech Stack

- **Django 5+** — Web framework
- **Django REST Framework** — API layer
- **SQLite** (dev) / **PostgreSQL** (production)
- **Pydantic** — Typed data models for provider interfaces
- **Celery + Redis** — Background task processing

## Project Structure

```
backend/
├── config/
│   ├── settings.py          # Django configuration
│   ├── urls.py              # Root URL routing
│   ├── asgi.py              # ASGI entry point
│   └── wsgi.py              # WSGI entry point
├── search/
│   ├── models.py            # DB models: SearchQuery, SearchResult, RawMarkdown, ParsedProduct
│   ├── views.py             # API endpoints
│   ├── serializers.py       # DRF serializers
│   ├── services.py          # Search pipeline orchestrator
│   ├── urls.py              # Search app routes
│   ├── admin.py             # Django admin configuration
│   ├── providers/
│   │   ├── base.py          # Abstract provider interfaces + shared Pydantic models
│   │   ├── firecrawl.py     # FirecrawlSearchProvider implementation
│   │   ├── gemini.py        # GeminiProvider (LLM) implementation
│   │   └── registry.py      # Provider factory functions
│   └── agents/
│       └── parser.py        # ParserAgent — extracts structured JSON from markdown via LLM
├── tests/
│   └── test_fc.py           # Integration tests
├── manage.py                # Django CLI
└── .env                     # Environment variables
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/search/` | Execute a product search |
| `GET`  | `/api/search/<uuid>/` | Retrieve a specific search with all results |
| `GET`  | `/api/search/history/` | List last 20 searches |

### POST `/api/search/`

```json
{
  "query": "RTX 5070",
  "num_sites": 5
}
```

Returns the full `SearchQuery` object with nested results, raw markdown, and parsed product data.

## Data Pipeline

1. **SearchQuery** — User's query is persisted immediately with `pending` status
2. **Search Provider** — Queries Firecrawl's `/v1/search`, deduplicates by domain
3. **Crawling** — Concurrently scrapes each unique URL via Firecrawl's `/v1/scrape`
4. **RawMarkdown** — Stores the extracted markdown content per result
5. **Parser Agent** — (Phase 2) Sends markdown to Gemini for structured JSON extraction
6. **ParsedProduct** — Stores the structured product JSON

All intermediate results are persisted — nothing is discarded.

## Database Models

- **`SearchQuery`** — User search with status tracking (`pending` → `searching` → `crawling` → `parsing` → `completed`/`failed`)
- **`SearchResult`** — Individual URL result linked to a search
- **`RawMarkdown`** — Extracted page content, one-to-one with SearchResult
- **`ParsedProduct`** — Structured JSON output from the Parser Agent

## Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys (FIRECRAWL_API_KEY, GEMINI_API_KEY)

# Run migrations
python manage.py migrate

# Start dev server
python manage.py runserver
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | dev key | Django secret key |
| `DEBUG` | `True` | Debug mode |
| `SEARCH_PROVIDER` | `firecrawl` | Active search provider |
| `FIRECRAWL_API_KEY` | — | Firecrawl API key |
| `LLM_PROVIDER` | `gemini` | Active LLM provider |
| `GEMINI_API_KEY` | — | Gemini API key |

## Phases

- **Phase 1** — Search + Crawl + Markdown storage ✅
- **Phase 2** — Parser Agent (structured JSON extraction) ✅
- **Phase 3+** — Specification normalization, comparison engine, recommendations, user features
