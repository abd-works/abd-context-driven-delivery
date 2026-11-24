"""The installer's diagnose-install instructions, as a skill or an MCP client asks for them."""

import tempfile
from pathlib import Path

from expects import contain, equal, expect
from mamba import before, description, it

from harness.agent_tools.agent_tools import AgentInstructions
from harness.installation.install_record import InstallRecord
from harness.installation.installer import Installer
import harness.hooks  # noqa: F401 - registers the hook installation with the Installer, as the cdd server does
import harness.mcp.mcp_server  # noqa: F401 - registers the MCP server's installation with the Installer

_REPO = Path(__file__).resolve().parents[2]


with description("the installer's diagnose-install instructions"):
    with before.each:
        installer = Installer.create(ide="Claude", path=tempfile.mkdtemp(prefix="installer-diagnose-"), repo=_REPO)
        self.text = AgentInstructions.for_callable(Installer.diagnose_install, installer).expand({}).instructions

    with it("should say how the install compares with the last one, asked with no arguments"):
        expect(self.text).to(contain("installed"))


with description("the installer of a checkout into a project's own IDE folder"):
    with before.each:
        # A folder outside the temporary folder, in one that exists, as a project's IDE folder is; making its installer
        # writes nothing into it.
        self.folder = Path.home() / ".claude-of-no-such-project"
        self.installer = Installer.create(ide="Claude", path=self.folder, repo=_REPO)

    with it("should keep the record of what it wrote in that folder, so each folder's install is known by itself"):
        expect(self.installer.record.path).to(equal(self.folder / InstallRecord.NAME))

    with it("should hold the one lock of that folder, so a second install into it waits"):
        expect(self.installer.lock.folder).to(equal(self.folder))
