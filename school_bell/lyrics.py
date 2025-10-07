"""Utilities for generating school bell lyrics with Gemini."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Iterable, List

from google import genai
from google.genai.types import GenerateContentConfig, GoogleSearch, Tool

from .config import GeminiConfig


@dataclass
class Event:
    """Represents a single event surfaced for the school bell."""

    title: str
    description: str
    relevance: str


@dataclass
class LyricsResult:
    """Structured result returned by the lyrics generator."""

    lyrics: str
    events: List[Event]
    raw_response: str

    def to_dict(self) -> dict:
        return {
            "lyrics": self.lyrics,
            "events": [event.__dict__ for event in self.events],
            "raw_response": self.raw_response,
        }


class LyricsGenerator:
    """Wrapper around the Gemini API for deterministic prompting."""

    def __init__(self, config: GeminiConfig) -> None:
        self._config = config
        self._client = genai.Client(api_key=config.api_key)
        self._tool: Iterable[Tool] = ()
        if config.enable_search:
            self._tool = (Tool(google_search=GoogleSearch()),)

    def generate(self, target_date: date) -> LyricsResult:
        """Generate lyrics and event context for the given target date."""
        formatted_date = target_date.strftime("%d.%m.%Y")
        prompt = f"""
        הנחיות:
        1. חפש אירועים רלוונטיים ומשמעותיים שצפויים להתרחש בתאריך {formatted_date} בישראל.
        2. התמקד באירועים חברתיים, אזרחיים, חינוכיים, תרבותיים, דתיים ואקטואליים.
        3. לאחר התחקיר, צור צלצול בית ספר קצר עם 4-8 שורות בעברית, מתאים לכלל התלמידים.

        פורמט התשובה:
        החזר JSON תקין עם השדות הבאים בלבד:
        {{
            "events": [
                {{"title": "כותרת האירוע", "description": "פירוט קצר", "relevance": "מדוע זה חשוב לתלמידים"}}
            ],
            "lyrics": "שורות השיר מופרדות בשבירת שורה"
        }}

        אל תוסיף טקסט מחוץ למבנה ה-JSON. אם לא נמצאו אירועים מובהקים, הצע אירועים נושאיים כלליים והתאם את השיר.
        """

        response = self._client.models.generate_content(
            model=self._config.model,
            contents=prompt,
            config=GenerateContentConfig(
                tools=list(self._tool),
                response_modalities=["TEXT"],
            ),
        )

        raw_text = "\n".join(
            part.text for part in response.candidates[0].content.parts if hasattr(part, "text")
        )

        data = self._parse_raw_response(raw_text)
        events = [Event(**event_data) for event_data in data.get("events", [])]

        return LyricsResult(
            lyrics=data.get("lyrics", ""),
            events=events,
            raw_response=raw_text,
        )

    @staticmethod
    def _parse_raw_response(raw_text: str) -> dict:
        """Parse a JSON response from the model, handling minor formatting issues."""
        import json

        cleaned = raw_text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            if cleaned.lower().startswith("json"):
                cleaned = cleaned[4:]
        cleaned = cleaned.strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise ValueError(
                "Gemini response could not be parsed as JSON."
            ) from exc
