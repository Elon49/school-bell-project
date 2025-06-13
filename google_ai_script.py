import logging
from google import genai
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch
from typing import Optional
import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def generate_lyrics() -> Optional[str]:
    """Generate lyrics for tomorrow's school bell using Google Gemini."""
    if not config.GEMINI_API_KEY:
        logging.error("GEMINI_API_KEY not set")
        return None

    try:
        client = genai.Client(api_key=config.GEMINI_API_KEY)
        google_search_tool = Tool(google_search=GoogleSearch())
        response = client.models.generate_content(
            model=config.GEMINI_MODEL_ID,
            contents="""
אני מבקש ממך לבצע חיפוש מעמיק וממוקד על אירועים חשובים שצפויים להתרחש מחר בישראל,
תוך התמקדות בהיבטים לאומיים, תרבותיים, דתיים, פוליטיים ואקטואליים הרלוונטיים למציאות הישראלית.
השתמש במידע עדכני זמין עד תאריך הידע שלך, חפש ברשת או בנתונים זמינים אחרים כדי לאסוף פרטים על מאורעות משמעותיים.
לאחר מכן, כתוב שיר קצר (4-8 שורות) שישמש כטקסט לצלצול בית ספר, המשלב את האירועים שמצאת בצורה יצירתית, קליטה ומתאימה לתלמידים,
תוך שמירה על קשר ישיר לאקטואליה ולזיקה הישראלית.
""",
            config=GenerateContentConfig(
                tools=[google_search_tool],
                response_modalities=["TEXT"],
            )
        )
        lyrics = "\n".join(part.text for part in response.candidates[0].content.parts)
        logging.info("Lyrics generated successfully")
        return lyrics
    except Exception as exc:
        logging.error("Failed to generate lyrics: %s", exc)
        return None


if __name__ == "__main__":
    lyrics = generate_lyrics()
    if lyrics:
        print(lyrics)
