"""Command-line entry point for generating the AI school bell."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Optional

from school_bell import WorkflowResult, load_settings, run_workflow


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate the daily AI school bell.")
    parser.add_argument(
        "--date",
        help="Target date (YYYY-MM-DD). Defaults to tomorrow if omitted.",
    )
    parser.add_argument(
        "--lyrics-input",
        type=Path,
        help="Use existing lyrics from a file instead of generating new ones.",
    )
    parser.add_argument(
        "--skip-lyrics",
        action="store_true",
        help="Skip lyric generation (requires --lyrics-input).",
    )
    parser.add_argument(
        "--skip-music",
        action="store_true",
        help="Skip music generation and only produce lyrics.",
    )
    parser.add_argument(
        "--version-count",
        type=int,
        help="Override the number of song variations to request.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print a JSON summary of the workflow result.",
    )
    return parser


def serialize_result(result: WorkflowResult) -> dict:
    return {
        "target_date": result.target_date.isoformat(),
        "lyrics_path": str(result.lyrics_path) if result.lyrics_path else None,
        "songs": [song.to_dict() for song in result.songs],
        "events": [event.__dict__ for event in result.lyrics.events] if result.lyrics else [],
        "lyrics": result.lyrics.lyrics if result.lyrics else None,
    }


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.skip_lyrics and not args.lyrics_input:
        parser.error("--skip-lyrics requires --lyrics-input to supply the lyrics.")

    settings = load_settings()
    result = run_workflow(
        settings,
        target_date=args.date,
        lyrics_path=args.lyrics_input,
        skip_lyrics=args.skip_lyrics,
        skip_music=args.skip_music,
        version_count=args.version_count,
    )

    if args.json:
        print(json.dumps(serialize_result(result), ensure_ascii=False, indent=2))
    else:
        _pretty_print(result)
    return 0


def _pretty_print(result: WorkflowResult) -> None:
    print(f"Target date: {result.target_date:%d-%m-%Y}")
    if result.lyrics_path:
        print(f"Lyrics saved to: {result.lyrics_path}")
    if result.lyrics:
        print("\nLyrics:\n" + result.lyrics.lyrics)
        if result.lyrics.events:
            print("\nEvents considered:")
            for event in result.lyrics.events:
                print(f"- {event.title}: {event.description} ({event.relevance})")
    if result.songs:
        print("\nGenerated songs:")
        for song in result.songs:
            print(f"  Version {song.version} -> {song.folder}")
            if song.audio_path:
                print(f"    Audio: {song.audio_path}")
            if song.cover_path:
                print(f"    Cover: {song.cover_path}")


if __name__ == "__main__":
    raise SystemExit(main())
