# syntax=docker/dockerfile:1
FROM python:3.12-slim-bookworm
WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

RUN apt-get update \
    && apt-get install -y --no-install-recommends libatomic1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY prisma ./prisma
COPY app ./app

RUN python -m prisma generate

EXPOSE 8000

CMD ["sh", "-c", "python -m prisma migrate deploy && python -m app.seed && exec uvicorn app.main:app --host 0.0.0.0 --port 8000"]
