from __future__ import annotations

import re
from typing import Any, Dict, Optional


def _clean_section_text(text: Optional[str]) -> str:
    value = str(text or "").replace("\r", "").strip()
    value = re.sub(r"\n{3,}", "\n\n", value)
    return value


def _truncate_text(text: str, limit: int) -> str:
    value = _clean_section_text(text)
    if len(value) <= limit:
        return value
    return f"{value[:limit - 3].rstrip()}..."


def build_structured_answer(
    *,
    answer: str,
    details: Optional[str] = None,
    source: Optional[str] = None,
) -> str:
    clean_answer = _clean_section_text(answer)
    clean_details = _clean_section_text(details)
    clean_source = _clean_section_text(source)

    if clean_answer.startswith("Answer:"):
        return clean_answer

    lines = ["Answer:", clean_answer or "I will help with this question as clearly as possible."]
    if clean_details:
        lines.extend(["", "Details:", clean_details])
    if clean_source:
        lines.extend(["", "Source:", clean_source])
    return "\n".join(lines)


def parse_answer_sections(answer: Optional[str]) -> Dict[str, str]:
    body = _clean_section_text(answer)
    if body.startswith("Answer:"):
        body = body[len("Answer:"):].strip()

    details = ""
    source = ""
    details_marker = "\nDetails:\n"
    source_marker = "\nSource:\n"

    if details_marker in body:
        body, remainder = body.split(details_marker, 1)
        body = body.strip()
        if source_marker in remainder:
            details, source = remainder.split(source_marker, 1)
        else:
            details = remainder
    elif source_marker in body:
        body, source = body.split(source_marker, 1)

    return {
        "body": _clean_section_text(body),
        "details": _clean_section_text(details),
        "source": _clean_section_text(source),
    }


def build_presentation_metadata(
    *,
    answer: Optional[str],
    verification_status: Optional[str] = None,
    fallback_mode: bool = False,
) -> Dict[str, Any]:
    sections = parse_answer_sections(answer)
    paragraphs = [segment.strip() for segment in sections["body"].split("\n\n") if segment.strip()]
    summary = _truncate_text(paragraphs[0] if paragraphs else sections["body"], 240)
    disclaimer = ""
    status = str(verification_status or "").upper()
    if status == "UNVERIFIED":
        disclaimer = "Unverified response. The UI should display a disclaimer."
    elif status == "PARTIAL":
        disclaimer = "Partially verified response. Keep the verification badge visible."

    return {
        "summary": summary,
        "body": _truncate_text(sections["body"], 1200),
        "details": _truncate_text(sections["details"], 600),
        "source": sections["source"],
        "paragraphs": paragraphs[:6],
        "disclaimer": disclaimer,
        "fallback_mode": bool(fallback_mode),
    }
