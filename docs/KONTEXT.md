# KONTEXT — Chill Marketing AI Bot

**Дата:** 22.05.2026
**Версия:** 1.0.0

---

## Goal

Build and maintain "Chill Marketing AI Bot" — an intelligent marketing decision support system using LLM (GigaChat API). Covers 70–90% of marketer functions: idea analytics, content analysis, market research, SMI monitoring, marketing model selection, and a community feed.

## Constraints & Preferences

- **Backend:** Python 3.12, FastAPI, SQLAlchemy 2.0 + Pydantic v2, SQLite (dev), GigaChat API
- **Frontend:** React 18, TypeScript, Vite 5, MUI 5, Redux Toolkit, React Router v6, Framer Motion
- **Schema migrations:** inline in `main.py` (`create_tables()` + ALTER TABLE) — no Alembic for MVP
- **Git:** repo has no `.git` (not a git repo)
- **All modules must have fallback data** when LLM is unavailable
- **SQLite** stores naive datetimes; all timezone conversion code must handle `.tzinfo is None`

---

## Project Structure

```
D:\Папки Пользователя\Кодинг\Python\TEST-main\chill-marketing-ai-bot\
├── backend/
│   ├── app/
│   │   ├── api/           # analytics, content, smi, market_research, dot_analysis, help_colleague, trends
│   │   ├── database/      # engine, SessionLocal, get_db()
│   │   ├── models/        # SQLAlchemy models + Pydantic v2 schemas (pydantic_models.py)
│   │   ├── services/      # Business logic per module (analytics/, content/, smi/, ...)
│   │   ├── utils/         # llm_client.py, marketing_models.py, rss_fetcher.py, vector_store.py, ...
│   │   ├── config.py      # Pydantic BaseSettings from .env
│   │   ├── main.py        # FastAPI app, CORS, routers, create_tables()
│   │   └── celery.py      # Celery (optional, not actively used)
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── public/vite.svg     # CM gradient favicon
│   ├── src/
│   │   ├── components/     # Layout.tsx (sidebar, appbar, drawer, notifications, profile menu), SettingsDialog.tsx
│   │   ├── contexts/       # ThemeContext.tsx (light/dark mode, localStorage)
│   │   ├── pages/          # Dashboard, AnalyticsPage, ContentPage, SMIPage, MarketResearchPage,
│   │   │                   # DotAnalysisPage, HelpColleaguePage, HelpColleagueDetailPage, HelpColleagueProfilePage
│   │   ├── services/       # Axios API clients per module
│   │   ├── store/          # Redux store + slices (analytics, content, helpColleague, ...)
│   │   ├── App.tsx         # React Router v6 routes
│   │   ├── main.tsx        # Entry: Redux Provider → ThemeContext → MUI ThemeProvider (dynamic) → BrowserRouter
│   │   └── index.css
│   ├── nginx.conf          # Production: SPA fallback + /api proxy_pass
│   ├── vite.config.ts      # Dev: proxy /api → localhost:8005 (recently changed from 8000→8003→8000→8005)
│   ├── Dockerfile          # Multi-stage: node:20 build → nginx serve
│   └── package.json
├── docker-compose.yml      # Backend + Frontend (SQLite volume, simplified for MVP)
├── README.md
├── KONTEXT.md              # Legacy context (many outdated entries)
└── exp/                    # Fresh docs: README.md, Documentation.md, KONTEXT.md (this file)
```

---

## Modules — Status & Details

### 1. Analytics (`/analytics`)
- **Status:** ✅ Done
- 4 modes: Идея, Конкуренты, SWOT, ЦА
- Uses LLM for analysis, falls back to structured templates

### 2. Content (`/content`)
- **Status:** ✅ Done
- Input: content type (post/reels/article/stories/carousel) + platform (Instagram/Telegram/YouTube/TikTok) + idea text
- Returns: success_probability, viral_potential, originality_score, engagement_prediction, hashtags, recommendations
- F-string bug fixed: escaped `{` → `{{` in JSON prompt templates

### 3. SMI (`/smi`)
- **Status:** ✅ Done
- Checks topic relevance via RSS feeds from top news sources

### 4. Market Research (`/market-research`)
- **Status:** ✅ Done
- Two-stage pipeline: collect real data (World Bank API, arXiv, Google Trends) → feed to LLM
- Enhanced fallback keeps real data when LLM fails

