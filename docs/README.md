# Chill Marketing AI Bot

Интеллектуальная система поддержки принятия решений в маркетинге на основе LLM (GigaChat API).

Заменяет 70–90% функций маркетолога: анализ идей, контент, SMI, исследования рынка, маркетинговые модели, сообщество.

---

## Модули системы

| Модуль | Маршрут | Назначение |
|--------|---------|------------|
| **Analytics** | `/analytics` | AI-аналитика идеи (4 режима) |
| **Content** | `/content` | Анализ контента для соцсетей |
| **SMI** | `/smi` | Проверка актуальности темы |
| **Market Research** | `/market-research` | Исследование рынка (World Bank, arXiv, Google Trends) |
| **Dot Analysis** | `/dot-analysis` | Подбор маркетинговых моделей (AARRR, 4P, JTBD и др.) |
| **Help Colleague** | `/help-colleague` | Сообщество: посты, ответы, голосование, AI-ответ, теги, уведомления |

---

## Технологии

**Backend:** Python 3.12, FastAPI, SQLAlchemy 2.0 + Pydantic v2, SQLite, GigaChat API, httpx

**Frontend:** TypeScript, React 18, Vite 5, MUI 5, Redux Toolkit, React Router v6, Framer Motion, Recharts, Axios

**Инфра:** Docker Compose, nginx (для production-сборки фронта)

---

## Структура проекта

```
chill-marketing-ai-bot/
├── backend/
│   ├── app/
│   │   ├── api/              # FastAPI routers (аналитика, контент, smi, исследования, dot, help-colleague, тренды)
│   │   ├── database/         # SQLAlchemy engine + get_db
│   │   ├── models/           # SQLAlchemy ORM + Pydantic схемы
│   │   ├── services/         # Бизнес-логика по модулям
│   │   ├── utils/            # LLM клиент, маркетинговые модели, RSS, Qdrant
│   │   ├── config.py         # Pydantic Settings (из .env)
│   │   ├── main.py           # FastAPI app + create_tables()
│   │   └── celery.py         # Celery (опционально)
│   ├── requirements.txt      # Python зависимости
│   └── Dockerfile
├── frontend/
│   ├── public/
│   │   └── vite.svg          # Favicon (градиент "CM")
│   ├── src/
│   │   ├── components/       # Layout (sidebar + appbar), SettingsDialog
│   │   ├── contexts/         # ThemeContext (светлая/тёмная тема)
│   │   ├── pages/            # Dashboard, Analytics, Content, SMI, MarketResearch, DotAnalysis, HelpColleague*
│   │   ├── services/         # API-клиенты (Axios) для каждого модуля
│   │   ├── store/            # Redux store + slices (analytics, content, helpColleague и др.)
│   │   ├── App.tsx           # Роутинг (React Router v6)
│   │   ├── main.tsx          # Точка входа (ThemeProvider + Redux Provider + BrowserRouter)
│   │   └── index.css
│   ├── nginx.conf            # SPA + proxy_pass /api → backend:8000
│   ├── vite.config.ts        # Vite config, proxy /api → localhost:8005 (dev)
│   ├── Dockerfile            # Multi-stage: build → nginx
│   └── package.json
├── docker-compose.yml        # Backend + Frontend (SQLite)
├── README.md
├── KONTEXT.md
└── exp/
    ├── README.md
    ├── Documentation.md
    └── KONTEXT.md
```

---

## Запуск

### Локально (dev)

```powershell
# Terminal 1 — Backend
cd backend
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8005

# Terminal 2 — Frontend
cd frontend
npm run dev   # http://localhost:3000, proxy /api → :8005
```

### Docker

```bash
docker-compose up --build
# Frontend: http://localhost:3000
# Backend:  http://localhost:8000
# Swagger:  http://localhost:8000/docs
```

---

## Help Colleague (социальная лента)

### Функции
- Создание постов с категорией и тегами
- Сортировка: **Новые** / **Горячие** (Reddit-формула) / **Топ**
- Фильтры: категория, теги, поиск
- Голосование за посты и ответы (±1)
- AI-ответ (GigaChat) через кнопку на странице поста
- Закрытие поста (только автор)
- Уведомления о новых ответах (polling 30 сек)
- Профиль пользователя с кармой и статистикой
- Тёмная тема (через Настройки)

### API Help Colleague

Все под `/api/v1/help-colleague/`.

- `GET /tags` · `POST /tags` — теги
- `POST /posts` · `GET /posts` · `GET /posts/{id}` — CRUD постов
- `POST /posts/{id}/responses` — ответ
- `POST /posts/{id}/vote` — голос (±1)
- `POST /posts/{id}/close` — закрыть
- `POST /posts/{id}/ai-response` — AI-ответ
- `POST /responses/{id}/rate` — оценка ответа
- `GET /search?q=` — поиск
- `GET /profile/{userId}` · `/profile/{userId}/posts` · `/profile/{userId}/responses`
- `GET /notifications` · `/notifications/unread-count` · `POST /notifications/read`

### Модели БД

**HelpColleaguePost:** id, user_id, title, description, category, is_anonymous, responses_count, rating, hot_score, status, created_at

**HelpColleagueResponse:** id, post_id, user_id, content, rating, is_from_bot, created_at

**HelpColleagueTag** + **HelpColleaguePostTag** (M:N)

**HelpColleagueNotification:** id, user_id, from_user_id, post_id, type, message, is_read, created_at

**HelpColleagueUserStats:** (зарезервировано)

### Hot Score (Reddit-style)
```
hot_score = max(rating, 0) + responses_count * 2
            ──────────────────────────────
                (age_hours + 2) ^ 1.5
```

---

## Настройки (SettingsDialog)

Боковое меню → «Настройки»:

- **Тема:** светлая / тёмная (localStorage, ThemeContext)
- **Уведомления:** вкл/выкл polling
- **Постов на странице:** 10 / 20 / 50
- **Язык:** русский (заглушка, disabled)

---

## Известные особенности

- **SQLite в продакшне:** не поддерживает конкурентные записи. Для продакшна заменить на PostgreSQL.
- **GigaChat:** требуется `GIGACHAT_CREDENTIALS`. При их отсутствии — fallback-ответы.
- **Qdrant:** не запущен локально — инициализация падает с `WinError 10061`, но это не критично.
- **CORS:** открыт для всех источников (`allow_origins=["*"]`).
- **Прокси:** если вы в РФ, для GigaChat может потребоваться `GIGACHAT_PROXY`.

---

## Деплой

```bash
docker-compose up --build -d
```
