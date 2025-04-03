# event_broker.py
import pika
import json, os


AMQP_HOST = os.getenv("RABBITMQ_HOST", "localhost")
EVENT_BROKER_EXCHANGE = "event_broker_exchange"  # event_broker (step 3)

# msg_to_event_broker = {
#         'video_id': video_id,
#         'album_id': album_id,
#         'subscriber_list': new_subscriber_list, # Gotten from Supabase
#         'input_person': input_person_email
#     }


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
