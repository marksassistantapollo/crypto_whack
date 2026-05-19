FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create a directory for the database to persist
RUN mkdir -p /data
VOLUME /data

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
