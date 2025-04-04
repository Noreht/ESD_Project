# # event_broker.py
# import pika
# import json, os


# AMQP_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
# EVENT_BROKER_EXCHANGE = "event_broker_exchange"  # event_broker (step 3)

# # msg_to_event_broker = {
# #         'video_id': video_id,
# #         'album_id': album_id,
# #         'subscriber_list': new_subscriber_list, # Gotten from Supabase
# #         'input_person': input_person_email
# #     }




# sharedalbum_eventbroker.py
import pika
import json
import os
import time

AMQP_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
EVENT_BROKER_EXCHANGE = "event_broker_exchange"
QUEUE_NAME = "notifications_queue"  # the queue this broker listens to

def callback(ch, method, properties, body):
    print("\n[SharedAlbum_EventBroker] Received event from shared album:")
    print(json.loads(body))

    # Optionally, publish to another service or process the data

def start_listening():
    while True:
        try:
            RABBITMQ_USER = os.getenv("RABBITMQ_USER", "myuser")
            RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "mypassword")

            credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
            parameters = pika.ConnectionParameters(host="rabbitmq", credentials=credentials)
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()

            # Declare exchange and queue
            channel.exchange_declare(exchange=EVENT_BROKER_EXCHANGE, exchange_type="fanout", durable=True)
            channel.queue_declare(queue=QUEUE_NAME, durable=True)
            channel.queue_bind(exchange=EVENT_BROKER_EXCHANGE, queue=QUEUE_NAME)

            print("[SharedAlbum_EventBroker] Listening for events...")

            channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback, auto_ack=True)
            channel.start_consuming()

        except pika.exceptions.AMQPConnectionError as e:
            print(f"Connection failed: {e}, retrying in 5 seconds...")
            time.sleep(5)
        except Exception as e:
            print(f"Unexpected error: {e}, restarting in 5 seconds...")
            time.sleep(5)

def publish_to_event_broker(payload: dict):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=AMQP_HOST))
    channel = connection.channel()

    channel.exchange_declare(
        exchange=EVENT_BROKER_EXCHANGE, exchange_type="fanout", durable=True
    )

    EVENT_BROKER_QUEUE = "notifications_queue"  # listen to event_broker

    channel.basic_publish(
        exchange=EVENT_BROKER_EXCHANGE,
        routing_key=EVENT_BROKER_QUEUE,  # Fanout ignores this
        body=json.dumps(payload),
        properties=pika.BasicProperties(delivery_mode=2),  # Persistent message
    )

    print(
        "\n[SharedAlbum_EventBroker.py] User added new video to shared_album! (Step 3)\n"
    )
    connection.close()

if __name__ == "__main__":
    start_listening()