### 5. Dot Analysis (`/dot-analysis`)
- **Status:** ✅ Done
- Library of 15+ marketing models (AARRR, 4P, JTBD, GTM, Hook Model, SWARM, etc.)
- LLM selects best-fit models for user context

### 6. Help Colleague (`/help-colleague`)
- **Status:** ✅ Done (last module completed)
- Full social-feed backend + frontend
- See dedicated section below

---

## Help Colleague — Full Specification

### Backend
- **Models:** `HelpColleaguePost`, `HelpColleagueResponse`, `HelpColleagueTag`, `HelpColleaguePostTag` (M:N), `HelpColleagueNotification`
- **Column `hot_score`** added via inline migration (ALTER TABLE) in `main.py`
- **Service:** `backend/app/services/help_colleague/service.py`
- **API router:** `backend/app/api/help_colleague.py` (prefix `/api/v1/help-colleague`)
- **All endpoints working** — tested with seed data (8 example posts + responses + votes)

### Frontend
- **Pages:** `HelpColleaguePage.tsx` (feed), `HelpColleagueDetailPage.tsx` (detail + responses + AI button), `HelpColleagueProfilePage.tsx`
- **Service:** `helpColleagueService.ts` — all 19 typed API methods
- **Redux slice:** `helpColleagueSlice.ts` — posts, currentPost, responses, sort, tags, notifications
- **Layout.tsx:** notification bell with 30-sec polling, profile menu, settings button

### Features
- Sort: **New** (blue toggle), **Hot** (orange toggle), **Top** (gold toggle) — each with distinct MUI-selected colors
- Filters: category dropdown + tag chips
- Create post with tags (comma-separated), auto-creates tags
- Vote on posts and responses (±1), updates hot score
- Close post (owner only)
- AI-generated answer via GigaChat button on detail page
- Notification polling (30s), mark-as-read, unread badge
- User profile with karma, posts/responses count

### Known Bugs / Gotchas
- ~~`_recalc_hot_score` crashed on naive datetime from SQLite~~ FIXED: `created.tzinfo is None → replace(tzinfo=timezone.utc)`
- ~~Profile 404 when User not in table~~ FIXED: returns default profile
- ~~Missing POST /tags endpoint~~ FIXED: added
- `create_tables()` must run before any route handler — already in `main.py` startup event
- The `/api/v1/help-colleague/posts/top` and `/api/v1/help-colleague/posts/hot` routes must be defined **before** `/api/v1/help-colleague/posts/{post_id}` to avoid FastAPI matching "top"/"hot" as `post_id`

### Tags
```
вконтакте, таргетинг, ozon, wb, маркетплейсы, telegram-ads, b2b,
нейросети, креативы, ai, ltv, аналитика, retention, вакансия, pm, seo, реклама
```

---

## Settings (UI)

- **Component:** `SettingsDialog.tsx`
- **Context:** `ThemeContext.tsx`
- Settings stored in `localStorage`:
  - `theme-mode` → 'light' | 'dark'
  - `notifications-enabled` → 'true' | 'false'
  - `posts-per-page` → number (10/20/50)
- MUI theme is dynamically built in `main.tsx` based on `mode` from `useThemeMode()`

---

## Docker / Deploy

### Dockerfiles
- `backend/Dockerfile` — python:3.12-slim, uvicorn on port 8000
- `frontend/Dockerfile` — multi-stage: node:20 build → nginx:alpine serve on port 80
- `docker-compose.yml` — simplified: backend + frontend + SQLite volume (no PostgreSQL/Redis/Qdrant for MVP)

### Deployment Recommendation: **Amvera** (free tier)
- Supports Docker containers, persistent storage, custom domains
- Alternative: Vercel (frontend only) + separate backend hosting

---

## Common Commands

```powershell
# Backend
cd backend
.\venv\Scripts\activate
uvicorn app.main:app --reload --port 8005

# Frontend
cd frontend
npm run dev

# Docker
docker-compose up --build

# Seed help-colleague (requires running server)
python seed_hc.py
```

---

## Quick Context (for new LLM session)

When you start fresh, the app is **fully functional** with all 6 modules. The most recent work was on the `help-colleague` module (social feed). All critical bugs are fixed. The app uses SQLite with inline migrations. No Alembic. Frontend proxies `/api` to backend. The theme supports light/dark mode. Help-colleague has seed data.

**To verify everything works:** start backend (port 8005) + frontend (port 3000), open `/help-colleague`, check that 16 posts load, click one, see AI button, submit a response, vote, check settings dialog.
