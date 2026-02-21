# ArchViz Desktop Tool (PyQt)

A desktop application to **collect exterior + interior arch-viz inputs** (plans, materials, room-by-room notes, and camera angles) and generate **consistent renders** using **Gemini Flash 2.5 (or latest)**.

This repo is intentionally organized for clean GitHub use: modular code, clear models, and a simple run path.

## What it does (MVP)

- Accepts **PDFs and images** as inputs.
- Splits inputs into:
  - **Exterior**: plan/top view + wall paint/finishes + camera angles.
  - **Interior**: dynamically created **rooms**, each with files/notes, finishes, and camera angles.
- Collates everything into a structured **Render Job**.
- Calls a **Gemini image generation client** to generate renders for each camera angle.
- Saves outputs under `output/`.

> Note: The first version focuses on *input collation + a clean API integration point*.
> Interpreting architectural drawings and enforcing advanced cross-view consistency is model/prompt dependent and will be iterated.

---

## Tech stack

- **Python 3.10+**
- **PyQt6** UI
- **Pydantic** for typed data models
- **requests** for HTTP
- Optional: **google-genai** SDK (`pip install -e .[gemini]`)

---

## Project structure

```
archviz_desktop_tool/
  archviz_app/
    main.py                # app entrypoint
    core/
      job_builder.py       # collate UI state -> RenderJob
      prompt_builder.py    # RenderJob -> Gemini prompt payload
    models/
      render_job.py        # Pydantic models
    services/
      gemini_client.py     # Gemini REST/SDK client + interface
      render_service.py    # orchestrates generation per camera angle
    ui/
      main_window.py       # tabs + layout
      exterior_tab.py
      interior_tab.py
      widgets.py           # reusable widgets (file pickers, angle editor)
    utils/
      file_utils.py        # base64, mime detection
      qt_async.py          # QThread worker helpers
  output/                  # generated renders (gitignored)
  tests/
  pyproject.toml
  .gitignore
  README.md
```

---

## Setup

### 1) Create a virtualenv

```bash
cd archviz_desktop_tool
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -U pip
```

### 2) Install dependencies

```bash
pip install -e .
# (optional) Gemini SDK
pip install -e ".[gemini]"
```

### 3) Run

```bash
archviz-tool
# or
python -m archviz_app.main
```

---

## Using the app

1. Paste your **Gemini API key** (kept only in-memory for this run).
2. Add exterior files + finishes + camera angles.
3. Create interior rooms (e.g., Living, Kitchen, Bedroom 1...) and fill their files/notes/camera angles.
4. Click **Generate**.
5. Outputs are written to `output/<timestamp>/...`.

---

## Gemini integration notes

This project provides a clean integration point in:
- `archviz_app/services/gemini_client.py`

Because Gemini endpoints and model names evolve, the client is designed to be easy to update.

### Model name
Default is set to `gemini-2.5-flash-image` (update in UI or config if needed).

---

## Roadmap ideas

- Parse PDF plans (room count detection) to auto-create rooms.
- Per-room reference image boards.
- Consistency prompts: shared palette + material library + style bible.
- Job templates and presets.
- Render queue + retry + caching.

---

## License

MIT
