from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


class FileInput(BaseModel):
    """Represents a user-provided PDF/image reference."""

    path: Path
    kind: Literal["pdf", "image", "other"] = "other"


class CameraAngle(BaseModel):
    """A camera angle description. Keep as free-form text for now."""

    name: str = Field(..., description="Short label like 'Front 45°' or 'North-East'.")
    description: str = Field("", description="Any extra notes (lens, height, FOV, etc.)")


class FinishNotes(BaseModel):
    """Free-form notes for materials/colors."""

    notes: str = ""


class ExteriorInputs(BaseModel):
    plan_files: list[FileInput] = Field(default_factory=list)
    finishes: FinishNotes = Field(default_factory=FinishNotes)
    camera_angles: list[CameraAngle] = Field(default_factory=list)


class RoomInputs(BaseModel):
    room_name: str
    plan_or_reference_files: list[FileInput] = Field(default_factory=list)
    finishes: FinishNotes = Field(default_factory=FinishNotes)
    camera_angles: list[CameraAngle] = Field(default_factory=list)


class InteriorInputs(BaseModel):
    rooms: list[RoomInputs] = Field(default_factory=list)


class RenderJob(BaseModel):
    project_name: str = "Untitled Project"
    style_consistency_notes: str = ""
    exterior: ExteriorInputs = Field(default_factory=ExteriorInputs)
    interior: InteriorInputs = Field(default_factory=InteriorInputs)

    model_name: str = "gemini-2.5-flash-image-preview"
