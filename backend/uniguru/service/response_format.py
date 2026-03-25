from __future__ import annotations

import re
from typing import Optional


def _clean_section_text(text: Optional[str]) -> str:
    value = str(text or "").replace("\r", "").strip()
    value = re.sub(r"\n{3,}", "\n\n", value)
    return value


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
