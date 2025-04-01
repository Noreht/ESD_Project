import requests

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
        return False  # Assume it doesn't exist if the check fails

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
    # Step 1: Check if it exists
    exists = video_exists(video_id, category, email)

    if exists:
        print("Video already exists in OutSystems. Skipping insert.")
    else:
        # Step 2: Insert if it doesn't exist
        insert_video(video_id, category, email)
