"""Smoke test stage example columns stay side-by-side and scroll into view."""
from __future__ import annotations

import http.server
import os
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

CATALOG = Path(__file__).resolve().parents[2] / "catalog"


def main() -> None:
    os.chdir(CATALOG)
    server = http.server.ThreadingHTTPServer(
        ("127.0.0.1", 0), http.server.SimpleHTTPRequestHandler
    )
    port = server.server_address[1]
    threading.Thread(target=server.serve_forever, daemon=True).start()

    with sync_playwright() as playwright:
        page = playwright.chromium.launch().new_page(viewport={"width": 1400, "height": 900})
        page.goto(f"http://127.0.0.1:{port}/cdd-approach.html", wait_until="networkidle")
        page.locator('[data-principle="iterate-and-learn"] .approach-principle__toggle').click()
        page.wait_for_timeout(400)
        for stage_id in ("discovery", "specification", "implementation"):
            page.locator(f'[data-stage-id="{stage_id}"].approach-window__stage').click()
            page.wait_for_timeout(1800 if stage_id == "implementation" else 900)

        result = page.evaluate(
            """() => {
              const host = document.getElementById('approach-stage-examples');
              const open = host?.querySelectorAll('.approach-stage-column.is-open') || [];
              const impl = host?.querySelector(
                '.approach-stage-column[data-stage-id="implementation"].is-open'
              );
              const preview = host?.querySelector(
                '.approach-stage-column[data-stage-id="specification"].is-open .skill-md-preview h1'
              );
              const editor = document.getElementById('catalog-monaco');
              const discoveryCol = host?.querySelector(
                '.approach-stage-column[data-stage-id="discovery"]'
              );
              const specCol = host?.querySelector(
                '.approach-stage-column[data-stage-id="specification"]'
              );
              const discoveryBox = discoveryCol?.getBoundingClientRect();
              const specBox = specCol?.getBoundingClientRect();
              return {
                openCount: open.length,
                openIds: Array.from(open).map((col) => col.getAttribute('data-stage-id')),
                specHeading: preview?.textContent?.trim() || '',
                implVisible: !!(impl && impl.offsetParent),
                editorWidth: editor?.offsetWidth || 0,
                editorHeight: editor?.offsetHeight || 0,
                hasEditor: !!(editor && editor._editor),
                columnsAligned:
                  discoveryBox &&
                  specBox &&
                  Math.abs(discoveryBox.left - specBox.left) > 40,
                examplesTopAligned:
                  discoveryBox &&
                  specBox &&
                  Math.abs(discoveryBox.top - specBox.top) < 2,
              };
            }"""
        )
        print(result)
    server.shutdown()

    if result["openCount"] != 3:
        raise SystemExit(f"FAIL: expected three open columns, got {result}")
    if result["specHeading"] != "Story: Create Unconfirmed User":
        raise SystemExit(f"FAIL: specification heading clipped: {result['specHeading']}")
    if not result["implVisible"]:
        raise SystemExit(f"FAIL: implementation column not visible in clip: {result}")
    if not result["hasEditor"] or result["editorWidth"] < 200 or result["editorHeight"] < 200:
        raise SystemExit(f"FAIL: implementation monaco not laid out: {result}")
    if not result.get("columnsAligned"):
        raise SystemExit(f"FAIL: refine stage columns not laid out side by side: {result}")
    if not result.get("examplesTopAligned"):
        raise SystemExit(f"FAIL: example tops are not aligned: {result}")
    print("OK: stacked refine columns render and implementation monaco loads")


if __name__ == "__main__":
    main()
