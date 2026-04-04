FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Копируем файлы зависимостей
COPY pyproject.toml uv.lock /app/

# Обновляем pip
RUN pip install --upgrade pip
RUN uv sync --frozen

# Устанавливаем uvicorn + зависимости FastAPI
# Если используешь uv, можно потом синхронизировать зависимости через uv sync
# RUN pip install "uvicorn[standard]"

# Копируем исходный код приложения
COPY src /app/

# Экспонируем порт (необязательно, но удобно)
ENV PATH="/app/.venv/bin:$PATH"

# Команда запуска приложения
CMD ["python", "-m", "app.main"]