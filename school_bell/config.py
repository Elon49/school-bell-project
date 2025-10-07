"""Configuration helpers for the school bell project."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
import os

load_dotenv()


@dataclass
class GeminiConfig:
    """Settings related to the Google Gemini model."""

    api_key: str
    model: str = "gemini-2.0-flash"
    enable_search: bool = True


@dataclass
class SunoConfig:
    """Settings for interacting with the Suno-compatible API."""

    api_token: str
    create_task_url: str = "https://apibox.erweima.ai/api/v1/generate"
    status_url_template: str = (
        "https://apibox.erweima.ai/api/v1/generate/record-info?taskId={task_id}"
    )
    style: str = "Israeli Pop, High BPM, Drums, Beat, Techno"
    title: str = "ORT ISRAEL"
    custom_mode: bool = True
    instrumental: bool = False
    model: str = "V4"
    callback_url: Optional[str] = None
    poll_interval: int = 30
    max_polls: int = 12
    request_timeout: int = 60


@dataclass
class Settings:
    """Aggregated configuration for the full workflow."""

    gemini: GeminiConfig
    suno: SunoConfig
    output_root: Path = Path(".")
    version_count: int = 2

    @property
    def headers(self) -> dict[str, str]:
        """Return default headers for Suno API requests."""
        return {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.suno.api_token}",
        }


def _get_env_int(var_name: str, default: int) -> int:
    """Read an integer environment variable, falling back to a default."""
    raw_value = os.getenv(var_name)
    if raw_value is None:
        return default
    try:
        return int(raw_value)
    except ValueError as exc:
        raise ValueError(f"Environment variable {var_name} must be an integer.") from exc


def load_settings() -> Settings:
    """Load settings from environment variables."""
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        raise EnvironmentError(
            "GEMINI_API_KEY is missing. Add it to your environment or .env file."
        )

    suno_api_token = os.getenv("SUNO_API_TOKEN")
    if not suno_api_token:
        raise EnvironmentError(
            "SUNO_API_TOKEN is missing. Add it to your environment or .env file."
        )

    gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    enable_search = os.getenv("GEMINI_ENABLE_SEARCH", "true").lower() != "false"

    suno_style = os.getenv("SUNO_STYLE", "Israeli Pop, High BPM, Drums, Beat, Techno")
    suno_title = os.getenv("SUNO_TITLE", "ORT ISRAEL")
    suno_model = os.getenv("SUNO_MODEL", "V4")
    suno_instrumental = os.getenv("SUNO_INSTRUMENTAL", "false").lower() == "true"
    suno_custom_mode = os.getenv("SUNO_CUSTOM_MODE", "true").lower() != "false"
    suno_callback = os.getenv("SUNO_CALLBACK_URL")
    poll_interval = _get_env_int("SUNO_POLL_INTERVAL", 30)
    max_polls = _get_env_int("SUNO_MAX_POLLS", 12)
    request_timeout = _get_env_int("SUNO_REQUEST_TIMEOUT", 60)
    version_count = _get_env_int("SUNO_VERSION_COUNT", 2)

    output_root_env = os.getenv("SCHOOL_BELL_OUTPUT", ".")
    output_root = Path(output_root_env).expanduser().resolve()

    gemini_config = GeminiConfig(
        api_key=gemini_api_key,
        model=gemini_model,
        enable_search=enable_search,
    )

    suno_config = SunoConfig(
        api_token=suno_api_token,
        style=suno_style,
        title=suno_title,
        model=suno_model,
        instrumental=suno_instrumental,
        custom_mode=suno_custom_mode,
        callback_url=suno_callback,
        poll_interval=poll_interval,
        max_polls=max_polls,
        request_timeout=request_timeout,
    )

    return Settings(
        gemini=gemini_config,
        suno=suno_config,
        output_root=output_root,
        version_count=version_count,
    )
