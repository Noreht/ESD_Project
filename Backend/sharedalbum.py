from flask import Flask, jsonify
import requests
from dotenv import load_dotenv
import os

# Define shared_album dictionary
categories = {
    "Korea Travel": [
        "Shopping",
        "Food",
        "Landmarks",
        "Photo Worthy",
        "Hotel",
        "Music Bank",
        "Itinerary",
        "Instagrammable",
    ]
}


# TODO1 : Connect to Supabase (Shared Album DB) - Add video_id and Read

app = Flask(__name__)

load_dotenv()  # Load environment variables from .env file


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_KEY")


# TODO2: Return Text Array (Subcategories) to UI ('Korea Trip' shared album displays 'Food', 'Shopping'....)
# use 'http://127.0.0.1:5001/get_data' (Returns Subcategory List to UI)
@app.route("/get_data", methods=["GET"])
def get_data():
    # Use the correct table endpoint
    TABLE_NAME = "sharedalbum"  # Replace with your actual table name
    endpoint = f"{SUPABASE_URL}/rest/v1/{TABLE_NAME}"  # entire table

    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
    }

    album_id = "1"  #! Theron UI press Album_ID

    response = requests.get(
        endpoint,
        headers=headers,
        params={
            "select": "subcategory_list",
            "album_id": f"eq.{album_id}",  # Filter by album_id
        },
    )

    if response.status_code == 200:
        return jsonify(response.json()), 200

    else:
        return (
            jsonify({"error": "Failed to fetch data from Supabase"}),
            response.status_code,
        )


if __name__ == "__main__":
    app.run(debug=True, port=5001)


# TODO2: Exposes POST endpoint URL (Adds video_id ) x Supabase 


# TODO3: Publish message to RabbitMQ (Publish-Subscribe)
