"""The install script's restart of the cdd server, as /install-latest runs it: the lane serves the checkout's own commit."""

import importlib.util
from pathlib import Path

from expects import contain, equal, expect
from mamba import before, description, it

_SCRIPT = Path(__file__).resolve().parent / "install.py"
_spec = importlib.util.spec_from_file_location("cdd_install_script", _SCRIPT)
install = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(install)


class FakeServed:
    """The code a lane serves: update moves a pinned lane onto the checkout's current commit and restarts its server."""

    def __init__(self) -> None:
        self.updated = 0

    def update(self) -> str:
        self.updated += 1
        return "running (pid 7, pinned C:/home/dev/runtime)"


class FakeCddEntry:
    def __init__(self) -> None:
        self.pointed = 0

    def point_chats_at_served_lane(self) -> None:
        self.pointed += 1


class FakeServer:
    def __init__(self) -> None:
        self.served = FakeServed()
        self.cdd_entry = FakeCddEntry()


class FakeLayout:
    def __init__(self, is_claude_code: bool) -> None:
        self.is_claude_code = is_claude_code


class FakeInstaller:
    def __init__(self, is_claude_code: bool = True) -> None:
        self.layout = FakeLayout(is_claude_code)


with description("the cdd server's restart in an install from the latest release"):
    with before.each:
        self.server = FakeServer()
        self.result = install._serve_this_checkout(FakeInstaller(), self.server)

    with it("should serve the checkout's current commit on its lane, so the chat bar shows the release just merged"):
        expect(self.server.served.updated).to(equal(1))

    with it("should point the chats at the lane it serves"):
        expect(self.server.cdd_entry.pointed).to(equal(1))

    with it("should answer what the lane now serves"):
        expect(self.result).to(contain("pinned C:/home/dev/runtime"))

    with description("for an IDE other than Claude Code"):
        with it("should leave the chats' entry alone, since only Claude Code chats read it"):
            server = FakeServer()
            install._serve_this_checkout(FakeInstaller(is_claude_code=False), server)
            expect(server.cdd_entry.pointed).to(equal(0))
