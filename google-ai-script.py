from google import genai
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch
import os

GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GOOGLE_API_KEY)
model_id = "gemini-2.0-flash"

google_search_tool = Tool(
    google_search = GoogleSearch()
)

response = client.models.generate_content(
    model=model_id,
    contents = """
אני מבקש ממך לבצע חיפוש מעמיק וממוקד על אירועים חשובים שצפויים להתרחש מחר בישראל, 
תוך התמקדות בהיבטים לאומיים, תרבותיים, דתיים, פוליטיים ואקטואליים הרלוונטיים למציאות הישראלית. 
השתמש במידע עדכני זמין עד תאריך הידע שלך, חפש ברשת או בנתונים זמינים 
אחרים כדי לאסוף פרטים על מאורעות משמעותיים. לאחר מכן, כתוב שיר קצר (4-8 שורות) שישמש כטקסט 
לצלצול בית ספר, המשלב את האירועים שמצאת בצורה יצירתית, קליטה ומתאימה לתלמידים, תוך שמירה על 
קשר ישיר לאקטואליה ולזיקה הישראלית.
""",
    config=GenerateContentConfig(
        tools=[google_search_tool],
        response_modalities=["TEXT"],
    )
)

for each in response.candidates[0].content.parts:
    print(each.text)
# Example response:
# The next total solar eclipse visible in the contiguous United States will be on ...

# To get grounding metadata as web content.
# print(response.candidates[0].grounding_metadata.search_entry_point.rendered_content)