from __future__ import annotations

import json
import urllib.request
import xml.etree.ElementTree as ET
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from typing import Any


def get_json(url: str, headers: dict | None = None, timeout: int = 20) -> Any:
    request_headers = {"User-Agent": "AutoTubeLab/0.1 (+https://github.com/kanhaal/autotube-lab)"}
    request_headers.update(headers or {})
    request = urllib.request.Request(url, headers=request_headers)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def get_text(url: str, timeout: int = 20) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": "AutoTubeLab/0.1"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8", "replace")


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def parse_dt(value: object) -> datetime:
    """Parse API/RSS timestamps and always return an aware UTC datetime."""
    if value is None or value == "":
        return datetime.now(UTC)
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(value, tz=UTC)

    text = str(value).strip()
    try:
        return _as_utc(datetime.fromisoformat(text))
    except ValueError:
        pass

    try:
        return _as_utc(parsedate_to_datetime(text))
    except (TypeError, ValueError):
        return datetime.now(UTC)


def _element_text(element: ET.Element, name: str) -> str:
    node = element.find(name)
    return "" if node is None else "".join(node.itertext()).strip()


def parse_rss(xml: str) -> list[dict[str, str]]:
    root = ET.fromstring(xml)
    items = []
    for item in root.findall(".//item"):
        items.append({
            "title": _element_text(item, "title"),
            "url": _element_text(item, "link"),
            "published": _element_text(item, "pubDate"),
            "summary": _element_text(item, "description"),
        })
    if items:
        return items

    namespace = {"a": "http://www.w3.org/2005/Atom"}
    for entry in root.findall(".//a:entry", namespace):
        title = entry.find("a:title", namespace)
        link = entry.find("a:link", namespace)
        updated = entry.find("a:updated", namespace)
        summary = entry.find("a:summary", namespace)
        items.append({
            "title": "".join(title.itertext()).strip() if title is not None else "",
            "url": link.get("href", "") if link is not None else "",
            "published": updated.text if updated is not None and updated.text else "",
            "summary": "".join(summary.itertext()).strip() if summary is not None else "",
        })
    return items
