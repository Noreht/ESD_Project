import cv2
import pytesseract
import json
import os
import pika
import rabbitmq.amqp_setup as amqp_setup  # Import RabbitMQ setup

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

def callback(ch, method, properties, body):
    """
    Callback function to process messages from the RabbitMQ queue.
    """
    message = json.loads(body)
    video_id = message.get("video_id")
    email = message.get("email")  # Get email from the incoming message

    if video_id and email:
        print(f"Received video ID: {video_id} for email: {email}")
        video_path = video_id  # For testing purposes
        detected_categories = process_video(video_path)

        # Prepare result to send to CatB
        processed_result = {
            "video": video_id,
            "categories": detected_categories,
            "email": email  # Include email for CatB to use
        }

        print("Publishing message to RabbitMQ with routing_key='video.processed'")
        amqp_setup.channel.basic_publish(
            exchange=amqp_setup.exchange_name,
            routing_key="video.processed",
            body=json.dumps(processed_result),
            properties=pika.BasicProperties(delivery_mode=2)
        )
    else:
        print("Missing video_id or email in incoming message:", message)


def start_consuming():
    """
    Start the RabbitMQ consumer to listen for incoming messages.
    """
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # Declare the queue to listen on
    channel.queue_declare(queue='video_processing')

    # Start consuming messages from the queue
    channel.basic_consume(queue='video_processing', on_message_callback=callback, auto_ack=True)

    print("Waiting for messages...")
    channel.start_consuming()

if __name__ == "__main__":
    print("Starting Video Processing Service...")
    start_consuming()
