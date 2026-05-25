# Frontend

Современный React + TypeScript фронтенд для Chill Marketing AI Bot с красивым UI.

## Технологии

- **React 18** - UI библиотека
- **TypeScript** - типизация
- **Redux Toolkit** - управление состоянием
- **Material UI** - компоненты интерфейса
- **Framer Motion** - анимации
- **React Router** - навигация
- **Vite** - сборка
- **Axios** - HTTP клиент

## Установка

```bash
npm install
```

## Запуск в режиме разработки

```bash
npm run dev
```

Приложение будет доступно на http://localhost:3000

## Сборка для продакшена

```bash
npm run build
```

## Структура

```
src/
├── components/     # Переиспользуемые компоненты
│   └── Layout.tsx  # Основной layout с sidebar
├── pages/          # Страницы приложения
│   ├── Dashboard.tsx
│   ├── AnalyticsPage.tsx
│   ├── ContentPage.tsx
│   ├── SMIPage.tsx
│   ├── MarketResearchPage.tsx
│   ├── DotAnalysisPage.tsx
│   └── HelpColleaguePage.tsx
├── services/       # API сервисы
│   ├── api.ts
│   ├── analyticsService.ts
│   ├── contentService.ts
│   ├── smiService.ts
│   ├── marketResearchService.ts
│   ├── dotAnalysisService.ts
│   └── helpColleagueService.ts
├── store/          # Redux store
│   ├── store.ts
│   └── slices/
│       ├── analyticsSlice.ts
│       ├── contentSlice.ts
│       ├── smiSlice.ts
│       ├── marketResearchSlice.ts
│       ├── dotAnalysisSlice.ts
│       ├── helpColleagueSlice.ts
│       └── uiSlice.ts
├── utils/          # Утилиты
├── App.tsx         # Корневой компонент
├── main.tsx        # Точка входа
└── index.css       # Глобальные стили
```

## Фичи

- 🎨 Современный дизайн с градиентами и анимациями
- 📱 Адаптивный интерфейс (mobile-first)
- 🚀 Плавные анимации с Framer Motion
- 🧩 Модульная архитектура
- 🔌 Готовая интеграция с backend API
- 📊 Визуализация данных с чипами и прогресс-барами
- 🌓 Светлая тема (темная в планах)

## Доступные модули

1. **Dashboard** - Главная страница с навигацией
2. **Аналитика** - Анализ маркетинговых идей
3. **Контент** - Оценка контента для соцсетей
4. **СМИ** - Проверка актуальности тем
5. **Исследования** - Маркетинговые исследования
6. **Dot Analysis** - Подбор маркетинговых моделей
7. **Помощь коллег** - Сообщество для обмена идеями
