# Build stage
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --prefix=/install -r requirements.txt

# Final stage
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /install /usr/local
COPY worker.py .

RUN useradd -m appuser
USER appuser

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
  CMD python -c "import redis, os; r = redis.Redis(host=os.getenv('REDIS_HOST','redis'), password=os.getenv('REDIS_PASSWORD')); r.ping()" || exit 1

CMD ["python", "worker.py"]