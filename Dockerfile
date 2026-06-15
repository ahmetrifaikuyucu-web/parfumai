FROM python:3.11-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 libatlas-base-dev gfortran && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY . .

RUN mkdir -p static/perfume_images data logs yedekler && \
    python setup.py && \
    rm -rf __pycache__ *.pyc .pytest_cache

EXPOSE 5000
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

CMD ["waitress-serve", "--host=0.0.0.0", "--port=5000", "app:create_app()"]
