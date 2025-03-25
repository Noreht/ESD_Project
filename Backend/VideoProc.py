import cv2
import pytesseract
import json

# Define the dictionary with category tags and related words
categories = {
    "Makeup": ["Makeup", "Soft Glam", "Full Glam", "Natural Look", "Foundation", "Concealer"],
    "Hair": ["Hair", "Hairstyle", "Hairstyles", "Updo", "Haircut", "Sleek Bun"],
    "Pageant": ["Pageant", "Miss Universe", "Miss Teen Earth", "Miss Grand", "Miss India", "Philippines", "Vietnam", "Thailand", "Nicaragua", "Catriona", "Harnaaz", "Rachel Gupta", "Pose", "Power Pose"],
    "Rampwalk": ["Rampwalk", "Runway", "Pose", "Ramp", "Catwalk", "Pageant Walk", "Stage Walk"],
    "Food": ["Food", "Recipes", "Breakfast", "Lunch", "Dinner", "Eat", "Vegan", "Vegetarian", "Dessert", "Cooking Tips"],
    "Travel": ["Travel", "Destination", "Airport", "Flight", "Visa", "Resort", "Backpacking", "Road Trip"],
    "Motivational": ["Motivational", "Insecurity", "Confidence", "Vision Board", "Productivity", "Planning", "Mindset", "Self-Improvement"],
    "Workout": ["Workout", "Abs", "Arms", "Workout Routine", "Leg Day", "Pilates", "At-Home Workout", "Cardio"],
    "Dance": ["Dance", "Choreography", "Dance Cover", "Freestyle", "Ballet", "Hip-Hop", "Salsa", "TikTok Dance"],
    "Photography": ["Photography", "Portrait", "Lighting", "Camera Tricks", "Aesthetic Shots", "Photo Editing"],
    "Filming": ["Filming", "Cinematography", "Filmmaking", "Video Editing", "B-roll", "Transitions", "Reel Ideas"],
    "Skincare": ["Skincare", "SPF", "Moisturizer", "Serum", "Face Mask", "Hydration"],
    "Fashion": ["Fashion", "Outfit", "OOTD", "Trendy", "Style Inspo", "Wardrobe Essentials"],
    "Self-Care": ["Self-Care", "Mental Health", "Wellness", "Journaling", "Meditation", "Self-Love"],
    "ASMR": ["ASMR", "Satisfying", "Whispers", "Relaxing Sounds", "Tingles", "Triggers"],
    "Finance": ["Finance", "Investing", "Savings", "Budgeting", "Passive Income", "Financial Freedom"],
    "Tech": ["Tech", "Gadgets", "Tech Review", "Coding", "Cybersecurity"],
    "Pets": ["Pets", "Dogs", "Cats", "Pet Care", "Funny Animals", "Adopt Don't Shop"],
    "Comedy": ["Comedy", "Funny", "Relatable", "Meme", "Humor", "Parody"],
    "Education": ["Education", "Study Tips", "Learning Hacks", "Exam Prep", "Educational Content"]
}

# Load the video (replace with URL-based processing later)
video_path = "dummy_videos/Hair/Updo.mp4"
vidcap = cv2.VideoCapture(video_path)

# Read the first frame
success, image = vidcap.read()

# Store detected categories
detected_categories = set()

# Loop through the frames
while success:
    # Convert the frame to grayscale (optional, improves OCR accuracy)
    gray_frame = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Use OCR (Tesseract) to extract text from the frame
    extracted_text = pytesseract.image_to_string(gray_frame)
    
    # Check if extracted text contains any words from the categories
    for category, words in categories.items():
        for word in words:
            if word.lower() in extracted_text.lower():
                detected_categories.add(category)
    
    # Read the next frame
    success, image = vidcap.read()

# Release the video capture object when done
vidcap.release()

# Assign category (if multiple categories are found, return all)
assigned_categories = list(detected_categories) if detected_categories else ["Uncategorized"]

# Create the JSON object with video path (later this will be URL)
result = {
    "video": video_path,
    "categories": assigned_categories
}

# Print the JSON output (later this will be sent via AMQP)
print(json.dumps(result, indent=4))
