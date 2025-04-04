# Dockerfile inside SharedAlbumEventBroker/
FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install pika

ENV RABBITMQ_HOST=rabbitmq

CMD ["python", "sharedalbum_eventbroker.py"]
