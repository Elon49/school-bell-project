"""Interaction layer for the Suno-compatible music generation API."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Dict, List

import requests

from .config import Settings
from .lyrics import LyricsResult


@dataclass
class SongResult:
    """Metadata about a generated song and its assets."""

    version: int
    folder: Path
    audio_path: Path | None
    cover_path: Path | None
    api_payload: Dict[str, Any]
    api_response: Dict[str, Any]

    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "folder": str(self.folder),
            "audio_path": str(self.audio_path) if self.audio_path else None,
            "cover_path": str(self.cover_path) if self.cover_path else None,
            "api_payload": self.api_payload,
            "api_response": self.api_response,
        }


class SunoMusicGenerator:
    """Handles creation, polling, and downloading of Suno music generations."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def create_task(self, lyrics: str) -> Dict[str, Any]:
        payload = {
            "prompt": lyrics,
            "style": self._settings.suno.style,
            "title": self._settings.suno.title,
            "customMode": self._settings.suno.custom_mode,
            "instrumental": self._settings.suno.instrumental,
            "model": self._settings.suno.model,
        }
        if self._settings.suno.callback_url:
            payload["callBackUrl"] = self._settings.suno.callback_url

        response = requests.post(
            self._settings.suno.create_task_url,
            headers=self._settings.headers,
            json=payload,
            timeout=self._settings.suno.request_timeout,
        )
        response.raise_for_status()
        data = response.json()
        return {"payload": payload, "response": data}

    def poll_task(self, task_id: str) -> Dict[str, Any]:
        for attempt in range(self._settings.suno.max_polls):
            response = requests.get(
                self._settings.suno.status_url_template.format(task_id=task_id),
                headers=self._settings.headers,
                timeout=self._settings.suno.request_timeout,
            )
            response.raise_for_status()
            data = response.json()
            status = data.get("data", {}).get("status")
            if status == "SUCCESS":
                return data
            if status not in {"PENDING", "PROCESSING", "CREATED", "SUCCESS"}:
                raise RuntimeError(f"Task failed with status: {status}")
            time.sleep(self._settings.suno.poll_interval)

        raise TimeoutError(
            "Timed out while waiting for the Suno API to finish generating the song."
        )

    def download_assets(
        self,
        task_response: Dict[str, Any],
        payload: Dict[str, Any],
        target_date: date,
        version_count: int,
    ) -> List[SongResult]:
        tomorrow = target_date
        results: List[SongResult] = []
        response_data = task_response.get("data", {}).get("response", {}).get("sunoData", [])
        if not response_data:
            raise ValueError("Task response did not contain 'sunoData'.")

        for version in range(1, version_count + 1):
            folder_name = tomorrow.strftime("%d-%m-%y") + f"-{version}"
            folder_path = self._settings.output_root / folder_name
            folder_path.mkdir(parents=True, exist_ok=True)

            song_data = response_data[version - 1] if version - 1 < len(response_data) else {}
            audio_url = song_data.get("audioUrl")
            image_url = song_data.get("imageUrl")

            audio_path = self._download_file(audio_url, folder_path / "song.mp3")
            cover_path = self._download_file(image_url, folder_path / "cover.jpeg")

            metadata_path = folder_path / "metadata.json"
            metadata = {
                "lyrics": payload["prompt"],
                "style": payload["style"],
                "title": payload["title"],
                "suno_response": song_data,
            }
            metadata_path.write_text(
                json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
            )

            lyrics_path = folder_path / "lyrics.txt"
            if not lyrics_path.exists():
                lyrics_path.write_text(payload["prompt"], encoding="utf-8")

            results.append(
                SongResult(
                    version=version,
                    folder=folder_path,
                    audio_path=audio_path,
                    cover_path=cover_path,
                    api_payload=payload,
                    api_response=song_data,
                )
            )

        return results

    def generate(
        self, lyrics_result: LyricsResult, target_date: date, version_count: int | None = None
    ) -> List[SongResult]:
        version_count = version_count or self._settings.version_count
        task = self.create_task(lyrics_result.lyrics)
        task_id = task["response"]["data"]["taskId"]
        status_response = self.poll_task(task_id)
        return self.download_assets(status_response, task["payload"], target_date, version_count)

    @staticmethod
    def _download_file(url: str | None, destination: Path) -> Path | None:
        if not url:
            return None
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        destination.write_bytes(response.content)
        return destination
