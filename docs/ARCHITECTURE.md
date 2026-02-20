# Architecture notes

This app is built around a simple flow:

1. **UI** collects user inputs (files, notes, camera angles)
2. `core/job_builder.py` converts UI state into a typed `RenderJob`
3. `core/prompt_builder.py` creates per-angle prompts
4. `services/render_service.py` orchestrates rendering (exterior + rooms)
5. `services/gemini_client.py` is the only integration point for Gemini payload/response details

## Why this design

- Gemini APIs and model payloads change. Keeping them contained in one module makes maintenance easy.
- UI can evolve (e.g., better room detection) without impacting service logic.

## Consistency

True cross-view consistency typically needs:
- a shared style bible (global notes)
- a shared material/palette library
- explicit instructions to reuse those materials
- potentially multi-step generation (e.g., generate keyframe, then derive variations)

This MVP provides the hooks to iterate.
