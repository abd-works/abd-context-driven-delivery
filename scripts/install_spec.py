"""The install script's restart of the cdd server, as /install-latest runs it: the lane serves the checkout's own commit."""

import argparse
import importlib.util
import tempfile
from pathlib import Path

from expects import contain, equal, expect
from mamba import before, description, it

from harness.process.claude_chat_process import claude_config_folder

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


def _chat_install(from_chat: str | None, path: str | None = None, ide: str | None = "Claude") -> argparse.Namespace:
    return argparse.Namespace(from_chat=from_chat, path=path, ide=ide)


with description("the folder an install writes into"):
    with description("for a chat working in a folder that is no CDD checkout"):
        with it("should be the IDE's folder in the chat's folder, so the chat gets the skills and commands it works with"):
            expect(install._install_path(_chat_install("C:/work/shop"))).to(equal(str(Path("C:/work/shop").resolve() / ".claude")))

    with description("with a path named"):
        with it("should be the path named, whatever chat asked"):
            expect(install._install_path(_chat_install("C:/work/shop", path="C:/elsewhere/.claude"))).to(equal("C:/elsewhere/.claude"))

    with description("with no chat named"):
        with it("should be none, so the saved install's folder is used"):
            expect(install._install_path(_chat_install(None))).to(equal(None))


with description("a chat folder an install refuses"):
    with description("for the home folder"):
        with it("should refuse it, since its .claude holds Claude Code's settings for every project"):
            expect(install._chat_folder_refusal(_chat_install(str(Path.home())))).to(contain("home folder"))

    with description("for a folder in the temporary folder"):
        with it("should refuse it, since it is thrown away"):
            expect(install._chat_folder_refusal(_chat_install(str(Path(tempfile.gettempdir()) / "scratch")))).to(contain("temporary folder"))

    with description("for one of the desktop app's spare folders"):
        with it("should refuse it, since the app moves the chat to its project"):
            spare = claude_config_folder() / "spares" / "spare-Ab12"
            expect(install._chat_folder_refusal(_chat_install(str(spare)))).to(contain("spare folder"))

    with description("for a project folder"):
        with it("should refuse nothing"):
            expect(install._chat_folder_refusal(_chat_install("C:/work/shop"))).to(equal(""))

    with description("with a path named"):
        with it("should refuse nothing, since the path says where to install"):
            expect(install._chat_folder_refusal(_chat_install(str(Path.home()), path="C:/elsewhere/.claude"))).to(equal(""))
