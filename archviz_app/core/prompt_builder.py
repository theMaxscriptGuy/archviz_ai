from __future__ import annotations

from archviz_app.models.render_job import RenderJob


def build_prompt_for_angle(job: RenderJob, *, scope: str, scope_name: str, angle_name: str, angle_desc: str) -> str:
    """Build a single prompt for a given camera angle.

    scope: 'exterior' or 'room'
    scope_name: room name when scope == 'room'

    The prompt is intentionally plain text. You can evolve it as you refine consistency requirements.
    """

    base = f"""
You are an architectural visualization rendering assistant.

Goal: Generate a photorealistic render that is CONSISTENT across views.

PROJECT: {job.project_name}
STYLE / CONSISTENCY NOTES:
{job.style_consistency_notes}

SCOPE: {scope}
SCOPE_NAME: {scope_name}
CAMERA ANGLE NAME: {angle_name}
CAMERA ANGLE DETAILS: {angle_desc}

Instructions:
- Maintain consistent materials, colors, and style across all generated images.
- Use the provided plan and material notes as ground truth.
- Do not hallucinate additional rooms/materials not described.
- Produce a high quality, realistic render.

Return only the final image.
""".strip()

    return base
