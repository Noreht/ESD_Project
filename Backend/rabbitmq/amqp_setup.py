#!/usr/bin/env python3

"""
RabbitMQ Setup: Creates the exchange and queue for video processing microservice.
"""

import pika

# RabbitMQ connection settings
amqp_host = "localhost"
amqp_port = 5672

# Standardized exchange and queue settings
exchange_name = "video_processing_topic"  # Declared here for consistency
exchange_type = "topic"
queue_name = "Processed_Videos"
routing_key = "video.processed"

def create_exchange(channel):
    """Creates an exchange if it does not already exist."""
    print(f"Declaring exchange: {exchange_name} of type {exchange_type}")
    channel.exchange_declare(exchange=exchange_name, exchange_type=exchange_type, durable=True)

def create_queue(channel):
    """Creates and binds a queue to the exchange with a routing key."""
    print(f"Creating queue: {queue_name}")
    channel.queue_declare(queue=queue_name, durable=True)
    channel.queue_bind(exchange=exchange_name, queue=queue_name, routing_key=routing_key)

# Establish persistent connection to RabbitMQ
def init_rabbitmq():
    print(f"Connecting to RabbitMQ at {amqp_host}:{amqp_port}...")
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=amqp_host, port=amqp_port, heartbeat=300, blocked_connection_timeout=300)
    )
    print("Connected to RabbitMQ")
    
    channel = connection.channel()
    create_exchange(channel)
    create_queue(channel)
    
    return connection, channel  # Return open connection and channel

# Create a persistent connection and channel
connection, channel = init_rabbitmq()