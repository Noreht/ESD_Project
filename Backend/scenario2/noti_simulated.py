import pika
import json
import os

AMQP_HOST = os.getenv("RABBITMQ_HOST", "localhost")
SHARED_ALBUM_EXCHANGE = "shared_album_exchange"  # sent by shared_album (step 9)
SHARED_ALBUM_QUEUE = "shared_album_queue"  # listen to shared_album

EVENT_BROKER_EXCHANGE = "event_broker_exchange"  # event_broker (step 3)
EVENT_BROKER_QUEUE = "notifications_queue"  # listen to event_broker


def callback(ch, method, properties, body):
    message = json.loads(body)

    # Determine which queue the message came from based on the queue name
    if method.routing_key == SHARED_ALBUM_QUEUE:
        print("📸 Received new video data from []:")
        print(json.dumps(message, indent=2))

        print(f"[Notification Microservice] sending to {message['subscriber_list']}")

        print(
            f"New video added into Shared Album ({message['shared_album_name']}), under subcategory {message['new_vid_subcategory']}. Check your updated {message['shared_album_name']}"
        )

    elif method.routing_key == EVENT_BROKER_QUEUE:
        print("\n🔔 Received new video data from [Event Broker]:")
        print(json.dumps(message, indent=2))

        print(f"[Notification Microservice] sending to {message['subscriber_list']}...")
        print(
            f"New video added into Shared Album ({message['album_id']}). Autocategorisation in progress... Please check later for categories into {message['album_id']}"
        )


connection = pika.BlockingConnection(pika.ConnectionParameters(host=AMQP_HOST))
channel = connection.channel()

# Declare the two exchanges for event broker and shared album
channel.exchange_declare(
    exchange=EVENT_BROKER_EXCHANGE, exchange_type="fanout", durable=True
)
channel.exchange_declare(
    exchange=SHARED_ALBUM_EXCHANGE, exchange_type="fanout", durable=True
)

# Declare separate queues for event broker and shared album messages
channel.queue_declare(queue=EVENT_BROKER_QUEUE, durable=True)
channel.queue_declare(queue=SHARED_ALBUM_QUEUE, durable=True)

# Bind the appropriate queues to the exchanges
channel.queue_bind(exchange=EVENT_BROKER_EXCHANGE, queue=EVENT_BROKER_QUEUE)
channel.queue_bind(exchange=SHARED_ALBUM_EXCHANGE, queue=SHARED_ALBUM_QUEUE)

# Start consuming from the notifications queue (which listens to the event_broker_exchange)
channel.basic_consume(
    queue=SHARED_ALBUM_QUEUE, on_message_callback=callback, auto_ack=True
)

# Start consuming from shared_album_queue (which listens to shared_album)
channel.basic_consume(
    queue=EVENT_BROKER_QUEUE, on_message_callback=callback, auto_ack=True
)


print(
    "[Notifications] 🟢 Waiting for messages from shared_album... To exit press CTRL+C"
)

print(
    "[Notifications] 🟢 Waiting for messages from event_broker_exchange... To exit press CTRL+C"
)


channel.start_consuming()
