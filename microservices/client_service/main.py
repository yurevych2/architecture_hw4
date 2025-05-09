from fastapi import FastAPI, Header, HTTPException
import os
import re
import requests
from requests.exceptions import RequestException
from logging_config import logger
from alert_engine import generate_alert
from .tasks import process_data_task

app = FastAPI()
SECRET_TOKEN = os.getenv("CLIENT_SECRET", "SECRET_TOKEN")
DB_SERVICE = "http://localhost:8001"
LOGIC_SERVICE = "http://localhost:8002"

def contains_personal_data(value: str) -> bool:
    patterns = [
        r"\b\d{3}-\d{2}-\d{4}\b",     # SSN
        r"\b\d{16}\b",                # Credit card
        r"\b\d{10}\b",                # Phone number
        r"\b[\w.-]+@[\w.-]+\.\w+\b"   # Email
    ]
    return any(re.search(p, value) for p in patterns)

@app.get("/")
def root():
    logger.info("Client root endpoint hit.")
    return {"message": "Client Service: Orchestrates calls between DB and Logic"}

@app.get("/health")
def health():
    logger.info("Health check for client service.")
    return {"status": "ok"}

@app.post("/add")
def add_data(key: str, value: str, authorization: str = Header(None)):
    logger.info(f"/add called with key={key}")

    if authorization != f"Bearer {SECRET_TOKEN}":
        logger.warning("Unauthorized access to /add")
        generate_alert("Attempted Fraud", f"Invalid token received: {authorization}")
        raise HTTPException(status_code=403, detail="Invalid or missing token")

    if not key or value is None:
        logger.warning("Missing key or value in request.")
        generate_alert("Incorrect Input", f"Missing key or value: key={key}, value={value}")
        return {"error": "Missing key or value"}

    if contains_personal_data(value):
        logger.warning(f"Potential personal data in value: {value}")
        generate_alert("Personal Data", f"User submitted sensitive value: {value}")

    try:
        response = requests.post(f"{DB_SERVICE}/write", json={"key": key, "value": value}, timeout=3)
        response.raise_for_status()
        logger.info(f"Successfully wrote {key} to DB")
        return response.json()
    except RequestException as e:
        logger.error(f"Error writing to DB: {e}")
        raise HTTPException(status_code=502, detail="Failed to write to DB")

@app.post("/run")
def run_process(key: str, authorization: str = Header(None)):
    logger.info(f"/run called with key={key}")

    if authorization != f"Bearer {SECRET_TOKEN}":
        logger.warning("Unauthorized access to /run")
        generate_alert("Attempted Fraud", f"Invalid token received: {authorization}")
        raise HTTPException(status_code=403, detail="Invalid or missing token")

    try:
        db_response = requests.get(f"{DB_SERVICE}/read", params={"key": key}, timeout=3)
        db_response.raise_for_status()
        data = db_response.json().get("value")
        if data is None:
            logger.warning(f"No data found for key={key}")
            generate_alert("Incorrect Input", f"No data found for key={key}")
            raise HTTPException(status_code=404, detail="Data not found in DB")
    except RequestException as e:
        logger.error(f"Error reading from DB: {e}")
        raise HTTPException(status_code=502, detail="Failed to read from DB")

    task = process_data_task.delay(data)

    return {"message": "Processing started", "task_id": task.id}

