"""LiveAppCapture — one capture of a running application: its smoke test, its page scout, and its re-capture of pages."""
from __future__ import annotations

import dataclasses
import ipaddress
import logging
import re
import socket
import subprocess
from pathlib import Path
from typing import Optional
from urllib.parse import urlsplit

from harness.process.process import LOOPBACK_CONNECT_SECONDS

_log = logging.getLogger(__name__)

_STUBS_DIR = ("tests", "stubs")
_SCOUT_DIR = ("sandbox", "extracted-context", "app-extraction")
_COMMON_PORTS = [3000, 8000, 8080, 5000, 4000, 5173, 4173]
_FALLBACK_BASE_URL = "http://localhost:3000"
_SMOKE_REQUEST_SECONDS = 5
_PAGE_LOAD_MILLISECONDS = 30_000
_ROOT_RENDER_MILLISECONDS = 10_000
# A page with no `#root` element (not a single-page app) gets this long to settle before it is captured.
_SETTLE_MILLISECONDS = 1500
_ROOT_RENDERED = "() => { const r = document.querySelector('#root'); return !!(r && r.childElementCount > 0); }"


class CaptureFailed(Exception):
    """The capture could not look at the application at all, such as when the process list cannot be read."""


@dataclasses.dataclass
class ScreenResult:
    """Reachability verdict for one screen during a smoke test."""

    slug: str
    url: str
    reachable: bool
    status_code: int


@dataclasses.dataclass
class SmokeTestResult:
    """Results of a smoke test run against the stubbed application."""

    passed: bool
    screen_results: list[ScreenResult]
    inventory_path: str


@dataclasses.dataclass
class PageCapture:
    """One captured page from a scout or complete-capture run."""

    slug: str
    url: str
    screenshot_path: str
    aria_path: str


@dataclasses.dataclass
class FailedPage:
    """A page the browser could not load or snapshot, with the browser's reason, so it can be captured again."""

    url: str
    reason: str


@dataclasses.dataclass
class ScoutResult:
    """Results of the Phase 0 app scout."""

    overview_path: str
    pages_dir: str
    page_captures: list[PageCapture]
    failed_pages: list[FailedPage] = dataclasses.field(default_factory=list)

    @property
    def page_count(self) -> int:
        return len(self.page_captures)

    @property
    def page_slugs(self) -> list[str]:
        return [p.slug for p in self.page_captures]


