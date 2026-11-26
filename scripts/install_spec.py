"""The install script's restart of the cdd server, as /install-latest runs it: the lane serves the checkout's own commit."""

import argparse
import importlib.util
import tempfile
from pathlib import Path

from expects import contain, equal, expect
from mamba import before, description, it

import harness.hooks  # noqa: F401 - registers the hook installation with the Installer, as the script does
import harness.mcp.mcp_server  # noqa: F401 - registers the MCP server's installation with the Installer
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
    return argparse.Namespace(from_chat=from_chat, path=path, ide=ide, dev_lane=False)


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

    with description("for a chat whose folder is not known, named with nothing"):
        with it("should refuse it, since an empty name would install into whatever directory the script runs in"):
            expect(install._chat_folder_refusal(_chat_install(""))).to(contain("not known"))


with description("an install told where to go by something that is no IDE or no folder"):
    with description("with an IDE name CDD does not install into"):
        with it("should refuse with the refused exit, before anything is written"):
            expect(install._install(_chat_install(None, path="C:/work/shop/.emacs", ide="Emacs"))).to(equal(install.REFUSED_EXIT))

    with description("with a file as the path"):
        with it("should refuse with the refused exit, before anything is written"):
            expect(install._install(_chat_install(None, path=str(_SCRIPT)))).to(equal(install.REFUSED_EXIT))

    with description("with a path whose parent folder does not exist"):
        with it("should refuse with the refused exit, before anything is written"):
            missing = _SCRIPT.parent / "does" / "not" / "exist" / ".github"
            expect(install._install(_chat_install(None, path=str(missing), ide="VS Code"))).to(equal(install.REFUSED_EXIT))


with description("the install command"):
    with description("asked for the dev lane"):
        with it("should point the project's chats at the dev lane"):
            expect(install._parser().parse_args(["--dev-lane"]).dev_lane).to(equal(True))

    with description("asked for no lane"):
        with it("should leave the project's chats on the stable lane unless it is the checkout's own"):
            expect(install._parser().parse_args([]).dev_lane).to(equal(False))


class FakeFullInstaller:
    """An installer that records how its Installer-only refresh was asked for, and has no whole install to run, which
    would replace the last one."""

    def __init__(self) -> None:
        self.self_installs = 0

    def install_self(self) -> None:
        self.self_installs += 1


def _self_install() -> argparse.Namespace:
    """The script's arguments for its self option, whose name a Namespace cannot take as a keyword."""
    args = argparse.Namespace(no_replace=False)
    setattr(args, "self", True)
    return args


with description("an Installer-only refresh asked of the install script"):
    with before.each:
        self.installer = FakeFullInstaller()
        install._install_toolsets(_self_install(), self.installer, FakeServer())

    with it("should refresh the Installer's own commands, leaving the rest of the last install in place"):
        expect(self.installer.self_installs).to(equal(1))
