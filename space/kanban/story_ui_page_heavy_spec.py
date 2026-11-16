"""Deploy Story UI App With Board State: the board's server serves the Story UI editor's built page at /story-map, on its
own port, beside the board's page. The page is the one ``npm run build`` writes in the Stories practice's app folder,
which App.install of the Story UI app runs, so this spec builds it with real npm and starts a real board server on a
free port. No request here reaches cdd, so the server's cdd connection never starts."""

import os
import re
import subprocess
import time
from urllib.error import URLError
from urllib.request import urlopen

from expects import contain, equal, expect
from mamba import after, before, description, it

from harness.diagnostics.app import Npm
from space.kanban.board_app import APP_FOLDER, BOARD_SERVER, STORY_UI_FOLDER
from space.kanban.editor_apps_examples import free_port

STORY_MAP_PAGE = "/story-map"
FILE_LINK = "?file=.context/story-map.md"
STARTED_WITHIN_SECONDS = 30
STOPPED_WITHIN_SECONDS = 5


class StoryUiNotBuilt(Exception):
    """npm run build left the Story UI editor without its built page."""

    def __init__(self, stderr: str) -> None:
        super().__init__(f"npm run build in {STORY_UI_FOLDER} failed: {stderr}")


def built_index() -> str:
    return (STORY_UI_FOLDER / "dist" / "index.html").read_bytes().decode("utf-8")


def answered(url: str):
    return urlopen(url, timeout=5)


def page_at(url: str) -> str:
    with answered(url) as answer:
        return answer.read().decode("utf-8")


def listening(origin: str, server: subprocess.Popen) -> None:
    """Wait until the board's server answers, failing with what it printed when it exits or never answers."""
    deadline = time.monotonic() + STARTED_WITHIN_SECONDS
    while time.monotonic() < deadline and server.poll() is None:
        try:
            answered(f"{origin}{STORY_MAP_PAGE}/").close()
            return
        except URLError:
            time.sleep(0.2)
    server.kill()
    raise RuntimeError(f"The board's server did not answer at {origin}: {server.communicate()[0]}")


with description("Deploy Story UI App With Board State") as self:
    with before.all:
        # A fresh checkout has not installed the Story UI's packages, and its build needs them.
        if not (STORY_UI_FOLDER / "node_modules").is_dir():
            installed = Npm().run(STORY_UI_FOLDER, "install")
            if installed.code != 0:
                raise StoryUiNotBuilt(installed.stderr)
        built = Npm().run(STORY_UI_FOLDER, "run", "build")
        if built.code != 0:
            raise StoryUiNotBuilt(built.stderr)
        port = free_port()
        self.origin = f"http://127.0.0.1:{port}"
        self.server = subprocess.Popen(
            BOARD_SERVER.command,
            cwd=APP_FOLDER,
            env={**os.environ, "BOARD_PORT": str(port)},
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        listening(self.origin, self.server)

    with after.all:
        self.server.terminate()
        self.server.communicate(timeout=STOPPED_WITHIN_SECONDS)

    with it("should answer the Story UI editor's page at /story-map on the board's own port"):
        expect(page_at(f"{self.origin}{STORY_MAP_PAGE}/")).to(equal(built_index()))

    with it("should answer the Story UI editor's page for a file link under /story-map"):
        expect(page_at(f"{self.origin}{STORY_MAP_PAGE}/{FILE_LINK}")).to(equal(built_index()))

    with it("should serve the Story UI editor's built script under /story-map"):
        script = re.search(r'src="(/story-map/assets/[^"]+\.js)"', built_index()).group(1)
        with answered(f"{self.origin}{script}") as answer:
            expect(answer.headers.get("Content-Type")).to(contain("javascript"))
