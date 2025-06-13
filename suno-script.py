import logging
import requests
import time
import sys
import json
import os
from datetime import datetime, timedelta
from typing import Optional

import config
from google_ai_script import generate_lyrics

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Authorization": f"Bearer {config.SUNO_API_TOKEN}"
}


def create_task(lyrics: str) -> Optional[str]:
    payload = {
        "prompt": lyrics,
        "style": config.STYLE_PROMPT,
        "title": config.DEFAULT_TITLE,
        "customMode": True,
        "instrumental": False,
        "model": "V4",
    }
    if config.CALLBACK_URL:
        payload["callBackUrl"] = config.CALLBACK_URL

    try:
        response = requests.post(config.CREATE_TASK_URL, headers=HEADERS, json=payload)
        response.raise_for_status()
        task_id = response.json()["data"]["taskId"]
        logging.info("Task created: %s", task_id)
        return task_id
    except Exception as exc:
        logging.error("Task creation failed: %s", exc)
        return None


def wait_for_task(task_id: str, max_checks: int = 5, interval: int = 60) -> Optional[dict]:
    for _ in range(max_checks):
        try:
            status_resp = requests.get(config.STATUS_URL.format(task_id=task_id), headers=HEADERS)
            status_resp.raise_for_status()
            data = status_resp.json()["data"]
            status = data["status"]
            if status == "SUCCESS":
                logging.info("Task succeeded")
                return data
            elif status == "PENDING" or "SUCCESS" in status:
                logging.info("Status: %s. Waiting %s seconds...", status, interval)
                time.sleep(interval)
            else:
                logging.error("Task failed. Status: %s", status)
                return None
        except Exception as exc:
            logging.error("Status check failed: %s", exc)
            return None
    logging.error("Timeout waiting for task completion")
    return None


def download_files(data: dict) -> None:
    tomorrow = datetime.now() + timedelta(days=1)
    for version, song_data in enumerate(data["response"]["sunoData"], start=1):
        folder_name = tomorrow.strftime("%d-%m-%y") + f"-{version}"
        os.makedirs(folder_name, exist_ok=True)
        audio_url = song_data["audioUrl"]
        image_url = song_data["imageUrl"]
        try:
            audio_resp = requests.get(audio_url)
            audio_resp.raise_for_status()
            with open(os.path.join(folder_name, "song.mp3"), "wb") as f:
                f.write(audio_resp.content)
            logging.info("Saved audio to %s/song.mp3", folder_name)
        except Exception as exc:
            logging.error("Failed to download audio: %s", exc)

        try:
            image_resp = requests.get(image_url)
            image_resp.raise_for_status()
            with open(os.path.join(folder_name, "cover.jpeg"), "wb") as f:
                f.write(image_resp.content)
            logging.info("Saved image to %s/cover.jpeg", folder_name)
        except Exception as exc:
            logging.error("Failed to download image: %s", exc)


def main():
    lyrics = generate_lyrics()
    if not lyrics:
        logging.error("No lyrics generated. Exiting.")
        return

    task_id = create_task(lyrics)
    if not task_id:
        return

    data = wait_for_task(task_id)
    if not data:
        return

    download_files(data)


if __name__ == "__main__":
    if not config.SUNO_API_TOKEN:
        logging.error("SUNO_API_TOKEN not set")
        sys.exit(1)
    main()
