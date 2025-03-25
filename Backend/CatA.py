# CatA.py
from flask import Flask, request, jsonify
import pika
import json
import sqlite3  # Change to actual DB in production
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(
    app,
    resources={
        r"/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE"],
            "allow_headers": "Content-Type,Authorization",
        }
    },
)
# AMQP Connection setup
def publish_to_queue(video_id):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='video_processing')
    message = json.dumps({"video_id": video_id})
    channel.basic_publish(exchange='', routing_key='video_processing', body=message)
    connection.close()

# DB Check Function
def check_categories(video_id):
    conn = sqlite3.connect('categories.db')  # Replace with actual DB
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM categories WHERE video_id = ?", (video_id,))
    result = cursor.fetchone()[0]
    conn.close()
    return result > 0

@app.route('/post_video', methods=['POST'])
@cross_origin() 
def receive_video():
    data = request.get_json()
    video_id = data.get("video_id")
    
    if not video_id:
        return jsonify({"error": "Missing video_id"}), 400
    
    if not check_categories(video_id):
        publish_to_queue(video_id)
    
    return jsonify({"message": "Processing started"})

if __name__ == '__main__':
    app.run(debug=True)