FROM python:3.11-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml uv.lock /app/

RUN pip install --upgrade pip
RUN uv sync --frozen --no-dev

COPY src /app/

ENV PATH="/app/.venv/bin:$PATH"

CMD ["python", "-m", "app.main"]