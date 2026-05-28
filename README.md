# Score IS — Информационная система учёта товарооборота

Full-stack веб-приложение для учёта закупок, продаж и складских остатков.

## Стек

| Слой | Технологии |
|------|-----------|
| Backend | FastAPI, SQLAlchemy, SQLite, Alembic, python-jose, bcrypt |
| Frontend | Vue 3, Vite, Element Plus, Pinia, Chart.js, axios |
| Инфраструктура | Docker, Docker Compose, nginx |

## Быстрый старт (Docker Compose)

```bash
# 1. Скопируйте файл с переменными окружения и задайте SECRET_KEY
cp .env.example .env
# Откройте .env и замените SECRET_KEY на случайную строку (минимум 32 символа)

# 2. Соберите и запустите
cd Score_IS
docker compose up --build -d

# 3. Заполните начальные данные (первый запуск)
docker exec emal-posuda-backend python seed.py
```

После запуска:
- Фронтенд: http://localhost:28491
- API (Swagger): http://localhost:18473/docs

## Локальный запуск без Docker

### Backend

```bash
cd Score_IS/backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Создайте .env с SECRET_KEY
echo "SECRET_KEY=ваш-секретный-ключ" > .env

python seed.py          # Первоначальные данные
uvicorn app.main:app --reload
```

### Frontend

```bash
cd Score_IS/frontend
npm install
npm run dev
```

## Демо-учётные данные (после seed.py)

| Email | Пароль | Роль |
|-------|--------|------|
| admin@example.com | admin123 | Администратор |

> Смените пароль после первого входа через раздел «Пользователи».

## Переменные окружения

| Переменная | Обязательна | По умолчанию | Описание |
|------------|-------------|-------------|----------|
| `SECRET_KEY` | **Да** | — | Ключ подписи JWT |
| `DATABASE_URL` | Нет | `sqlite:///./app.db` | URL БД |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Нет | `1440` | Время жизни токена (мин.) |
| `CORS_ORIGINS` | Нет | `*` (без credentials) | Список разрешённых origin через запятую, например `http://localhost:5173,https://example.com` |

## Функциональность

- Справочники: категории, единицы измерения, склады, поставщики, клиенты
- Товары с артикулами, ценами, изображениями и минимальным остатком
- Складские остатки с учётом среднего себестоимости
- Документы прихода (закупки) и расхода (продажи): черновик → проведён → отменён
- Инвентаризация и перемещение товаров между складами
- Дашборд с ключевыми показателями и графиками
- Отчёты с экспортом в Excel
- Управление пользователями (роли: admin, manager, warehouse)

## Структура проекта

```
Score_IS/
├── backend/
│   ├── app/
│   │   ├── api/v1/       # REST-роутеры
│   │   ├── core/         # конфигурация, БД, безопасность
│   │   ├── services/     # бизнес-логика документов
│   │   ├── models.py     # ORM-модели
│   │   ├── schemas.py    # Pydantic-схемы
│   │   └── crud.py       # функции работы с БД
│   ├── alembic/          # миграции
│   ├── seed.py           # начальные данные
│   └── requirements.txt
└── frontend/
    └── src/
        ├── api/          # axios-клиент
        ├── views/        # страницы
        ├── components/   # переиспользуемые компоненты
        ├── stores/       # Pinia-сторы
        └── router/       # маршруты
```
