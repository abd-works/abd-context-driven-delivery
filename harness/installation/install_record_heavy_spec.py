"""What an install remembers of the files it wrote, run with the real installer on real folders: each IDE folder keeps
its own record, a stopped install's files stay known, and two installs at once into one folder both finish."""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from harness.agent_tools.agent_tools import ToolsetReference
from harness.installation.installer import Installer, ToolsetInstallFailed
from harness.installation.repository_toolsets import RepositoryToolsets

RepositoryToolsets(_REPO_ROOT).ensure_import_path()

from expects import be_above, equal, expect
from mamba import after, before, context, description, it

import harness.hooks  # noqa: F401 - registers the hook installation with the Installer, as the cdd server does
import harness.mcp.mcp_server  # noqa: F401 - registers the MCP server's installation with the Installer
from harness.guidance.fixtures.agentic_ops.agentic_ops import SampleAgenticOps
from harness.installation.install_record import InstallRecord
from harness.mcp.spec_support import ThrowawayMachine

# One whole install in a process of its own, as scripts/install.py runs it: the server channels registered, then every
# toolset of the checkout installed into the folder named.
_INSTALL_IN_ITS_OWN_PROCESS = (
    "import sys; sys.path.insert(0, sys.argv[1]); "
    "import harness.hooks.hook_installation, harness.mcp.mcp_server; "
    "from harness.installation.installer import Installer; "
    "Installer.create(ide='Cursor', path=sys.argv[2], repo=sys.argv[1]).install()"
)
_INSTALL_SECONDS = 180


def _skills(folder: Path) -> list[str]:
    return sorted(path.parent.name for path in (folder / "skills").rglob("SKILL.md")) if (folder / "skills").is_dir() else []


def _generate_skills(names: list[str]) -> list[str]:
    """The names among names that are SampleAgenticOps' generate skill, which each IDE's layout nests its own way."""
    return [name for name in names if name.endswith("generate") or name.endswith("generate/SKILL.md")]


def _recorded(folder: Path) -> list[str]:
    return json.loads((folder / InstallRecord.NAME).read_text(encoding="utf-8"))["installed_files"]


def _start_install(folder: Path) -> subprocess.Popen:
    command = [sys.executable, "-c", _INSTALL_IN_ITS_OWN_PROCESS, str(_REPO_ROOT), str(folder)]
    return subprocess.Popen(command, cwd=_REPO_ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")


with description("an install into an IDE folder") as self:
    with before.all:
        self.machine = ThrowawayMachine()
        self.machine.enter()

    with after.all:
        self.machine.leave()

    with before.each:
        self.project = Path(tempfile.mkdtemp(prefix="install-record-"))
        self.claude = Installer.create(ide="Claude", path=self.project / ".claude", repo=_REPO_ROOT)
        self.cursor = Installer.create(ide="Cursor", path=self.project / ".cursor", repo=_REPO_ROOT)

    with after.each:
        shutil.rmtree(self.project, ignore_errors=True)

    with context("with another IDE's folder installed into after it, in the same project"):
        with before.each:
            self.cursor.install([SampleAgenticOps()])
            self.claude.install([SampleAgenticOps()])
            self.removed = Installer.create(ide="Cursor", path=self.project / ".cursor", repo=_REPO_ROOT).clean()

        with it("should still remove its own files on clean"):
            expect(_skills(self.project / ".cursor")).to(equal([]))

        with it("should answer the files it removed"):
            expect(len(self.removed)).to(be_above(0))

        with it("should leave the other folder's install as it is"):
            expect(len(_generate_skills(_skills(self.project / ".claude")))).to(equal(1))

    with context("that stops at a toolset it cannot publish"):
        with before.each:
            try:
                self.cursor.install([SampleAgenticOps(), ToolsetReference.parsed("no.such.module:Nope")])
            except ToolsetInstallFailed:
                pass

        with it("should have recorded the files it wrote before it stopped"):
            expect(len(_generate_skills(_recorded(self.project / ".cursor")))).to(equal(1))

        with context("and is then cleaned"):
            with it("should remove the files it wrote before it stopped"):
                Installer.create(ide="Cursor", path=self.project / ".cursor", repo=_REPO_ROOT).clean()
                expect(_skills(self.project / ".cursor")).to(equal([]))

    with context("that is finished, then refreshed with the Installer's own commands alone"):
        with before.each:
            self.cursor.install([SampleAgenticOps()])
            Installer.create(ide="Cursor", path=self.project / ".cursor", repo=_REPO_ROOT).install_self()

        with it("should keep the skills the install wrote"):
            expect(len(_generate_skills(_skills(self.project / ".cursor")))).to(equal(1))

        with it("should keep them in its record, so a clean still removes them"):
            expect(len(_generate_skills(_recorded(self.project / ".cursor")))).to(equal(1))

    with context("that is finished, with two more started at the same moment into the same folder"):
        with before.each:
            folder = self.project / ".cursor"
            first = _start_install(folder)
            first.communicate(timeout=_INSTALL_SECONDS)
            together = [_start_install(folder), _start_install(folder)]
            self.outcomes = [(install.communicate(timeout=_INSTALL_SECONDS)[1], install.returncode) for install in together]

        with it("should finish both"):
            expect([(code, errors[-600:] if code else "") for errors, code in self.outcomes]).to(equal([(0, ""), (0, "")]))

        with it("should have the one that waited say what it waited for and for how long"):
            expect(len([errors for errors, _code in self.outcomes if "waiting up to 180 seconds for the install process" in errors])).to(equal(1))

        with it("should leave every file the record lists in the folder"):
            folder = self.project / ".cursor"
            expect([name for name in _recorded(folder) if not (folder / name).is_file()]).to(equal([]))
