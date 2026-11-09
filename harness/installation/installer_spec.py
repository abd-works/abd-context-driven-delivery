"""The installer's diagnose-install instructions, as a skill or an MCP client asks for them."""

import tempfile
from pathlib import Path

from expects import contain, expect
from mamba import before, description, it

from harness.agent_tools.agent_tools import AgentInstructions
from harness.installation.installer import Installer

_REPO = Path(__file__).resolve().parents[2]


with description("the installer's diagnose-install instructions"):
    with before.each:
        installer = Installer(ide="Claude", path=tempfile.mkdtemp(prefix="installer-diagnose-"), repo=_REPO)
        self.text = AgentInstructions.for_callable(Installer.diagnose_install, installer).expand({}).instructions

    with it("should say how the install compares with the last one, asked with no arguments"):
        expect(self.text).to(contain("installed"))
