FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir /users_backend
WORKDIR /users_backend

RUN pip install --upgrade pip
RUN pip install poetry

COPY pyproject.toml .

RUN poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction --no-ansi

EXPOSE 8000

COPY . .

CMD ["uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
