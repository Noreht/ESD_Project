from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

OUTSYSTEMS_BASE_URL = "https://personal-e6asw36f.outsystemscloud.com/VideoCategories/rest/RetrieveVideoCategories"

def video_exists(video_id, category, email):
    url = f"{OUTSYSTEMS_BASE_URL}/VideoExists"
    payload = {
        "VideoId": video_id,
        "category": category,
        "email": email
    }

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        return response.text.strip().lower() == "true"
    else:
        print("Error checking video existence:", response.status_code)
        print(response.text)
        return False  # Assume it doesn't exist if check fails

def insert_video(video_id, category, email):
    url = f"{OUTSYSTEMS_BASE_URL}/InsertPersonal"
    payload = {
        "VideoId": video_id,
        "category": category,
        "email": email
    }

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        print("Video inserted into OutSystems")
    else:
        print("Error inserting video:", response.status_code)
        print(response.text)

def handle_video_post(video_id, email, category=""):
    if video_exists(video_id, category, email):
        print("Video already exists in OutSystems. Skipping insert.")
    else:
        insert_video(video_id, category, email)

# === Route to handle POST from gateway ===
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
            "data_received": data  # debug payload
        }), 400

    handle_video_post(video_id, email, category)
    return jsonify({"message": "Video processed"}), 200

# === Start Flask App ===
if __name__ == "__main__":
    app.run(host='localhost', port=5001, debug=True)
