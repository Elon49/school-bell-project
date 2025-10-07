"""Legacy helper to trigger music generation via the Suno-compatible API."""

from __future__ import annotations

from datetime import datetime, timedelta

from school_bell import LyricsResult, SunoMusicGenerator, load_settings


def main() -> None:
    settings = load_settings()
    music_generator = SunoMusicGenerator(settings)

    # Fallback lyrics if no external text is provided.
    default_lyrics = """
    צלצול בית ספר חדש מתגלגל,
    היום נפתח עם חיוך ומתגבר.
    ביחד נעלה את הקצב כאן,
    אורט הנרי רונסון, אנחנו מוכן!
    """.strip()

    lyrics = LyricsResult(lyrics=default_lyrics, events=[], raw_response=default_lyrics)
    target_date = (datetime.now() + timedelta(days=1)).date()
    songs = music_generator.generate(lyrics, target_date)

    print("Generated the following versions:")
    for song in songs:
        print(f"- Version {song.version}: {song.folder}")
        if song.audio_path:
            print(f"  Audio: {song.audio_path}")
        if song.cover_path:
            print(f"  Cover: {song.cover_path}")


if __name__ == "__main__":
    main()
