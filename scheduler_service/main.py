import os, time, requests
from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
from logging_config import logger

app = FastAPI()
FIRST_URL = os.getenv("FIRST_SERVICE_URL", "http://logic:8002")

def ping_logic():
    try:
        r = requests.get(f"{FIRST_URL}/health", timeout=3)
        logger.info(f"Scheduler ping: logic health → {r.json()}")
    except Exception as e:
        logger.error(f"Scheduler error pinging logic: {e}")

@app.on_event("startup")
def start_scheduler():
    sched = BackgroundScheduler()
    sched.add_job(ping_logic, "interval", seconds=10)
    sched.start()
    logger.info("Scheduler started")

@app.get("/health")
def health():
    logger.info("Scheduler health check.")
    return {"status": "scheduler running"}
