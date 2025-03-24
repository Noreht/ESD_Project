




#! The below is just to simulate categories subscirbing to event broker (listen to queue for fanout exchange in event broker)

# categories.py
import pika
import json, os 

AMQP_HOST = os.getenv("RABBITMQ_HOST", "localhost") #! Dun change
EXCHANGE_NAME = "event_broker_exchange"  #! Dun change
QUEUE_NAME = "categories_queue" #! Dun change

def callback(ch, method, properties, body):
    message = json.loads(body)
    print("[Categories] ✅ Received new video data:")
    print(json.dumps(message, indent=2))
    
    # Simulate categorisation logic
    print(f"[Categories] Processing video_id: {message['video_id']} for categorisation...")

connection = pika.BlockingConnection(pika.ConnectionParameters(host=AMQP_HOST))
channel = connection.channel()


 #! Dun change anyth below 
channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type="fanout", durable=True)
channel.queue_declare(queue=QUEUE_NAME, durable=True)
channel.queue_bind(exchange=EXCHANGE_NAME, queue=QUEUE_NAME)

channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback, auto_ack=True)

print("[Categories] 🟢 Waiting for messages. To exit press CTRL+C")
channel.start_consuming()
