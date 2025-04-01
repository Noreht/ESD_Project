# CatB.py
import pika
import json
import sqlite3  # Change to actual DB in production

# AMQP Connection setup
def callback(ch, method, properties, body):
    message = json.loads(body)
    video_id = message.get("video_id")
    categories = message.get("categories", [])  # Expected from video processing
    
    if video_id and categories:
        update_db(video_id, categories)

def update_db(video_id, categories):
    conn = sqlite3.connect('categories.db')  # Replace with actual DB
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO categories (video_id, category) VALUES (?, ?)", (video_id, ', '.join(categories)))
    conn.commit()
    conn.close()

# AMQP Consumer Setup
def start_consumer():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='categories_update')
    channel.basic_consume(queue='categories_update', on_message_callback=callback, auto_ack=True)
    print("[x] Waiting for messages...")
    channel.start_consuming()

if __name__ == '__main__':
    start_consumer()