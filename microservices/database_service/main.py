from fastapi import FastAPI, Request
from typing import Dict
from logging_config import logger

app = FastAPI()
db: Dict[str, str] = {}

@app.get("/")
def root():
    logger.info("Database root endpoint hit.")
    return {"message": "Database Service: stores and retrieves data"}

@app.get("/health")
def health():
    logger.info("Database health check.")
    return {"status": "ok"}

@app.post("/write")
async def write(request: Request):
    body = await request.json()
    key = body.get("key")
    value = body.get("value")
    if not key or value is None:
        logger.warning("Missing key or value in /write request.")
        return {"error": "Missing key or value"}
    db[key] = value
    logger.info(f"Stored key={key} with value={value}")
    return {"status": "written"}

@app.get("/read")
def read(key: str):
    value = db.get(key, None)
    logger.info(f"Reading key={key}, found={value is not None}")
    return {"value": value}
