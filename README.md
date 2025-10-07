# ORT Henry Ronson - AI School Bell Generator

An end-to-end automation pipeline that researches tomorrow's key events in Israel, crafts a short Hebrew bell jingle, and then produces fully-arranged audio with cover art. The system is built around two AI services – Google Gemini for lyric intelligence and a Suno-compatible API for music production – and now exposes a robust Python package and CLI for daily operations.

## Highlights

- 🔍 **Event-aware lyrics** – Gemini performs guided web search and returns structured events plus 4–8 line lyrics in JSON.
- 🎵 **Hands-free music generation** – Automatically submits the lyrics to the Suno wrapper, polls for completion, and downloads audio & cover art.
- 📦 **Modular architecture** – Reusable `school_bell` package with clear configuration, orchestration, and API layers.
- 📝 **Persistent artefacts** – Lyrics, events, and metadata are saved alongside generated media inside date-stamped folders.
- ⚙️ **Configurable** – Tune styles, polling cadence, and other knobs via environment variables.

## What's new compared to the legacy scripts?

- The project is now organised as an installable `school_bell` Python package with a `main.py` CLI instead of only ad-hoc scripts.
- Gemini lyric generation, Suno music requests, and run bookkeeping were rewritten into dedicated modules (`config.py`, `lyrics.py`, `music.py`, `workflow.py`).
- Each execution saves a dated folder containing the researched events, generated lyrics, metadata, audio files, and cover art for every requested variation.
- Environment variables (optionally loaded from `.env`) control the behaviour, letting you tweak styles, polling cadence, and output locations without touching the code.

## Is this already on the `master` branch?

Yes. The latest commit in this repository (`56f5f7f` – *Document project changes and validation steps*) is already merged into the default `master` branch in the history that ships with this project.

If you clone or pull the repository you will get these updates automatically, but you can also double-check locally:

```bash
git checkout master
git pull
git log --oneline | head
```

You should see the commit hash `56f5f7f` at the top of the log output.

## How can I check that everything works?

1. **Sanity-check the code compiles** (no syntax errors):

   ```bash
   python -m compileall school_bell main.py google-ai-script.py suno-script.py
   ```

2. **Run the full pipeline** (requires valid API credentials):

   ```bash
   python main.py --json
   ```

   The command prints a machine-readable summary and creates dated output folders with lyrics, events, MP3s, and cover art.

3. **Use the legacy helpers** if you prefer the original flow:

   ```bash
   python google-ai-script.py      # Only fetch events + lyrics
   python suno-script.py           # Only trigger music generation
   ```

   Both scripts are now thin wrappers that call into the shared package, so their outputs should match the new CLI.

## Project Structure

```
.
├── main.py                 # CLI entry point
├── school_bell/            # Core reusable package
│   ├── __init__.py
│   ├── config.py
│   ├── lyrics.py
│   ├── music.py
│   └── workflow.py
├── google-ai-script.py     # Backwards compatible lyric helper
├── suno-script.py          # Backwards compatible music helper
├── requirements.txt        # Python dependencies
└── ...                     # Date folders containing generated assets
```

## Setup

1. **Python environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Environment variables**

   Create a `.env` file (or export the variables manually):

   ```dotenv
   GEMINI_API_KEY="YOUR_GOOGLE_AI_API_KEY"
   SUNO_API_TOKEN="YOUR_SUNO_API_TOKEN"

   # Optional overrides
   SUNO_STYLE="Israeli Pop, High BPM, Drums, Beat, Techno"
   SUNO_TITLE="ORT ISRAEL"
   SUNO_MODEL="V4"
   SUNO_POLL_INTERVAL=30
   SUNO_MAX_POLLS=12
   SUNO_VERSION_COUNT=2
   SCHOOL_BELL_OUTPUT="./"
   ```

## Usage

### Full automated pipeline

Run the CLI to research events, craft lyrics, and generate music (defaulting to tomorrow):

```bash
python main.py
```

Key flags:

- `--date YYYY-MM-DD` – target a specific day.
- `--skip-music` – research events & lyrics only.
- `--skip-lyrics --lyrics-input path/to/lyrics.txt` – reuse existing lyrics.
- `--version-count 1` – request a specific number of song variations.
- `--json` – emit a machine-readable summary of the run.

### Legacy helpers

The original scripts remain, now powered by the shared package:

- `python google-ai-script.py` prints tomorrow's lyrics & the detected events.
- `python suno-script.py` submits a default jingle to the music API.

### Outputs

For a target date (e.g., 05-03-25) the workflow creates folders such as:

```
05-03-25/
├── events.json
└── lyrics.txt

05-03-25-1/
├── cover.jpeg
├── metadata.json
└── song.mp3

05-03-25-2/
├── cover.jpeg
├── metadata.json
└── song.mp3
```

`events.json` captures the researched context, while each variation folder stores the final media and metadata about the API call that produced it.

## Development Notes

- The Gemini prompt enforces a strict JSON schema, simplifying downstream parsing.
- The Suno layer exposes explicit task creation, polling, and download steps to ease debugging and future integrations (e.g., web UI, schedulers).
- Extend `main.py` or import from `school_bell.workflow` to embed the system in other automation stacks.

## Roadmap Ideas

- Automated scheduling (e.g., GitHub Actions, cron).
- Multi-lingual lyric options with dynamic translation.
- Quality assessment loop to pick the best variation automatically.
- Optional SMS/Email notifications when new bells are ready.
