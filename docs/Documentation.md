# Chill Marketing AI Bot

> Интеллектуальная система поддержки принятия решений в маркетинге на основе больших языковых моделей (LLM).

Заменяет 70–90% рутинных функций маркетолога: от анализа идеи до генерации контента и исследований рынка.

---

## Модули системы

| Модуль | Путь | Описание |
|--------|------|----------|
| **Analytics** | `/analytics` | AI-аналитика маркетинговой идеи: 4 режима — Идея, Конкуренты, SWOT, ЦА |
| **Content** | `/content` | Анализ идеи для контента (пост, рилс, статья, сторис, карусель) под платформы Instagram, Telegram, YouTube, TikTok |
| **SMI** | `/smi` | Проверка актуальности темы для статьи/новости по RSS-лентам СМИ |
| **Market Research** | `/market-research` | Исследование рынка с реальными цифрами (World Bank API, arXiv, Google Trends) |
| **Dot Analysis** | `/dot-analysis` | Подбор маркетинговых моделей (AARRR, 4P, JTBD, GTM, SWARM, Hook Model и др.) под контекст бизнеса |
| **Help Colleague** | `/help-colleague` | Сообщество для обмена идеями: посты, ответы, голосование, AI-ответы, теги, рейтинг, уведомления |

---

## Технологический стек

### Backend
- **Язык:** Python 3.12
- **Фреймворк:** FastAPI
- **ORM:** SQLAlchemy 2.0 + Pydantic v2
- **База данных:** SQLite (локально) / PostgreSQL (продакшн)
- **LLM:** GigaChat API (через gigachat + langchain-gigachat)
- **HTTP-клиент:** httpx 0.28+
- **Фоновые задачи:** Celery + Redis (опционально)

### Frontend
- **Язык:** TypeScript
- **Фреймворк:** React 18
- **Сборка:** Vite 5
- **UI Kit:** MUI (Material-UI) 5
- **Анимации:** Framer Motion
- **Состояние:** Redux Toolkit
- **Роутинг:** React Router v6
- **Графики:** Recharts
- **Запросы:** Axios

---

## Быстрый старт

### Локальная разработка

```powershell
# Backend
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
.\venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000

# Frontend (в новом терминале)
cd frontend
npm install
npm run dev
```

Фронтенд запускается на `http://localhost:3000`, проксирует `/api/*` на `http://localhost:8000`.

### Docker Compose

```bash
docker-compose up --build
```

- Backend: `http://localhost:8000`
- Frontend: `http://localhost:3000`
- Swagger: `http://localhost:8000/docs`

---

## Структура проекта

```
chill-marketing-ai-bot/
├── backend/
│   ├── app/
│   │   ├── api/              # FastAPI роутеры
│   │   │   ├── analytics.py
│   │   │   ├── content.py
│   │   │   ├── smi.py
│   │   │   ├── market_research.py
│   │   │   ├── dot_analysis.py
│   │   │   ├── help_colleague.py
│   │   │   └── trends.py
│   │   ├── database/         # SQLAlchemy engine + session
│   │   ├── models/           # SQLAlchemy + Pydantic модели
│   │   ├── services/         # Бизнес-логика по модулям
│   │   │   ├── analytics/
│   │   │   ├── content/
│   │   │   ├── smi/
│   │   │   ├── market_research/
│   │   │   ├── dot_analysis/
│   │   │   └── help_colleague/
│   │   ├── utils/            # LLM клиент, библиотека моделей, RSS, векторы
│   │   ├── config.py         # Pydantic Settings (.env)
│   │   ├── celery.py         # Celery app
│   │   ├── main.py           # Точка входа FastAPI
│   │   └── tasks.py          # Celery задачи
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── public/
│   │   └── vite.svg          # Favicon
│   ├── src/
│   │   ├── components/       # Layout, SettingsDialog и др.
│   │   ├── contexts/         # ThemeContext (light/dark)
│   │   ├── pages/            # Страницы по модулям
│   │   ├── services/         # API клиенты (Axios)
│   │   ├── store/            # Redux slices
│   │   ├── App.tsx           # Роутинг
│   │   ├── main.tsx          # Точка входа (тема, провайдеры)
│   │   └── index.css
│   ├── nginx.conf
│   ├── vite.config.ts
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
├── README.md
└── KONTEXT.md
```

