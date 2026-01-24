# Product Intelligence Engine

AI-powered platform for searching live product data across multiple sources and presenting structured insights. See [`context.md`](context.md) for full vision and phased roadmap.

## Architecture

```
Next.js Frontend  ──HTTP──>  Django REST API  ──>  Search Providers (Firecrawl)
                                   │
                              Parser Agent (Gemini)
                                   │
                         SQLite / PostgreSQL
```

Everything is provider-abstracted — search, crawling, and LLM providers can be swapped via environment config.

## Repo Structure

```
├── backend/          # Django API — see backend/README.md
├── frontend/         # Next.js UI — see frontend/README.md
├── firecrawl.js      # Demo script (standalone Firecrawl API call, for reference only)
├── Makefile          # Quick-start commands
├── context.md        # Project vision, architecture, phases
└── .gitignore
```

## Quick Start

```bash
# Start both backend and frontend
make

# Or individually:
make backend    # python manage.py runserver (port 8000)
make frontend   # npm run dev (port 3000)
```

### Backend Setup

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # Add FIRECRAWL_API_KEY, GEMINI_API_KEY
python manage.py migrate
python manage.py runserver
```

### Frontend Setup

```bash
cd frontend
npm install
# or: bun install
npm run dev
```

Set `NEXT_PUBLIC_API_URL` in `.env.local` if the backend runs on a different port.

## More Details

- **Backend** → [`backend/README.md`](backend/README.md) — API endpoints, data pipeline, models, provider abstraction
- **Frontend** → [`frontend/README.md`](frontend/README.md) — Components, state flow, API client
- **Vision** → [`context.md`](context.md) — architecture decisions, 15-phase roadmap, product schema, engineering goals
- **Demo** → [`firecrawl.js`](firecrawl.js) — standalone Firecrawl search/scrape prototype (not part of the main app)
