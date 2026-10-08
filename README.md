# Store Backend

Сервис категорий backend на Python.

## Stack

* Python 3.12+
* FastAPI
* PostgreSQL
* SQLAlchemy 2.x
* Alembic
* Redis
* Kafka
* Prometheus
* Grafana
* pytest
* Docker Compose

Тестовый админ

```bash
Admin email: admin@example.com
Admin password: 1234
```

---

# Запуск проекта

## Запустить инфраструктуру

Из корня проекта:

```bash
docker compose up -d
```

Проверить контейнеры:

```bash
docker compose ps
```

Остановить:

```bash
docker compose down
```

# Python environment

Активировать venv:

```bash
source .venv/bin/activate
```

Windows:

```powershell
.venv\Scripts\activate
```

Установить зависимости:

```bash
pip install -r requirements.txt
```

---

# Database / Alembic

Применить миграции:

```bash
alembic upgrade head
```

Создать новую миграцию:

```bash
alembic revision --autogenerate -m "description"
```

Посмотреть текущую миграцию:

```bash
alembic current
```

Посмотреть историю:

```bash
alembic history
```

---

# Запуск FastAPI

```bash
uvicorn app.main:app --reload
```

API:

```text
http://localhost:8000
```

Swagger:

```text
http://localhost:8000/docs
```

Health:

```text
http://localhost:8000/health
```

Metrics:

```text
http://localhost:8000/metrics
```

---

# Основные API

## Health

```bash
curl http://localhost:8000/health
```

---


Получить товар:

```bash
curl http://localhost:8000/products/1
```

Получить список:

```bash
curl "http://localhost:8000/products?limit=10"
```

Следующая страница:

```bash
curl "http://localhost:8000/products?limit=10&cursor=<CURSOR>"
```

Создать товар:

```bash
curl -X POST http://localhost:8000/products \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{
    "category_id": 1,
    "name": "Keyboard",
    "description": "Mechanical keyboard",
    "price": 99.99
  }'
```

Удалить товар:

```bash
curl -X DELETE http://localhost:8000/products/1 \
  -H "Authorization: Bearer <TOKEN>"
```

---

# Authentication

Login:

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=admin"
```

Ответ содержит:

```text
access_token
```

Использовать токен:

```bash
-H "Authorization: Bearer <TOKEN>"
```

Создание admin:

```bash
python -m app.scripts.create_admin
```

---

# Services

## FastAPI

```text
http://localhost:8000
```

Metrics:

```text
http://localhost:8000/metrics
```

## Outbox Publisher

Metrics:

```text
http://localhost:8001/metrics
```

Запуск:

```bash
python -m app.kafka.outbox_publisher
```

## Cache Sync

Metrics:

```text
http://localhost:8002/metrics
```

Запуск:

```bash
python -m app.cache_sync.consumer
```

---

# Redis

Redis:

```text
localhost:6379
```

Проверить Redis:

```bash
docker exec -it store-redis redis-cli ping
```

Ожидаемый ответ:

```text
PONG
```

Посмотреть ключи:

```bash
docker exec -it store-redis redis-cli keys "*"
```

---

# PostgreSQL



# Kafka

Kafka:

```text
localhost:9092
```

Основной topic:

```text
product-events
```

Посмотреть topics:

```bash
docker exec -it store-kafka \
  /opt/kafka/bin/kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --list
```

Consumer group:

```text
cache-sync
```

---

# Prometheus

Prometheus:

```text
http://localhost:9090
```

Targets:

```text
http://localhost:9090/targets
```

Основные метрики:

```promql
http_requests_total
```

```promql
outbox_events_published_total
```

```promql
outbox_events_failed_total
```

```promql
kafka_events_processed_total
```

```promql
kafka_events_duplicates_total
```

Cache:

```promql
cache_hits_total
```

```promql
cache_misses_total
```

---

# Grafana

Grafana:

```text
http://localhost:3000
```

Datasource:

```text
Prometheus
```

Основные панели:

* HTTP RPS
* HTTP 5xx Errors
* HTTP p95 Latency
* HTTP Requests by Endpoint
* Redis Cache Hit Rate
* Outbox Publish Rate
* Outbox Publish Failures
* Kafka Processed Rate
* Kafka Duplicates Rate


# Tests

Запустить все тесты:

```bash
pytest
```

Более подробно:

```bash
pytest -v
```

Конкретный файл:

```bash
pytest tests/test_api.py -v
```

---

# Быстрый startup checklist

Когда возвращаюсь к проекту:

```bash
docker compose up -d
```

```bash
docker compose ps
```

Потом:

```bash
source .venv/bin/activate
```

Запустить API:

```bash
uvicorn app.main:app --reload
```

В отдельных терминалах:

```bash
python -m app.kafka.outbox_publisher
```

```bash
python -m app.cache_sync.consumer
```

Проверить:

```bash
curl http://localhost:8000/health
```

И открыть:

```text
http://localhost:8000/docs
http://localhost:9090
http://localhost:9090/targets
http://localhost:3000
```

Metrics:

```text
http://localhost:8000/metrics
http://localhost:8001/metrics
http://localhost:8002/metrics
```
