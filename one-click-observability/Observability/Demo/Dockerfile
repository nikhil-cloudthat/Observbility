FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN apt-get update -y
RUN apt install curl -y
RUN pip install -r requirements.txt
RUN pip install --upgrade pip
RUN pip install Flask opentelemetry-api opentelemetry-sdk opentelemetry-instrumentation-flask opentelemetry-exporter-otlp opentelemetry-instrumentation-logging

COPY application.py application.py

CMD ["python", "application.py"]