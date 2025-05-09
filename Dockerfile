# Dockerfile
FROM python:3.10-slim

# 1. Set working directory
WORKDIR /app

# 1.1
COPY logging_config.py logging_config.py

# 1.2
COPY alert_engine.py alert_engine.py

# 2. Copy and install dependencies
COPY microservices/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copy microservice source code
COPY microservices/ ./microservices/

# 4. Default environment var for client auth
ENV CLIENT_SECRET=SECRET_TOKEN

# 5. Expose all three service ports
EXPOSE 8000 8001 8002

# 6. Use uvicorn as entrypoint
ENTRYPOINT ["uvicorn"]

# 7. Default to Client Service (override for others)
CMD ["microservices.client_service.main:app", "--host", "0.0.0.0", "--port", "8000"]
