# Product Intelligence Engine — Frontend

Interactive dashboard for the Product Intelligence Platform — a dark-mode, single-page application for searching live product data across multiple websites and viewing structured insights.

## Architecture

A **Next.js 16** single-page app with a real-time animated pipeline visualization.

```
User Query → POST /api/search/ → Django Backend → Live Pipeline Status → Results Display
  (SearchBar)                     (API Client)                      (PipelineVisualizer → ResultsPanel → SiteCards)
```

## Tech Stack

- **Next.js 16.2.9** — React meta-framework
- **React 19** — UI library
- **TailwindCSS v4** — Utility-first styling
- **Framer Motion** — Animations and transitions
- **TanStack Query** — Server state management
- **Lucide React** — Icon library
- **TypeScript** — Type safety

## Project Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx          # Root layout — dark mode, Inter font, Providers wrapper
│   │   ├── page.tsx            # Home page — search orchestration + pipeline + results
│   │   └── globals.css         # Global styles — dark design system + component styles
│   ├── components/
│   │   ├── SearchBar.tsx       # Search input + websites counter (1-10)
│   │   ├── PipelineVisualizer.tsx  # Animated 4-step progress indicator
│   │   ├── ResultsPanel.tsx    # Results summary + site card grid
│   │   ├── SiteCard.tsx        # Expandable card — product JSON + raw markdown
│   │   └── Providers.tsx       # TanStack Query provider wrapper
│   ├── lib/
│   │   └── api.ts              # API client — POST search, GET detail, GET history
│   └── types/
│       └── search.ts           # TypeScript types mirroring Django API responses
├── public/
├── next.config.ts
├── package.json
└── .env.local
```

## Key Features

- **SearchBar** — Text input with configurable website count (1–10 sites)
- **PipelineVisualizer** — Real-time animated step indicator: Searching → Crawling → Parsing → Done
- **SiteCard** — Expandable card per search result with:
  - Title, domain, content preview, rank position
  - Toggle to view **Extracted Product Data** (structured JSON)
  - Toggle to view **Raw Scraped Content** (markdown)
- **Dark mode** — Full dark theme via CSS custom properties
- **Responsive** — Adapts layout for mobile and desktop

## API Client (`src/lib/api.ts`)

| Function | Method | Endpoint |
|----------|--------|----------|
| `searchProducts()` | `POST` | `/api/search/` |
| `getSearchDetail()` | `GET` | `/api/search/<id>/` |
| `getSearchHistory()` | `GET` | `/api/search/history/` |

Configure the API base URL via `NEXT_PUBLIC_API_URL` in `.env.local` (default: `http://localhost:8000`).

## Phases

- **Phase 1** — Live Product Search: search bar, pipeline visualization, site cards, markdown viewer ✅
- **Phase 2+** — Product cards with structured data, comparison tables, price charts, recommendation panel, search history, saved comparisons

## Getting Started

```bash
npm install
npm run dev
# or
bun install
bun dev
```

Open [http://localhost:3000](http://localhost:3000) — the backend must be running on port 8000.
