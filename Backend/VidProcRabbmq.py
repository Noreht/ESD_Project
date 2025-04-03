import cv2
import pytesseract
import json
import os
import pika
import rabbitmq.amqp_setup as amqp_setup  # Assuming you have this setup file

# Define category dictionaries
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

# New dictionary for Scenario 2 categories
scenario2_categories = {
    "Travel": [
        "Shopping", "Food", "Landmarks", "Photo Worthy", "Hotel", 
        "Music Bank", "Itinerary", "Instagrammable"
    ]
}

# Define the different queues to consume from
VIDEO_PROCESSING_QUEUE = "video_processing_queue"
SCENARIO_2_VIDEO_PROCESSING_QUEUE = "scenario_2_video_processing_queue"


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
    print(assigned_categories)
    return assigned_categories

def scenario2_process_video(video_path):
    """
    Process the video for scenario 2 (looking for specific categories like "Shopping", "Food", etc.).
    """
    vidcap = cv2.VideoCapture(video_path)
    
    # Read the first frame
    success, image = vidcap.read()

    # Store detected categories
    detected_categories = set()

    while success:
        # Convert to grayscale
        gray_frame = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        _, thresh_frame = cv2.threshold(gray_frame, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        # Use OCR (Tesseract) to extract text from the frame
        extracted_text = pytesseract.image_to_string(gray_frame)

        # Check if extracted text contains any words from scenario2_categories
        for category, words in scenario2_categories.items():
            for word in words:
                if word.lower() in extracted_text.lower():
                    detected_categories.add(word)  # Add the matching word

        # Read the next frame
        success, image = vidcap.read()

    # Release the video capture object when done
    vidcap.release()

    # Assign category (if multiple categories are found, return all)
    assigned_categories = ",".join(detected_categories) if detected_categories else "Uncategorized"

    # Create the JSON object with video path (later this will be URL)
    result = {"video_id": video_path, "album_id": album_id, "categories": assigned_categories, "email_id": input_person_email}

    # Print the JSON output (later this will be sent via AMQP)
    print("Extracted Text:", extracted_text)
    print(json.dumps(result, indent=4))

def callback(ch, method, properties, body):
    """
    Callback function to process messages from the RabbitMQ queue.
    """
    message = json.loads(body)
    video_id = message.get("video_id")
    album_id = message.get("album_id")
    input_person_email = message.get("email")

    print(message)

    if video_id:
        print(f"Received video ID: {video_id}")
        if method.routing_key == "video.to_process":
            video_path = "../Frontend/src/assets/videos/" + video_id  # For testing purposes
            print("Video Path", video_path)
            detected_categories = process_video(video_path)

            # Prepare result for video processing
            processed_result = {
                "video_id": video_id,
                "categories": detected_categories, 
                "email": input_person_email
            }

            # Publish result to RabbitMQ (or handle as needed)
            print("Publishing message to RabbitMQ with routing_key='video.processed'")
            amqp_setup.channel.basic_publish(
                exchange=amqp_setup.exchange_name,
                routing_key="video.processed",
                body=json.dumps(processed_result),
                properties=pika.BasicProperties(delivery_mode=2)  # Persistent message
            )
        elif method.routing_key == SCENARIO_2_VIDEO_PROCESSING_QUEUE:
            # Scenario 2 specific processing
            result = scenario2_process_video(video_id)
            print("Scenario 2 processing result:", result)
            # Publish or handle the result accordingly
            amqp_setup.channel.basic_publish(
                exchange=amqp_setup.exchange_name,
                routing_key="scenario_2.processed",
                body=json.dumps(result),
                properties=pika.BasicProperties(delivery_mode=2)  # Persistent message
            )

def start_consuming():
    """
    Start the RabbitMQ consumer to listen for incoming messages.
    """
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # Declare the queues to listen on
    channel.queue_declare(queue=VIDEO_PROCESSING_QUEUE)
    channel.queue_declare(queue=SCENARIO_2_VIDEO_PROCESSING_QUEUE)

    # Start consuming messages from both queues
    channel.queue_bind(queue=VIDEO_PROCESSING_QUEUE,exchange="video_processing_topic", routing_key="video.to_process")
    channel.basic_consume(queue=VIDEO_PROCESSING_QUEUE, on_message_callback=callback, auto_ack=True)

    channel.basic_consume(queue=SCENARIO_2_VIDEO_PROCESSING_QUEUE, on_message_callback=callback, auto_ack=True)

    print(VIDEO_PROCESSING_QUEUE)
    print(SCENARIO_2_VIDEO_PROCESSING_QUEUE)

    print("Waiting for messages from both queues...")
    channel.start_consuming()

if __name__ == "__main__":
    print("Starting Video Processing Service...")
    start_consuming()

