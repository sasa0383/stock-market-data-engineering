# Example Python Dockerfile for producer-service
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt


COPY . .

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]


