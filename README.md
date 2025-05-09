# Microservices system with Celery, logging, and alerting

## Overview

This microservices-based system is designed to handle synchronous and asynchronous operations with proper logging, alerting, and task delegation using Celery. It consists of multiple FastAPI-based services, Redis for message brokering, and Celery workers for background processing.

---

## Components

### 1. **Client service (`client_service`)**
- Exposes:
  - `POST /add`: save a key-value pair.
  - `POST /run`: process data for a given key.
- Validates authentication via token.
- Detects personal data (email, phone, credit cards numbers and so on) and raises alerts.
- Logs every request and outcome.
- Sends background processing tasks to Celery.

### 2. **Database service (`database_service`)**
- A simple key-value store microservice.
- Provides `POST /write` and `GET /read`

### 3. **Business logic service (`business_logic_service`)**
- Legacy-style logic microservice.
- Now optional as processing is handled via Celery.

### 4. **Scheduler service (`scheduler_service`)**
- Periodically pings the business logic service to ensure availability.
- Uses APScheduler.

### 5. **Celery workers**
- Two workers deployed in the same pod.
- Process tasks asynchronously via Redis.
- Each task is defined in `client_service/tasks.py`.

### 6. **Redis**
- Serves as the broker and backend for Celery.
- Deployed as a container inside the same pod.

### 7. **Logging and alert system**
- Logs all service activity into `logs/app.log`.
- Writes alerts (invalid token, personal data and so on) as `.txt` files into `error_reports/`.

---

## Operation flow

### `/add` (synchronous)
1. Validates token.
2. Checks for personal data in the value.
3. Sends data to `database_service` via `/write`.

### `/run` (asynchronous)
1. Reads raw value from `database_service` via `/read`.
2. Sends it to Celery using `process_data_task.delay(data)`.
3. Returns a `task_id` immediately.
4. Celery worker picks up the task and transforms the value (e.g., uppercase).

---

## Execution types

| Component                 | Operation                | Type         |
|--------------------------|--------------------------|--------------|
| `/add`                   | Write data to DB         | Synchronous  |
| `/run`                   | Start async processing   | Synchronous  |
| `process_data_task`      | Transform data           | Asynchronous |
| Redis                    | Queue broker for Celery  | Async support |
| Alert Generation         | On input or auth errors  | Synchronous  |

---

## Project Structure
```
architecture_microservices_HW3_p2/
├── microservices/
│ ├── client_service/
│ │ ├── main.py
│ │ ├── tasks.py
│ │ ├── celery_app.py
│ │ └── init.py
│ ├── database_service/
│ │ └── main.py
│ ├── business_logic_service/
│ │ └── main.py
│ └── requirements.txt
├── scheduler_service/
│ ├── main.py
│ ├── Dockerfile
│ └── requirements.txt
├── logging_config.py
├── alert_engine.py
├── pod.yaml
├── Dockerfile
└── README.md
```

---

## How to run

### 1. **Build images**
```bash
podman build -t localhost/microsvc -f Dockerfile .
podman build -t localhost/scheduler -f scheduler_service/Dockerfile scheduler_service/
```

### 2. Start the full pod
```bash
podman pod rm -f microservices-pod  # If already running
podman play kube pod.yaml
```

### 3. Example Usage
```bash
curl -X POST "http://localhost:8000/add?key=test1&value=hello" -H "Authorization: Bearer SECRET_TOKEN"
curl -X POST "http://localhost:8000/run?key=test1" -H "Authorization: Bearer SECRET_TOKEN"
```

### 4. Check Logs
```bash
podman logs -f microservices-pod-client
podman logs -f microservices-pod-worker1
podman logs -f microservices-pod-worker2
```

---

## Scaling strategy

### 10 simultaneous connections

**Assumptions:** Low traffic, occasional task submissions, minimal CPU and memory usage.

**Strategy:**
- 1 instance per service (client_service, database_service, logic_service);
- 1 Celery worker (2 concurrency);
- Redis in the same pod;
- Logs and alerts handled locally.

Single Pod with all containers. No scaling needed.

### 50 Simultaneous Connections

**Assumptions:** Moderate traffic with frequent async task generation, ~10 Celery tasks queued at a time.

**Strategy:**
- Increase replicas of client_service to 2;
- Add 2–3 Celery workers (2 concurrency each);
- A persistent volume for logs and alerts if needed;
- Liveness/readiness probes for auto-recovery;

Use Podman-compose to run client service and Celery workers as horizontally scalable deployments.

### 100 or More Simultaneous Connections

**Assumptions:** Heavy traffic, continuous task queuing. High concurrency needs for both sync and async services. Increased logging and alert generation.

**Strategy:**
- 3–5 replicas of client_service (behind a load balancer);
- 5–10 Celery workers (concurrency 2–4 depending on CPU availability);
- Logging backend instead of .txt files;
- Offload alerts to a monitoring/alerting service;
- Move DB to scalable backend (e.g., PostgreSQL, DynamoDB).

