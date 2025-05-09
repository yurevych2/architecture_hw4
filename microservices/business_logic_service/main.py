from fastapi import FastAPI, Request
from logging_config import logger

app = FastAPI()

@app.get("/")
def root():
    logger.info("Business Logic root endpoint hit.")
    return {"message": "Business Logic Service: processes data"}

@app.get("/health")
def health():
    logger.info("Business Logic health check.")
    return {"status": "ok"}

@app.post("/process")
async def process(request: Request):
    data = await request.json()
    input_data = data.get("data", "")
    logger.info(f"Processing data: {input_data}")
    result = input_data.upper()
    return {"processed_data": result}
