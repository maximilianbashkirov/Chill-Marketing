Вариант 1: Docker (рекомендуется)
# Запуск всего приложения (backend + frontend + БД)
docker-compose up --build
Backend: http://localhost:8000
Frontend: http://localhost:3000
API Docs: http://localhost:8000/docs
Вариант 2: Локально (отдельные терминалы)
Терминал 1 - Backend:

cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
Терминал 2 - Frontend:

cd frontend
npm install
npm run dev
Структура:
uvicorn app.main:app --reload - только backend (FastAPI на порту 8000)
npm run dev - только frontend (Vite на порту 3000)
Проверка работы:
Backend: http://localhost:8000/docs (Swagger)
Frontend: http://localhost:3000 (Main UI)
Frontend проксирует /api/* → localhost:8000
Frontend сделан на React + Vite + Material UI, подключается к backend через прокси в vite.config.ts. Всё корректно!