from microservices.client_service.celery_app import celery_app
from logging_config import logger

@celery_app.task(name="microservices.client_service.tasks.process_data_task")
def process_data_task(data):
    logger.info(f"Processing data asynchronously: {data}")
    return data.upper()
