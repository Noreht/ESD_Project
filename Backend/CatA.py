from flask import Flask, request, jsonify
import requests
import pika
import json

app = Flask(__name__)

# === OutSystems API Setup ===
OUTSYSTEMS_BASE_URL = "https://personal-e6asw36f.outsystemscloud.com/VideoCategories/rest/RetrieveVideoCategories"
API_KEY = "YOUR_API_KEY_HERE"  # Replace with your actual API key

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

# === RabbitMQ Setup ===
amqp_host = "localhost"
exchange_name = "video_processing_topic"
routing_key = "video.raw"

connection = pika.BlockingConnection(pika.ConnectionParameters(host=amqp_host))
channel = connection.channel()
channel.exchange_declare(exchange=exchange_name, exchange_type='topic', durable=True)

# === OutSystems Functions ===
def video_exists(video_id, category, email):
    url = f"{OUTSYSTEMS_BASE_URL}/VideoExists"
    payload = {
        "VideoId": video_id,
        "category": category,
        "email": email
    }

    response = requests.post(url, json=payload, headers=HEADERS)
    if response.status_code == 200:
        return response.text.strip().lower() == "true"
    else:
        print("Error checking video existence:", response.status_code)
        print(response.text)
        return False

def insert_video(video_id, category, email):
    url = f"{OUTSYSTEMS_BASE_URL}/InsertPersonal"
    payload = {
        "VideoId": video_id,
        "category": category,
        "email": email
    }

    response = requests.post(url, json=payload, headers=HEADERS)
    if response.status_code == 200:
        print("Video inserted into OutSystems")
    else:
        print("Error inserting video:", response.status_code)
        print(response.text)

# === Main handler ===
def handle_video_post(video_id, email, category=""):
    if video_exists(video_id, category, email):
        print("Video already exists in OutSystems. Skipping insert.")
    else:
        print("Sending video to Video Processor...")
        message = {
            "video_id": video_id,
            "email": email
        }
        channel.basic_publish(
            exchange=exchange_name,
            routing_key=routing_key,
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        print("Message sent to RabbitMQ")

# === Route ===
@app.route('/post_video', methods=['POST'])
def post_video():
    data = request.get_json()
    print("Received JSON data:", data)

    video_id = data.get("video") or data.get("video_id")
    email = data.get("email")
    category = data.get("categories", "")

    if not video_id or not email:
        return jsonify({
            "error": "Missing video or email",
            "data_received": data
        }), 400

    handle_video_post(video_id, email, category)
    return jsonify({"message": "Video forwarded to processor"}), 200

# === Run app ===
if __name__ == "__main__":
    app.run(host='localhost', port=5001, debug=True)
