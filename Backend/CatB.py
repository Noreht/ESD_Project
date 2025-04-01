import json
import pika
import requests
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))  # Ensure local import works
import rabbitmq.amqp_setup as amqp_setup  # Same setup used in VidProcRabbmq.py

# OutSystems API base URL
OUTSYSTEMS_BASE_URL = "https://personal-e6asw36f.outsystemscloud.com/VideoCategories/rest/RetrieveVideoCategories"

def insert_into_outsystems(video_id, category, email="zuwei@example.com"):
    """
    Calls OutSystems API to insert video + category.
    """
    url = f"{OUTSYSTEMS_BASE_URL}/InsertPersonal"
    payload = {
        "VideoId": video_id,
        "category": category,
        "email": email
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            print(f"Inserted into OutSystems: {video_id} - {category}")
        else:
            print(f"Failed to insert. Status: {response.status_code}")
            print("Response:", response.text)
    except Exception as e:
        print("Error while calling OutSystems:", str(e))

def callback(ch, method, properties, body):
    """
    RabbitMQ message handler.
    """
    try:
        print("Received message from RabbitMQ")
        data = json.loads(body)

        video_id = data.get("video")
        category = data.get("categories", "Uncategorized")

        if video_id:
            insert_into_outsystems(video_id, category)
        else:
            print("No video_id found in message:", data)

        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print("Error processing message:", str(e))
        ch.basic_nack(delivery_tag=method.delivery_tag)

def start_consuming():
    """
    Begin consuming messages from RabbitMQ.
    """
    queue_name = "video.processed"
    amqp_setup.channel.basic_consume(queue=queue_name, on_message_callback=callback)
    print(f"Listening for messages on queue '{queue_name}'...")
    amqp_setup.channel.start_consuming()

if __name__ == "__main__":
    print("Starting CatB listener...")
    start_consuming()
