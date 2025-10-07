"""Legacy helper for generating lyrics via Gemini (kept for backwards compatibility)."""

from __future__ import annotations

from datetime import datetime, timedelta

from school_bell import LyricsGenerator, load_settings


def main() -> None:
    settings = load_settings()
    generator = LyricsGenerator(settings.gemini)
    target_date = datetime.now() + timedelta(days=1)
    result = generator.generate(target_date.date())

    print("=== Generated Lyrics ===")
    print(result.lyrics)
    if result.events:
        print("\n=== Events Considered ===")
        for event in result.events:
            print(f"- {event.title}: {event.description} ({event.relevance})")


if __name__ == "__main__":
    main()
