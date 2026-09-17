from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from app.assets.manifest import sha256_file
from app.assets.models import AssetRecord
from app.assets.resolver import AssetRequest


@contextmanager
def _playwright_page(*, viewport: dict[str, int]):
    from playwright.sync_api import sync_playwright

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport=viewport)
        try:
            yield page
        finally:
            browser.close()


class ScreenshotCapture:
    def __init__(self, page_factory=None, timeout_ms: int = 15_000):
        self.page_factory = page_factory or _playwright_page
        self.timeout_ms = timeout_ms

    def capture(self, request: AssetRequest, out_dir: Path) -> AssetRecord:
        target_dir = Path(out_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / f"{request.id}.png"
        viewport = {"width": 1440, "height": 900}

        with self.page_factory(viewport=viewport) as page:
            page.goto(
                request.source_url,
                wait_until="domcontentloaded",
                timeout=self.timeout_ms,
            )
            page.screenshot(path=str(target), full_page=False)

        return AssetRecord(
            id=request.id,
            kind=request.kind,
            local_path=str(target),
            source_url=request.source_url,
            source_name=request.source_name,
            usage=request.purpose,
            license_note="source-page screenshot",
            sha256=sha256_file(target),
            captured_at=datetime.now(timezone.utc),
            scene_id=request.scene_id,
        )
