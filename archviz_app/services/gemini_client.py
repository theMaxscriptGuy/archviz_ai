from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import requests


@dataclass
class GeminiResponse:
    images_b64: list[str]
    raw: dict[str, Any]


class GeminiClient:
    """Gemini wrapper.

    Supports two backends:
    1) **google-genai SDK** (recommended for image preview models)
    2) **REST** fallback (best-effort)

    Many Gemini models (e.g., flash text models) will not return image bytes from
    `:generateContent`. Image-capable preview models are best used through the SDK.
    """

    def __init__(self, *, api_key: str, endpoint: str | None = None, timeout_s: int = 120):
        self.api_key = api_key
        self.endpoint = endpoint or "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        self.timeout_s = timeout_s

    # -----------------------------
    # Model listing
    # -----------------------------
    def list_models_rest(self) -> dict[str, Any]:
        url = "https://generativelanguage.googleapis.com/v1beta/models"
        r = requests.get(url, params={"key": self.api_key}, timeout=self.timeout_s)
        r.raise_for_status()
        return r.json()

    # -----------------------------
    # Image generation
    # -----------------------------
    def generate_image(
        self,
        *,
        model: str,
        prompt: str,
        inline_files: list[dict[str, str]] | None = None,
    ) -> GeminiResponse:
        """Generate image(s) using SDK if available, else REST."""

        try:
            return self._generate_image_sdk(model=model, prompt=prompt, inline_files=inline_files)
        except ModuleNotFoundError:
            # SDK not installed
            return self._generate_image_rest(model=model, prompt=prompt, inline_files=inline_files)

    def _generate_image_sdk(
        self,
        *,
        model: str,
        prompt: str,
        inline_files: list[dict[str, str]] | None = None,
    ) -> GeminiResponse:
        """SDK path using `google-genai`.

        This is the most reliable way to use Gemini image preview models.
        """

        from google import genai  # type: ignore

        client = genai.Client(api_key=self.api_key)

        # Build contents: prompt + inline parts
        contents: list[Any] = [prompt]

        # Best-effort: attach as bytes. SDK types have changed across versions,
        # so we keep it permissive.
        for f in inline_files or []:
            try:
                from google.genai import types  # type: ignore

                b = _b64decode(f["data_b64"])
                contents.append(types.Part.from_bytes(data=b, mime_type=f["mime_type"]))
            except Exception:
                # If types API isn't available, fall back to REST.
                return self._generate_image_rest(model=model, prompt=prompt, inline_files=inline_files)

        # Ask for image modality.
        try:
            from google.genai import types  # type: ignore

            cfg = types.GenerateContentConfig(response_modalities=["IMAGE", "TEXT"])
            resp = client.models.generate_content(model=model, contents=contents, config=cfg)
        except Exception:
            resp = client.models.generate_content(model=model, contents=contents)

        raw = _to_raw_dict(resp)
        images = _extract_images_b64(raw)
        return GeminiResponse(images_b64=images, raw=raw)

    def _generate_image_rest(
        self,
        *,
        model: str,
        prompt: str,
        inline_files: list[dict[str, str]] | None = None,
    ) -> GeminiResponse:
        url = self.endpoint.format(model=model)
        headers = {"Content-Type": "application/json"}
        params = {"key": self.api_key}

        parts: list[dict[str, Any]] = [{"text": prompt}]
        for f in inline_files or []:
            parts.append({"inline_data": {"mime_type": f["mime_type"], "data": f["data_b64"]}})

        payload = {"contents": [{"parts": parts}]}

        r = requests.post(url, headers=headers, params=params, data=json.dumps(payload), timeout=self.timeout_s)
        if r.status_code == 404:
            raise RuntimeError(
                "Gemini returned 404 (model not found or endpoint not supported). "
                "Fix by choosing a model name that exists for your API key. "
                "Try the app button 'List available models' or call: "
                "https://generativelanguage.googleapis.com/v1beta/models?key=YOUR_KEY"
            )
        r.raise_for_status()
        data = r.json()

        images = _extract_images_b64(data)
        return GeminiResponse(images_b64=images, raw=data)


# -----------------------------
# Helpers
# -----------------------------

def _extract_images_b64(data: Any) -> list[str]:
    images: list[str] = []

    def walk(node: Any) -> None:
        if isinstance(node, dict):
            inline = node.get("inline_data") or node.get("inlineData")
            if isinstance(inline, dict):
                mime = inline.get("mime_type") or inline.get("mimeType") or ""
                b64 = inline.get("data")
                if isinstance(mime, str) and mime.startswith("image/") and isinstance(b64, str) and b64:
                    images.append(b64)

            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for it in node:
                walk(it)

    walk(data)
    return images


def _to_raw_dict(resp: Any) -> dict[str, Any]:
    # google-genai responses typically have .model_dump() (pydantic-like)
    if hasattr(resp, "model_dump"):
        return resp.model_dump()
    # Or .to_dict()
    if hasattr(resp, "to_dict"):
        return resp.to_dict()
    # Last resort
    try:
        return json.loads(json.dumps(resp, default=str))
    except Exception:
        return {"repr": repr(resp)}


def _b64decode(s: str) -> bytes:
    import base64

    return base64.b64decode(s)