@dataclasses.dataclass
class CaptureResult:
    """Results of a Phase N complete-capture run."""

    overview_path: str
    added_captures: list[PageCapture]
    total_page_count: int
    failed_pages: list[FailedPage] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class LiveAppCapture:
    """The application one tool call captures: the repository it runs from, where the capture is written (the
    capture repository, or the app's own repository when none is named), its surface, its base URL (found on a common
    local port when blank), and the paths it visits (the root when none are named)."""

    repo_path: str
    capture_repo: str = ""
    surface: str = "web"
    base_url: str = ""
    entry_paths: Optional[list[str]] = None

    def stubs_root(self) -> Path:
        return self._write_root().joinpath(*_STUBS_DIR)

    def scout_root(self) -> Path:
        return self._write_root().joinpath(*_SCOUT_DIR)

    def smoke_test(self) -> SmokeTestResult:
        inventory = self.stubs_root() / "stub-inventory.md"
        inventory.parent.mkdir(parents=True, exist_ok=True)
        screen_results = self._probe_screens()
        self._append_smoke_results(inventory, screen_results)
        return SmokeTestResult(
            passed=bool(screen_results) and all(r.reachable for r in screen_results),
            screen_results=screen_results,
            inventory_path=str(inventory),
        )

    def scout(self) -> ScoutResult:
        pages_root = self._pages_root()
        overview = self.scout_root() / "extraction-overview.md"
        captures, failed = self._capture_for_surface(pages_root)
        overview.write_text(self._overview_header() + "".join(self._overview_section(c) for c in captures), encoding="utf-8")
        return ScoutResult(
            overview_path=str(overview),
            pages_dir=str(pages_root),
            page_captures=captures,
            failed_pages=failed,
        )

    def complete(self) -> CaptureResult:
        pages_root = self._pages_root()
        overview = self.scout_root() / "extraction-overview.md"
        existing_slugs = self._existing_slugs(overview)
        added, failed = self._capture_for_surface(pages_root)
        with overview.open("a", encoding="utf-8") as written:
            written.writelines("\n" + self._overview_section(c).rstrip("\n") + "\n" for c in added)
        return CaptureResult(
            overview_path=str(overview),
            added_captures=added,
            total_page_count=len(existing_slugs) + len(added),
            failed_pages=failed,
        )

    def _write_root(self) -> Path:
        return Path((self.capture_repo or "").strip() or self.repo_path)

    def _pages_root(self) -> Path:
        pages_root = self.scout_root() / "pages"
        pages_root.mkdir(parents=True, exist_ok=True)
        return pages_root

    def _paths(self) -> list[str]:
        return self.entry_paths or ["/"]

    def _is_browsable(self) -> bool:
        return self.surface in ("web", "api")

    def _app_url(self) -> str:
        if not self.base_url:
            self.base_url = self._detect_base_url()
        return self.base_url.rstrip("/")

    def _detect_base_url(self) -> str:
        for port in _COMMON_PORTS:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(LOOPBACK_CONNECT_SECONDS)
                if s.connect_ex(("localhost", port)) == 0:
                    return f"http://localhost:{port}"
        return _FALLBACK_BASE_URL

    # ── smoke test ───────────────────────────────────────────────────────────

    def _probe_screens(self) -> list[ScreenResult]:
        if not self._is_browsable():
            return [self._desktop_smoke()]
        import requests

        return [self._http_smoke_path(requests, path) for path in self._paths()]

    def _http_smoke_path(self, requests, path: str) -> ScreenResult:
        url = self._app_url() + path
        slug = path.strip("/").replace("/", "-") or "root"
        try:
            status = requests.get(url, timeout=(self._connect_seconds(), _SMOKE_REQUEST_SECONDS), allow_redirects=True).status_code
        except requests.RequestException as refused:
            _log.info("Smoke request to %s got no answer: %s", url, refused)
            return ScreenResult(slug=slug, url=url, reachable=False, status_code=0)
        return ScreenResult(slug=slug, url=url, reachable=status < 400, status_code=status)

    def _connect_seconds(self) -> float:
        """How long a smoke request waits to connect: an app on this computer accepts at once or not at all, so it gets
        the short loopback wait; an app elsewhere gets the whole request time."""
        host = urlsplit(self._app_url()).hostname or ""
        try:
            loopback = host == "localhost" or ipaddress.ip_address(host).is_loopback
        except ValueError:
            loopback = False
        return LOOPBACK_CONNECT_SECONDS if loopback else _SMOKE_REQUEST_SECONDS

    def _desktop_smoke(self) -> ScreenResult:
        lister = "tasklist" if re.search(r"[A-Za-z]:\\", self.repo_path) else "ps"
        try:
            listing = subprocess.check_output([lister, "-e"], stderr=subprocess.DEVNULL).decode(errors="replace")
        except (OSError, subprocess.CalledProcessError) as failed:
            raise CaptureFailed(f"Could not list running processes with {lister}: {failed}") from failed
        running = Path(self.repo_path).name.lower() in listing.lower()
        return ScreenResult(slug="desktop-root", url=self.repo_path, reachable=running, status_code=200 if running else 0)

    def _append_smoke_results(self, inventory: Path, results: list[ScreenResult]) -> None:
        lines = [
            "\n\n## Smoke Test Results\n",
            "| Slug | URL | Reachable | Status |\n",
            "|------|-----|-----------|--------|\n",
        ]
        for r in results:
            lines.append(f"| {r.slug} | {r.url} | {'yes' if r.reachable else 'no'} | {r.status_code} |\n")
        with inventory.open("a", encoding="utf-8") as written:
            written.writelines(lines)

    # ── page capture ─────────────────────────────────────────────────────────

    def _capture_for_surface(self, pages_root: Path) -> tuple[list[PageCapture], list[FailedPage]]:
        if not self._is_browsable():
            return [], []
        from playwright.sync_api import sync_playwright

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page()
            captured = self._capture_pages(page, pages_root)
            browser.close()
        return captured

    def _capture_pages(self, page, pages_root: Path) -> tuple[list[PageCapture], list[FailedPage]]:
        from playwright.sync_api import Error as BrowserError

        captures: list[PageCapture] = []
        failed: list[FailedPage] = []
        for index, path in enumerate(self._paths()):
            url = self._app_url() + path
            try:
                captures.append(self._snapshot_page(page, url, path, pages_root / self._slug(index, path)))
            except BrowserError as error:
                _log.warning("Could not capture %s: %s", url, error)
                failed.append(FailedPage(url=url, reason=str(error)))
        return captures, failed

    def _slug(self, index: int, path: str) -> str:
        label = path.strip("/").replace("/", "-") or "home"
        return f"{index + 1:02d}-{label}"

    def _snapshot_page(self, page, url: str, path: str, page_dir: Path) -> PageCapture:
        page_dir.mkdir(parents=True, exist_ok=True)
        screenshot, aria = page_dir / "screenshot.png", page_dir / "aria.yaml"
        page.goto(url, timeout=_PAGE_LOAD_MILLISECONDS, wait_until="networkidle")
        self._wait_for_root(page)
        page.screenshot(path=str(screenshot), full_page=True)
        aria.write_text(
            f"user_intent: visit {path}\naria_snapshot: |\n"
            + "\n".join(f"  {line}" for line in page.aria_snapshot().splitlines()),
            encoding="utf-8",
        )
        return PageCapture(slug=page_dir.name, url=url, screenshot_path=str(screenshot), aria_path=str(aria))

    def _wait_for_root(self, page) -> None:
        from playwright.sync_api import TimeoutError as RootNeverRendered

        try:
            page.wait_for_function(_ROOT_RENDERED, timeout=_ROOT_RENDER_MILLISECONDS)
        except RootNeverRendered:
            page.wait_for_timeout(_SETTLE_MILLISECONDS)

    # ── extraction overview ──────────────────────────────────────────────────

    def _overview_header(self) -> str:
        app_name = Path(self.repo_path).name
        return (
            f"---\napp: {app_name}\nsurface: {self.surface}\ntool: playwright\n---\n\n"
            f"# Extraction Overview — {app_name}\n\n"
        )

    def _overview_section(self, cap: PageCapture) -> str:
        return (
            f"## {cap.slug}\n\n"
            f"- **url:** {cap.url}\n"
            f"- **screenshot:** {cap.screenshot_path}\n"
            f"- **aria:** {cap.aria_path}\n\n"
        )

    def _existing_slugs(self, overview: Path) -> list[str]:
        if not overview.exists():
            return []
        return re.findall(r"^## (\S+)", overview.read_text(encoding="utf-8"), re.MULTILINE)
