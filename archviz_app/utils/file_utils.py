from __future__ import annotations

import base64
import mimetypes
from pathlib import Path


def guess_mime(path: Path) -> str:
    mime, _ = mimetypes.guess_type(str(path))
    return mime or "application/octet-stream"


def to_b64(path: Path) -> str:
    data = path.read_bytes()
    return base64.b64encode(data).decode("utf-8")


def kind_from_path(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".pdf"}:
        return "pdf"
    if suffix in {".png", ".jpg", ".jpeg", ".webp"}:
        return "image"
    return "other"
