"""Smoke test Monaco scenario folding on cdd-approach.html."""
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
        page.wait_for_timeout(400)
        page.locator('[data-stage-id="implementation"].approach-window__stage').click()
        page.wait_for_timeout(2500)

        stats = page.evaluate(
            """async () => {
              const root = document.getElementById('catalog-monaco');
              const editor = root && root._editor;
              if (!editor) return { ok: false, reason: 'no editor' };
              const model = editor.getModel();
              const folding = editor.getContribution('editor.contrib.folding');
              const foldModel = folding && folding.getFoldingModel
                ? await folding.getFoldingModel()
                : null;
              const regionList = [];
              const collapsed = [];
              if (foldModel && foldModel.regions) {
                const regions = foldModel.regions;
                for (let i = 0; i < regions.length; i++) {
                  regionList.push({
                    start: regions.getStartLineNumber(i),
                    end: regions.getEndLineNumber(i),
                    collapsed: regions.isCollapsed(i),
                  });
                  if (regions.isCollapsed(i)) {
                    collapsed.push({
                      start: regions.getStartLineNumber(i),
                      end: regions.getEndLineNumber(i),
                    });
                  }
                }
              }
              const hidden = new Set();
              collapsed.forEach((range) => {
                for (let line = range.start + 1; line <= range.end; line++) {
                  hidden.add(line);
                }
              });
              const lines = [];
              for (let line = 1; line <= model.getLineCount(); line++) {
                if (!hidden.has(line)) {
                  lines.push(model.getLineContent(line).trim());
                }
              }
              return {
                ok: true,
                collapsedCount: collapsed.length,
                regionList: regionList,
                folds: JSON.parse(root.getAttribute('data-folds') || '[]'),
                visible: lines,
                hasExpect: lines.some((line) => line.includes('expect(')),
                hasGiven: lines.some((line) => line.includes('given(')),
                hasStory: lines.some((line) => line.includes("story('")),
                hasScenario: lines.some((line) => line.includes("scenario('")),
                hasClosing: lines.some((line) => line === '});'),
              };
            }"""
        )
        browser.close()
    server.shutdown()

    print("monaco:", stats)
    if not stats.get("ok"):
        raise SystemExit(f"FAIL: {stats}")
    if stats["collapsedCount"] < 4:
        raise SystemExit(f"FAIL: expected collapsed fold regions, got {stats['collapsedCount']}")
    if stats["hasExpect"]:
        raise SystemExit("FAIL: expect() body lines are still visible")
    if not stats["hasGiven"] or not stats["hasStory"] or not stats["hasScenario"]:
        raise SystemExit("FAIL: story/scenario/step signatures should stay visible")
    print("OK: monaco scenario folds applied")


if __name__ == "__main__":
    main()
