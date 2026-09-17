from __future__ import annotations

import re


def _split_long_sentence(sentence: str, max_chars: int) -> list[str]:
    words = sentence.split()
    parts: list[str] = []
    current = ""
    for word in words:
        if len(word) > max_chars:
            if current:
                parts.append(current)
                current = ""
            parts.extend(word[i : i + max_chars] for i in range(0, len(word), max_chars))
            continue
        candidate = word if not current else f"{current} {word}"
        if len(candidate) <= max_chars:
            current = candidate
        else:
            parts.append(current)
            current = word
    if current:
        parts.append(current)
    return parts


def _split_paragraph(paragraph: str, max_chars: int) -> list[str]:
    if len(paragraph) <= max_chars:
        return [paragraph]
    sentences = [part.strip() for part in re.split(r"(?<=[.!?])\s+", paragraph) if part.strip()]
    parts: list[str] = []
    current = ""
    for sentence in sentences:
        if len(sentence) > max_chars:
            if current:
                parts.append(current)
                current = ""
            parts.extend(_split_long_sentence(sentence, max_chars))
            continue
        candidate = sentence if not current else f"{current} {sentence}"
        if len(candidate) <= max_chars:
            current = candidate
        else:
            parts.append(current)
            current = sentence
    if current:
        parts.append(current)
    return parts


def segment_script(script: str, max_chars: int = 900) -> tuple[str, ...]:
    if max_chars < 20:
        raise ValueError("max_chars must be at least 20")
    paragraphs = [re.sub(r"\s+", " ", part).strip() for part in re.split(r"\n\s*\n", script)]
    parts: list[str] = []
    for paragraph in paragraphs:
        if paragraph:
            parts.extend(_split_paragraph(paragraph, max_chars))
    return tuple(part for part in parts if part)
