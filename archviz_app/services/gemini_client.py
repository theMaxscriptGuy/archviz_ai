from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Optional

import requests


@dataclass
class GeminiResponse:
    images_b64: list[str]
    raw: dict[str, Any]


class GeminiClient:
    """Small client wrapper.

    We keep this minimal because Gemini model names/endpoints evolve.

    Supports:
    - REST call using `requests`
    - Optional SDK usage if `google-genai` is installed (future extension)

    IMPORTANT:
    You may need to adjust the endpoint and payload format to match your Gemini API.
    This file is the single place to do it.
    """

    def __init__(self, *, api_key: str, endpoint: str | None = None, timeout_s: int = 120):
        self.api_key = api_key
        self.endpoint = endpoint or "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        self.timeout_s = timeout_s

    def list_models_rest(self) -> dict[str, Any]:
        """List models available for the current API key."""
        url = "https://generativelanguage.googleapis.com/v1beta/models"
        r = requests.get(url, params={"key": self.api_key}, timeout=self.timeout_s)
        r.raise_for_status()
        return r.json()

    def generate_image_rest(
        self,
        *,
        model: str,
        prompt: str,
        inline_files: list[dict[str, str]] | None = None,
    ) -> GeminiResponse:
        """Attempts a REST call.

        `inline_files` items are expected like:
        {"mime_type": "application/pdf", "data_b64": "..."}

        NOTE: The exact schema for multimodal inputs and image generation output can differ.
        We return both parsed images (if found) and the raw response for debugging.
        """

        url = self.endpoint.format(model=model)
        headers = {"Content-Type": "application/json"}
        params = {"key": self.api_key}

        parts: list[dict[str, Any]] = [{"text": prompt}]
        for f in inline_files or []:
            parts.append(
                {
                    "inline_data": {
                        "mime_type": f["mime_type"],
                        "data": f["data_b64"],
                    }
                }
            )

        payload = {
            "contents": [{"parts": parts}],
        }

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

        images: list[str] = []

        def walk(node: Any) -> None:
            if isinstance(node, dict):
                # Gemini variants
                inline = node.get("inline_data") or node.get("inlineData")
                if isinstance(inline, dict):
                    mime = inline.get("mime_type") or inline.get("mimeType") or ""
                    b64 = inline.get("data")
                    if isinstance(mime, str) and mime.startswith("image/") and isinstance(b64, str) and b64:
                        images.append(b64)

                # Recurse
                for v in node.values():
                    walk(v)
            elif isinstance(node, list):
                for it in node:
                    walk(it)

        walk(data)
        return GeminiResponse(images_b64=images, raw=data)
