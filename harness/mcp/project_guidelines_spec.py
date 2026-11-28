"""The guidelines the cdd server serves each project it answers: the patterns CDD ships, less each the project's
.context/config.json disables, and the patterns the project keeps in its own guidelines folder, which no other project
the same server answers is served."""

import shutil
import tempfile
from pathlib import Path

from expects import contain, equal, expect
from mamba import after, before, context, description, it

import harness.hooks  # noqa: F401 - registers the hook channel with the installer, as the server does
from harness.mcp.mcp_server import McpHost, ProjectToolsets

# A project that keeps acme_domain_driven in its guidelines folder and disables lern_domain_driven.
_ACME = Path(__file__).resolve().parents[1] / "graph" / "_examples" / "project_guidelines"
_LERN = "cdd_guidance.patterns.lern_domain_driven.lern_domain_driven:LernDomainDriven"
_LERN_INSTRUCTIONS = "lern-domain-driven.instructions"
_ACME_INSTRUCTIONS = "acme-domain-driven.instructions"


with description("the guidelines the cdd server serves a project"):
    with before.all:
        self.folder = Path(tempfile.mkdtemp(prefix="cdd-served-guidelines-"))
        self.acme = self.folder / "acme"
        shutil.copytree(_ACME, self.acme)
        self.other = self.folder / "other"
        self.other.mkdir()
        self.host = McpHost(ProjectToolsets.of_refs((_LERN,)))

    with after.all:
        shutil.rmtree(self.folder, ignore_errors=True)

    with context("with a project that keeps its own pattern and disables the LERN pattern"):
        with it("should list its own pattern's instructions"):
            expect([tool["name"] for tool in self.host.tools_listed_for(self.acme)]).to(contain(_ACME_INSTRUCTIONS))

        with it("should not list the LERN pattern's instructions"):
            expect(_LERN_INSTRUCTIONS in [tool["name"] for tool in self.host.tools_listed_for(self.acme)]).to(equal(False))

        with it("should answer with its own pattern's guidance"):
            expect(str(self.host.dispatch(_ACME_INSTRUCTIONS, {}, self.acme))).to(contain("root-saves-itself"))

    with context("with another project the same server answers"):
        with it("should list the LERN pattern's instructions"):
            expect([tool["name"] for tool in self.host.tools_listed_for(self.other)]).to(contain(_LERN_INSTRUCTIONS))

        with it("should not list the first project's pattern"):
            expect(_ACME_INSTRUCTIONS in [tool["name"] for tool in self.host.tools_listed_for(self.other)]).to(equal(False))
