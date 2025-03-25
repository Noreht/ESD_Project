import cv2
import pytesseract
import json
import os
import pika
from flask import Flask, request, jsonify
from flask_cors import CORS
import rabbitmq.amqp_setup as amqp_setup  # Import RabbitMQ setup

app = Flask(__name__)
CORS(app)

# Define category dictionary
categories = {
    "Makeup": ["Makeup", "Soft Glam", "Full Glam", "Natural Look", "Foundation", "Concealer"],
    "Hair": ["Hair", "Hairstyle", "Hairstyles", "Updo", "Haircut", "Sleek Bun"],
    "Pageant": ["Pageant", "Miss Universe", "Miss Teen Earth", "Miss Grand", "Miss India", "Philippines", "Vietnam", "Thailand", "Nicaragua", "Catriona", "Harnaaz", "Rachel Gupta", "Pose", "Power Pose"],
    "Rampwalk": ["Rampwalk", "Runway", "Pose", "Ramp", "Catwalk", "Pageant Walk", "Stage Walk"],
    "Food": ["Food", "Recipes", "Breakfast", "Lunch", "Dinner", "Eat", "Vegan", "Vegetarian", "Dessert", "Cooking Tips"],
    "Travel": ["Travel", "Destination", "Airport", "Flight", "Visa", "Resort", "Backpacking", "Road Trip"],
    "Motivational": ["Motivational", "Insecurity", "Confidence", "Vision Board", "Productivity", "Planning", "Mindset", "Self-Improvement", "Success"],
    "Workout": ["Workout", "Abs", "Arms", "Workout Routine", "Leg Day", "Pilates", "At-Home Workout", "Cardio", "Reps"],
    "Dance": ["Dance", "Choreography", "Dance Cover", "Freestyle", "Ballet", "Hip-Hop", "Salsa", "TikTok Dance"],
    "Photography": ["Photography" , "Portrait", "Lighting", "Camera Tricks", "Aesthetic Shots", "Photo Editing"],
    "Filming": ["Film", "Filming", "Cinematography", "Filmmaking", "Video Editing", "B-roll", "Transitions", "Reel Ideas"],
    "Skincare": ["Skincare", "SPF", "Moisturizer", "Serum", "Face Mask", "Hydration"],
    "Fashion": ["Fashion", "Outfit", "Outfits", "OOTD", "Trendy", "Style Inspo", "Wardrobe Essentials"],
    "Wellness": ["Self-Care", "Mental Health", "Wellness", "Journaling", "Meditation", "Meditate", "Self-Love"],
    "ASMR": ["ASMR", "Satisfying", "Whispers", "Relaxing Sounds", "Tingles", "Triggers"],
    "Finance": ["Finance", "Investing", "Savings", "Budgeting", "Passive Income", "Financial Freedom"],
    "Tech": ["Tech", "Gadgets", "Tech Review", "Coding", "Cybersecurity"],
    "Pets": ["Pets", "Dog", "Cat", "Pet Care", "Funny Animals", "Adopt Don't Shop"],
    "Comedy": ["Comedy", "Funny", "Relatable", "Meme", "Humor", "Parody", "Joke"],
    "Study Tips": ["Education", "Study", "Study Tips", "Learning Hacks", "Exam Prep", "Educational Content"]
}

def process_video(video_path):
    """
    Process the given video file and return detected categories.
    """
    vidcap = cv2.VideoCapture(video_path)
    fps = vidcap.get(cv2.CAP_PROP_FPS)
    frame_interval = int(fps * 0.2)  # Process every 200ms

    detected_categories = set()
    last_text = ""

    frame_count = 0
    while True:
        success, image = vidcap.read()
        if not success:
            break

        if frame_count % frame_interval == 0:
            gray_frame = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            _, thresh_frame = cv2.threshold(gray_frame, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            # Use OCR (Tesseract) to extract text from the frame
            extracted_text = pytesseract.image_to_string(gray_frame)

            # Use Tesseract's image_to_data to check if there's any text
            ocr_data = pytesseract.image_to_data(thresh_frame, output_type=pytesseract.Output.DICT)
            extracted_text = " ".join(ocr_data['text']).strip()

            # Only process if text is detected & different from the last detected text
            if extracted_text and extracted_text != last_text:
                last_text = extracted_text  # Store last text to avoid duplicates

                # Check for matching categories
                for category, words in categories.items():
                    if any(word.lower() in extracted_text.lower() for word in words):
                        detected_categories.add(category)

        frame_count += 1

    vidcap.release()

    # Assign category (if multiple categories are found, return all)
    assigned_categories = ",".join(detected_categories) if detected_categories else "Uncategorized"

    return assigned_categories

@app.route("/process_video", methods=["POST"])
def handle_video_processing():
    if request.is_json:
        try:
            video_data = request.get_json()
            video_path = video_data.get("video_path")  # Expecting video_path in JSON

            if not video_path or not os.path.exists(video_path):
                return jsonify({"code": 400, "message": "Invalid video path"}), 400

            print(f"\nProcessing video: {video_path}")
            detected_categories = process_video(video_path)

            # Prepare result
            processed_result = {
                "video": video_path,
                "categories": detected_categories
            }

            # Publish result to RabbitMQ
            print("Publishing message to RabbitMQ with routing_key='video.processed'")
            amqp_setup.channel.basic_publish(
                exchange=amqp_setup.exchange_name,
                routing_key="video.processed",
                body=json.dumps(processed_result),
                properties=pika.BasicProperties(delivery_mode=2)  # Persistent message
            )

            return jsonify({"code": 200, "message": "Video processed successfully", "data": processed_result}), 200

        except Exception as e:
            print("Error:", str(e))
            return jsonify({"code": 500, "message": "Internal Server Error"}), 500

    return jsonify({"code": 400, "message": "Invalid JSON input"}), 400

if __name__ == "__main__":
    print("Starting Video Processing Service...")
    app.run(host="0.0.0.0", port=5200, debug=True)
