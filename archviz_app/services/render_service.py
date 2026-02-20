from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from archviz_app.core.prompt_builder import build_prompt_for_angle
from archviz_app.models.render_job import RenderJob
from archviz_app.services.gemini_client import GeminiClient
from archviz_app.utils.file_utils import guess_mime, to_b64


@dataclass
class RenderOutput:
    output_dir: Path
    written_files: list[Path]


def _inline_files(paths: Iterable[Path]) -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    for p in paths:
        out.append({"mime_type": guess_mime(p), "data_b64": to_b64(p)})
    return out


class RenderService:
    def __init__(self, *, gemini: GeminiClient, output_dir: Path):
        self.gemini = gemini
        self.output_dir = output_dir

    def render_all(self, job: RenderJob) -> RenderOutput:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        written: list[Path] = []

        # Exterior
        ext_files = [fi.path for fi in job.exterior.plan_files]
        for angle in job.exterior.camera_angles:
            prompt = build_prompt_for_angle(
                job,
                scope="exterior",
                scope_name="exterior",
                angle_name=angle.name,
                angle_desc=angle.description,
            )
            resp = self.gemini.generate_image_rest(
                model=job.model_name,
                prompt=prompt + "\n\nEXTERIOR FINISH NOTES:\n" + job.exterior.finishes.notes,
                inline_files=_inline_files(ext_files),
            )
            written += _write_images(resp.images_b64, self.output_dir / "exterior", angle.name)

        # Interior rooms
        for room in job.interior.rooms:
            room_files = [fi.path for fi in room.plan_or_reference_files]
            for angle in room.camera_angles:
                prompt = build_prompt_for_angle(
                    job,
                    scope="room",
                    scope_name=room.room_name,
                    angle_name=angle.name,
                    angle_desc=angle.description,
                )
                resp = self.gemini.generate_image_rest(
                    model=job.model_name,
                    prompt=prompt + "\n\nROOM FINISH NOTES:\n" + room.finishes.notes,
                    inline_files=_inline_files(room_files),
                )
                written += _write_images(resp.images_b64, self.output_dir / "interior" / _safe(room.room_name), angle.name)

        return RenderOutput(output_dir=self.output_dir, written_files=written)


def _safe(s: str) -> str:
    return "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in s).strip("_") or "room"


def _write_images(images_b64: list[str], out_dir: Path, stem: str) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    if not images_b64:
        return paths

    for i, b64 in enumerate(images_b64, start=1):
        p = out_dir / f"{_safe(stem)}_{i}.png"
        import base64

        p.write_bytes(base64.b64decode(b64))
        paths.append(p)

    return paths
