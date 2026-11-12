"""The answers a board read keeps in a session's folder, worked out again only when what they depend on changes."""

import shutil
import sys
import tempfile
import time
from pathlib import Path

from expects import equal, expect
from mamba import after, before, context, description, it

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from space.session.progress_cache import HAS_OUTPUT, PROGRESS_CACHE_FILE, VIOLATION_COUNT, ProgressCache


_WAIT_SECONDS = 10


def _until(condition) -> bool:
    deadline = time.monotonic() + _WAIT_SECONDS
    while time.monotonic() < deadline and not condition():
        time.sleep(0.05)
    return condition()


class _Counting:
    """An answer that counts how often it is worked out."""

    def __init__(self, value: object) -> None:
        self.value = value
        self.times = 0

    def __call__(self) -> object:
        self.times += 1
        return self.value


with description("a session's progress cache"):
    with before.each:
        self.folder = Path(tempfile.mkdtemp(prefix="cdd-progress-cache-"))
        self.cache = ProgressCache(self.folder)
        self.files_found = _Counting(True)

    with after.each:
        shutil.rmtree(self.folder, ignore_errors=True)

    with context("that has answered a fidelity's question under a key"):
        with before.each:
            self.cache.answer("stories-story-map", HAS_OUTPUT, "two lines", self.files_found)

        with it("should give the kept answer for the same key without working it out again"):
            self.cache.answer("stories-story-map", HAS_OUTPUT, "two lines", self.files_found)
            expect(self.files_found.times).to(equal(1))

        with it("should work the answer out again once the key changes"):
            self.cache.answer("stories-story-map", HAS_OUTPUT, "three lines", self.files_found)
            expect(self.files_found.times).to(equal(2))

        with it("should keep another question's answer apart"):
            expect(self.cache.answer("stories-story-map", VIOLATION_COUNT, "two lines", lambda: 4)).to(equal(4))

        with it("should give the kept answer to a cache made later for the same folder, once it has written them"):
            _until((self.folder / PROGRESS_CACHE_FILE).is_file)
            later = ProgressCache(self.folder)
            later.answer("stories-story-map", HAS_OUTPUT, "two lines", self.files_found)
            expect(self.files_found.times).to(equal(1))

    with context("that finds its file unreadable"):
        with it("should work the answer out again"):
            (self.folder / PROGRESS_CACHE_FILE).write_text("not json", encoding="utf-8")
            expect(ProgressCache(self.folder).answer("ddd-model", VIOLATION_COUNT, "one report", lambda: 3)).to(equal(3))

    with context("that belongs to a session with no folder yet"):
        with it("should keep its answers while it is held"):
            held = ProgressCache(None)
            held.answer("ddd-model", HAS_OUTPUT, "one line", self.files_found)
            held.answer("ddd-model", HAS_OUTPUT, "one line", self.files_found)
            expect(self.files_found.times).to(equal(1))
