from __future__ import annotations

from pathlib import Path

from archviz_app.models.render_job import (
    CameraAngle,
    ExteriorInputs,
    FileInput,
    FinishNotes,
    InteriorInputs,
    RenderJob,
    RoomInputs,
)
from archviz_app.utils.file_utils import kind_from_path


def build_render_job(
    *,
    project_name: str,
    style_notes: str,
    model_name: str,
    exterior_plan_files: list[str],
    exterior_finishes: str,
    exterior_angles: list[tuple[str, str]],
    rooms: list[dict],
) -> RenderJob:
    exterior = ExteriorInputs(
        plan_files=[
            FileInput(path=Path(p), kind=kind_from_path(Path(p))) for p in exterior_plan_files
        ],
        finishes=FinishNotes(notes=exterior_finishes),
        camera_angles=[CameraAngle(name=n, description=d) for (n, d) in exterior_angles],
    )

    interior_rooms: list[RoomInputs] = []
    for r in rooms:
        files = [FileInput(path=Path(p), kind=kind_from_path(Path(p))) for p in r.get("files", [])]
        angles = [CameraAngle(name=n, description=d) for (n, d) in r.get("angles", [])]
        interior_rooms.append(
            RoomInputs(
                room_name=r.get("name", "Room"),
                plan_or_reference_files=files,
                finishes=FinishNotes(notes=r.get("finishes", "")),
                camera_angles=angles,
            )
        )

    return RenderJob(
        project_name=project_name or "Untitled Project",
        style_consistency_notes=style_notes or "",
        exterior=exterior,
        interior=InteriorInputs(rooms=interior_rooms),
        model_name=model_name or "gemini-2.5-flash-image-preview",
    )
