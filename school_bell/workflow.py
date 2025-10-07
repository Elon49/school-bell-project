"""High-level orchestration for generating the daily school bell."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional

from .config import Settings
from .lyrics import LyricsGenerator, LyricsResult
from .music import SongResult, SunoMusicGenerator


@dataclass
class WorkflowResult:
    """Outcome of running the full pipeline."""

    target_date: date
    lyrics: LyricsResult | None
    songs: list[SongResult]
    lyrics_path: Path | None


def resolve_target_date(date_override: Optional[str]) -> date:
    if date_override:
        return datetime.strptime(date_override, "%Y-%m-%d").date()
    return (datetime.now() + timedelta(days=1)).date()


def run_workflow(
    settings: Settings,
    *,
    target_date: Optional[str] = None,
    lyrics_path: Optional[Path] = None,
    skip_lyrics: bool = False,
    skip_music: bool = False,
    version_count: Optional[int] = None,
) -> WorkflowResult:
    """Run the full generation workflow."""

    actual_date = resolve_target_date(target_date)
    lyrics_result: LyricsResult | None = None
    lyrics_file: Path | None = None

    if not skip_lyrics:
        generator = LyricsGenerator(settings.gemini)
        lyrics_result = generator.generate(actual_date)
        lyrics_file = _persist_lyrics(settings.output_root, actual_date, lyrics_result)
    elif lyrics_path:
        lyrics_file = lyrics_path
        lyrics_text = lyrics_path.read_text(encoding="utf-8")
        lyrics_result = LyricsResult(lyrics=lyrics_text, events=[], raw_response=lyrics_text)

    songs: list[SongResult] = []
    if not skip_music and lyrics_result:
        music_generator = SunoMusicGenerator(settings)
        songs = music_generator.generate(
            lyrics_result,
            actual_date,
            version_count or settings.version_count,
        )

    return WorkflowResult(
        target_date=actual_date,
        lyrics=lyrics_result,
        songs=songs,
        lyrics_path=lyrics_file,
    )


def _persist_lyrics(root: Path, target_date: date, result: LyricsResult) -> Path:
    folder = root / target_date.strftime("%d-%m-%y")
    folder.mkdir(parents=True, exist_ok=True)
    lyrics_path = folder / "lyrics.txt"
    lyrics_path.write_text(result.lyrics, encoding="utf-8")

    events_path = folder / "events.json"
    events_path.write_text(
        _serialize_events(result),
        encoding="utf-8",
    )
    return lyrics_path


def _serialize_events(result: LyricsResult) -> str:
    import json

    return json.dumps(
        {
            "events": [event.__dict__ for event in result.events],
            "raw_response": result.raw_response,
        },
        ensure_ascii=False,
        indent=2,
    )
