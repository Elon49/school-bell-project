# ORT Henry Ronson - AI School Bell Generator

## Description

This project automatically generates a unique, daily school bell song for ORT Henry Ronson High School. It leverages Artificial Intelligence to create lyrics based on upcoming events in Israel and then generates music for those lyrics using another AI service. The goal is to provide a fresh and relevant school bell each day.

## How it Works

The project consists of two main Python scripts which are now fully integrated:

1.  **`google_ai_script.py`**
    *   Uses the Google Gemini AI model (`gemini-2.0-flash`) via the `google-generativeai` library.
    *   Performs a Google Search to find significant national, cultural, religious, political, or current events expected to occur the *next day* in Israel.
    *   Prompts the AI to write short, catchy lyrics (4‑8 lines) suitable for a school bell, based on the identified events.
    *   Can be executed on its own to print the generated lyrics.

2.  **`suno_script.py`**
    *   Automatically calls `google_ai_script.generate_lyrics()` to obtain lyrics.
    *   Uses an external API (hosted at `apibox.erweima.ai`, likely a wrapper for Suno AI) to generate music.
    *   Sends a request to the API with the generated lyrics, a configurable style prompt, title and other parameters.
    *   Polls the API to check the status of the generation task.
    *   Once successful, downloads the generated audio (`song.mp3`) and cover image (`cover.jpeg`).
    *   Saves the files into a new directory named according to the *next day's date* and a version number (e.g., `DD-MM-YY-1`).

Running `suno_script.py` automatically generates lyrics and music in one step.

## Features

*   Automated daily generation of school bell songs.
*   Lyrics based on relevant, upcoming events in Israel.
*   Music generation using AI.
*   Integration with Google AI (Gemini) and Suno AI (via API).
*   Organized output into date-stamped folders.

## Setup

1.  **Clone the repository (if applicable):**
    ```bash
    git clone <repository_url>
    cd school-bell-project
    ```

2.  **Install dependencies:**
    Make sure you have Python 3 installed. Then install all packages listed in `requirements.txt`:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Environment Variables:**
    Create a file named `.env` in the `school-bell-project` directory. Add your API keys and optional configuration values:
    ```dotenv
    # .env
    SUNO_API_TOKEN="YOUR_SUNO_API_TOKEN_HERE"
    GEMINI_API_KEY="YOUR_GOOGLE_AI_API_KEY_HERE"
    # Optional overrides
    SUNO_STYLE_PROMPT="Israeli Pop, High BPM, Drums, Beat, Techno"
    SUNO_TITLE="ORT ISRAEL"
    ```
    *   Replace `"YOUR_SUNO_API_TOKEN_HERE"` with your token for the `apibox.erweima.ai` API used in `suno_script.py`.
    *   Replace `"YOUR_GOOGLE_AI_API_KEY_HERE"` with your Google AI (Gemini) API key used in `google_ai_script.py`.

## Usage

To generate a bell manually simply run:
```bash
python suno_script.py
```
The script will generate lyrics and music automatically and save the files into a new folder named after tomorrow's date.

## Folder Structure

*   `.env`: Stores API keys (should be ignored by git).
*   `.gitignore`: Specifies files/directories to be ignored by git (like `.env`).
*   `google_ai_script.py`: Script to generate lyrics using Google AI.
*   `suno_script.py`: Script to generate music using the Suno API.
*   `run_daily.py`: Optional scheduler script that runs the generation each morning.
*   `DD-MM-YY-V/`: Directories created by `suno-script.py` (e.g., `04-03-25-1`).
    *   `song.mp3`: The generated audio file.
    *   `cover.jpeg`: The generated cover image.
    *   `status_response.json`: (Optional, if `save_response_logs` is used) Logs from the API.

## Dependencies

*   Python 3.x
*   `requests`: For making HTTP requests to the Suno API.
*   `python-dotenv`: For loading environment variables from the `.env` file.
*   `google-generativeai`: The official Google AI Python SDK for Gemini.
*   `schedule`: For optional daily execution via `run_daily.py`.

## TODO / Future Improvements

*   **Callback URL:** Implement a proper callback URL (`callBackUrl` in `suno_script.py`) if needed for asynchronous notifications from the Suno API.
*   **Refine Prompts:** Continue experimenting with prompts for both Google AI and the Suno API to improve the quality and relevance of the generated bells.
