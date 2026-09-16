from datetime import UTC

from app.collectors.base import parse_dt, parse_rss


def test_parse_dt_normalizes_naive_iso_timestamp_to_utc():
    parsed = parse_dt("2026-09-16T12:30:00")
    assert parsed.tzinfo is UTC
    assert parsed.isoformat() == "2026-09-16T12:30:00+00:00"


def test_parse_dt_normalizes_offset_timestamp_to_utc():
    parsed = parse_dt("2026-09-16T18:00:00+05:30")
    assert parsed.tzinfo is UTC
    assert parsed.isoformat() == "2026-09-16T12:30:00+00:00"


def test_parse_dt_accepts_rfc2822_timestamp():
    parsed = parse_dt("Wed, 16 Sep 2026 12:30:00 GMT")
    assert parsed.tzinfo is UTC
    assert parsed.isoformat() == "2026-09-16T12:30:00+00:00"


def test_parse_dt_invalid_value_returns_aware_utc_fallback():
    parsed = parse_dt("not-a-date")
    assert parsed.tzinfo is UTC


def test_parse_rss_reads_multiple_items_without_cross_item_state():
    xml = """
    <rss><channel>
      <item><title>First</title><link>https://example.com/1</link><pubDate>Wed, 16 Sep 2026 12:00:00 GMT</pubDate><description>A</description></item>
      <item><title>Second</title><link>https://example.com/2</link><pubDate>Wed, 16 Sep 2026 13:00:00 GMT</pubDate><description>B</description></item>
    </channel></rss>
    """
    assert parse_rss(xml) == [
        {"title": "First", "url": "https://example.com/1", "published": "Wed, 16 Sep 2026 12:00:00 GMT", "summary": "A"},
        {"title": "Second", "url": "https://example.com/2", "published": "Wed, 16 Sep 2026 13:00:00 GMT", "summary": "B"},
    ]
