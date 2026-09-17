from contextlib import contextmanager
from pathlib import Path

from app.assets.resolver import AssetRequest
from app.assets.screenshots import ScreenshotCapture


class FakePage:
    def __init__(self):
        self.goto_calls = []
        self.screenshot_calls = []

    def goto(self, url, *, wait_until, timeout):
        self.goto_calls.append((url, wait_until, timeout))

    def screenshot(self, *, path, full_page):
        self.screenshot_calls.append((path, full_page))
        Path(path).write_bytes(b"fake-png")


def test_capture_uses_exact_verified_url_fixed_viewport_and_single_png(tmp_path: Path):
    page = FakePage()
    seen = {}

    @contextmanager
    def fake_page_factory(*, viewport):
        seen["viewport"] = viewport
        yield page

    request = AssetRequest(
        id="source-1",
        kind="source_screenshot",
        source_url="https://example.com/alpha",
        source_name="Official Alpha",
        purpose="show official announcement",
    )
    capture = ScreenshotCapture(page_factory=fake_page_factory, timeout_ms=12_000)

    record = capture.capture(request, tmp_path)

    assert seen["viewport"] == {"width": 1440, "height": 900}
    assert page.goto_calls == [("https://example.com/alpha", "domcontentloaded", 12_000)]
    assert len(page.screenshot_calls) == 1
    assert page.screenshot_calls[0][1] is False
    assert Path(record.local_path).name == "source-1.png"
    assert Path(record.local_path).read_bytes() == b"fake-png"
    assert record.source_url == request.source_url
    assert record.source_name == request.source_name
    assert record.usage == request.purpose
    assert len(record.sha256) == 64


def test_capture_does_not_import_playwright_when_fake_factory_is_injected(tmp_path: Path):
    page = FakePage()

    @contextmanager
    def fake_page_factory(*, viewport):
        assert viewport == {"width": 1440, "height": 900}
        yield page

    request = AssetRequest(
        id="source-2",
        kind="source_screenshot",
        source_url="https://example.com/beta",
        source_name="Official Beta",
        purpose="corroboration",
    )

    record = ScreenshotCapture(page_factory=fake_page_factory).capture(request, tmp_path)
    assert Path(record.local_path).exists()
