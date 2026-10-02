"""Smoke test story map visibility on cdd-approach.html."""
from __future__ import annotations

import http.server
import socket
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
CATALOG = ROOT / "catalog"


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _serve(port: int) -> http.server.ThreadingHTTPServer:
    handler = http.server.SimpleHTTPRequestHandler
    server = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def main() -> None:
    port = _free_port()
    import os

    os.chdir(CATALOG)
    server = _serve(port)
    url = f"http://127.0.0.1:{port}/cdd-approach.html"

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1400, "height": 900})
        page.goto(url, wait_until="networkidle")

        page.locator('[data-principle="iterate-and-learn"] .approach-principle__toggle').click()
        page.wait_for_timeout(500)
        scroll_before = page.evaluate("window.pageYOffset")
        page.locator('[data-stage-id="discovery"].approach-window__stage').click()
        page.wait_for_timeout(1200)
        scroll_after = page.evaluate("window.pageYOffset")
        page.wait_for_function(
            """() => {
              const frame = document.querySelector(
                '#approach-stage-examples .approach-stage-column[data-stage-id="discovery"] iframe.catalog-drawio-frame'
              );
              return frame && frame.getAttribute('src');
            }""",
            timeout=10000,
        )
        page.wait_for_timeout(4000)

        in_view = page.evaluate(
            """() => {
              const col = document.querySelector(
                '#approach-stage-examples .approach-stage-column[data-stage-id="discovery"].is-open'
              );
              if (!col) return { ok: false, reason: 'column not open' };
              const nav = document.querySelector('.site-nav');
              const pad = nav ? nav.getBoundingClientRect().height + 16 : 16;
              const margin = 16;
              const rect = col.getBoundingClientRect();
              const room = window.innerHeight - pad - margin;
              const fits = rect.height <= room;
              return {
                ok: true,
                fits,
                top: rect.top,
                bottom: rect.bottom,
                height: rect.height,
                pad,
                innerHeight: window.innerHeight,
                topVisible: rect.top >= pad - 4,
                bottomVisible: rect.bottom <= window.innerHeight - margin + 4,
              };
            }"""
        )

        wrap = page.locator(
            '#approach-stage-examples .approach-stage-column[data-stage-id="discovery"] '
            ".approach-stage-drawio--story-map"
        )
        frame = wrap.locator("iframe.catalog-drawio-frame")
        src = frame.get_attribute("src")
        box = wrap.bounding_box()
        iframe_box = frame.bounding_box()
        layout = wrap.evaluate(
            """(el) => {
              const spacer = el.querySelector('.approach-stage-drawio__spacer');
              const scale = parseFloat(el.dataset.storyMapScale || '1');
              const pageH = parseFloat(el.dataset.pageH || '0');
              const scaledH = pageH ? Math.ceil(pageH * scale) : 0;
              return {
                clientHeight: el.clientHeight,
                scrollHeight: el.scrollHeight,
                overflowY: getComputedStyle(el).overflowY,
                scale,
                scaledH,
                spacerHeight: spacer ? spacer.offsetHeight : 0,
                clipHeight: el.closest('.approach-stage-examples__clip')?.clientHeight || 0,
              };
            }"""
        )

        browser.close()
    server.shutdown()

    print("scroll before:", scroll_before, "after:", scroll_after)
    print("in view:", in_view)
    print("iframe src set:", bool(src))
    print("wrap box:", box)
    print("iframe box:", iframe_box)
    print("layout:", layout)
    if scroll_after <= scroll_before:
        raise SystemExit("FAIL: page did not scroll down to the example panel")
    if not in_view.get("ok"):
        raise SystemExit(f"FAIL: discovery column not open: {in_view}")
    if in_view["fits"] and (not in_view["topVisible"] or not in_view["bottomVisible"]):
        raise SystemExit(f"FAIL: expanded example should fit in viewport: {in_view}")
    if not in_view["bottomVisible"]:
        raise SystemExit(f"FAIL: bottom of expanded example is clipped: {in_view}")
    if not src:
        raise SystemExit("FAIL: story map iframe never loaded (no src)")
    if not box or box["height"] < 100:
        raise SystemExit(f"FAIL: story map container too small: {box}")
    if not iframe_box or iframe_box["width"] > 6000:
        raise SystemExit(f"FAIL: iframe layout too wide (double-scale bug): {iframe_box}")
    if layout["spacerHeight"] > layout["clientHeight"] + 8:
        raise SystemExit(f"FAIL: story map content taller than viewport: {layout}")
    if layout["scaledH"] and layout["spacerHeight"] < layout["scaledH"] - 4:
        raise SystemExit(f"FAIL: story map spacer does not match scaled height: {layout}")
    print("OK: story map container rendered")


if __name__ == "__main__":
    main()
