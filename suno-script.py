import requests
import time
import sys
import json
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

# Load API token from .env
load_dotenv()
SUNO_API_TOKEN = os.getenv("SUNO_API_TOKEN")
if not SUNO_API_TOKEN: 
    print("Error: 'TOKEN' not found in .env file.")
    sys.exit(1)

# API endpoints
CREATE_TASK_URL = "https://apibox.erweima.ai/api/v1/generate"
STATUS_URL = "https://apibox.erweima.ai/api/v1/generate/record-info?taskId={task_id}"

# Check for required command-line argument
# if len(sys.argv) < 2:
#     print("Usage: python script.py \"your lyrics here\" [output_file.mp3]")
#     sys.exit(1)

# Headers for API requests
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Authorization": f"Bearer {SUNO_API_TOKEN}"
}

# Payload for task creation
PAYLOAD = {
  "prompt": "שיר קצר, עליז, פזמון קליט, קצב גבוה, תופים, טכנו, צלצול לבית הספר אורט הנרי רונסון לכבוד חג פורים השמח",
  "style": "Israeli Pop, High BPM, Drums, Beat, Techno",
  "title": "ORT ISRAEL",
  "customMode": True,
  "instrumental": False,
  "model": "V4",
  "callBackUrl": "https://api.example.com/callback" #TODO: change to actual callback url
}
# Save the response data
def save_response_logs(response):
    if response.status_code == 200:
        data = response.json()
        task_id = data["data"]["taskId"]
        dir_path = task_id
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
        file_path = os.path.join(dir_path, "status_response.json")
        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)
        print(f"Status response saved to {file_path}")
    else:
        print(f"Failed to get status response: {response.status_code}")

# Create audio generation task
create_response = requests.post(CREATE_TASK_URL, headers=HEADERS, json=PAYLOAD)
if create_response.status_code != 200:
    print(f"Task creation failed: {create_response.text}")
    sys.exit(1)

task_id = create_response.json()["data"]["taskId"]
print(f"Task ID: {task_id}")

# Check task status with timeout
MAX_CHECKS = 5          # Maximum number of status checks
CHECK_INTERVAL = 60      # Seconds between checks
TIMEOUT = MAX_CHECKS * CHECK_INTERVAL  # Total timeout in seconds

time.sleep(CHECK_INTERVAL)
for _ in range(MAX_CHECKS):
    status_response = requests.get(STATUS_URL.format(task_id=task_id), headers=HEADERS)
    if status_response.status_code == 200:
        status = status_response.json()["data"]["status"]
        if status == "SUCCESS":
            break
        elif status == "PENDING" or "SUCCESS" in status:
            print(f"Status: {status}. Waiting {CHECK_INTERVAL} seconds...")
            time.sleep(CHECK_INTERVAL)
        else:
            print("Task failed. Status: ", status)
            sys.exit(1) 
    else:
        print(f"Status check failed: {status_response.text}")
        sys.exit(1)
else:
    print(f"Timeout: Task not completed within {TIMEOUT} seconds.")
    sys.exit(1)

# Create folder name with tomorrow's date and version
tomorrow = datetime.now() + timedelta(days=1)
for version in [1, 2]:
    folder_name = tomorrow.strftime("%d-%m-%y") + f"-{version}"
    os.makedirs(folder_name, exist_ok=True)

    # Get audio and image URLs for this version
    song_data = status_response.json()["data"]["response"]["sunoData"][version-1]
    audio_url = song_data["audioUrl"]
    image_url = song_data["imageUrl"]

    # Download and save audio file
    audio_response = requests.get(audio_url)
    if audio_response.status_code == 200:
        audio_path = os.path.join(folder_name, "song.mp3")
        with open(audio_path, "wb") as f:
            f.write(audio_response.content)
        print(f"Saved audio to {audio_path}")

    # Download and save image file  
    image_response = requests.get(image_url)
    if image_response.status_code == 200:
        image_path = os.path.join(folder_name, "cover.jpeg")
        with open(image_path, "wb") as f:
            f.write(image_response.content)
        print(f"Saved image to {image_path}")