---

## API Endpoints

Базовый путь: `/api/v1`

### Analytics
| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/analytics/analyze` | Анализ маркетинговой идеи |
| GET | `/analytics/requests` | Список запросов |
| GET | `/analytics/requests/{id}` | Детали запроса |

### Content
| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/content/analyze` | Анализ контент-идеи |

### SMI
| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/smi/analyze` | Анализ актуальности темы |

### Market Research
| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/market-research/conduct` | Исследование рынка |

### Dot Analysis
| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/dot-analysis/analyze` | Подбор моделей |

### Help Colleague
| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/help-colleague/tags` | Список тегов |
| POST | `/help-colleague/tags` | Создать тег |
| POST | `/help-colleague/posts` | Создать пост |
| GET | `/help-colleague/posts` | Лента постов (sort: new/hot/top, filter: category, tag) |
| GET | `/help-colleague/posts/{id}` | Детали поста |
| POST | `/help-colleague/posts/{id}/responses` | Ответить на пост |
| POST | `/help-colleague/posts/{id}/vote` | Голосовать (±1) |
| POST | `/help-colleague/posts/{id}/close` | Закрыть пост (автор) |
| POST | `/help-colleague/posts/{id}/ai-response` | Сгенерировать AI-ответ |
| POST | `/help-colleague/responses/{id}/rate` | Оценить ответ |
| GET | `/help-colleague/search?q=` | Поиск по постам |
| GET | `/help-colleague/profile/{userId}` | Профиль пользователя |
| GET | `/help-colleague/profile/{userId}/posts` | Посты пользователя |
| GET | `/help-colleague/profile/{userId}/responses` | Ответы пользователя |
| GET | `/help-colleague/notifications` | Уведомления |
| GET | `/help-colleague/notifications/unread-count` | Счётчик непрочитанных |
| POST | `/help-colleague/notifications/read` | Отметить прочитанными |

---

## Help Colleague (сообщество)

Социальная лента для обмена маркетинговыми идеями, вопросами и кейсами.

### Возможности
- **Сортировка:** Новые / Горячие (Reddit-style hot score) / Топ (по рейтингу)
- **Фильтры:** по категории (idea, problem, feedback, collaboration) и тегам
- **Голосование:** за посты и ответы (лайк/дизлайк)
- **AI-ответ:** автоматическая генерация ответа через GigaChat
- **Теги:** создаются автоматически при создании поста
- **Уведомления:** при новых ответах на пост (30-сек polling)
- **Профиль:** карма, статистика постов и ответов
- **Тёмная тема:** переключение в настройках

### Hot Score Formula
```
hot_score = (rating + responses_count * 2) / (age_hours + 2)^1.5
```

### Модели данных

**HelpColleaguePost:** id, user_id, title, description, category, is_anonymous, responses_count, rating, hot_score, status, created_at, tags (M:N)

**HelpColleagueResponse:** id, post_id, user_id, content, rating, is_from_bot, created_at

**HelpColleagueNotification:** id, user_id, from_user_id, post_id, type, message, is_read, created_at

---

## Настройки приложения

Доступны через боковое меню → «Настройки»:
- **Тема:** светлая / тёмная (сохраняется в localStorage)
- **Уведомления:** вкл/выкл 30-сек polling
- **Постов на странице:** 10 / 20 / 50
- **Язык:** Русский (заглушка)

---

## Деплой

### Рекомендация: Amvera (бесплатный тариф)

1. Создайте `Dockerfile` (уже есть) и залейте проект на GitHub
2. Зарегистрируйтесь на [amvera.io](https://amvera.io)
3. Создайте проект → свяжите с репозиторием
4. Укажите порт 8000 в конфигурации
5. Amvera сам соберёт образ и запустит

### Vercel
Подходит только для фронтенда. Бекенд придётся размещать отдельно.

---

## Переменные окружения (.env)

```
GIGACHAT_CREDENTIALS=<base64 credentials>
GIGACHAT_PROXY=http://proxy:port
DEEPSEEK_API_KEY=<key>
NEWSAPI_KEY=<key>
DATABASE_URL=sqlite:///./chillbot.db
```

---

## Лицензия

MIT
