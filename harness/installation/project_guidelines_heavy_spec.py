"""An install into a project publishes the guidelines that project works with: each pattern CDD ships that the
project's .context/config.json does not disable, and each pattern the project keeps in its own guidelines folder,
published as a shipped one is. An install into another project from the same checkout publishes none of the first
project's patterns."""

import shutil
import tempfile
from pathlib import Path

from expects import contain, equal, expect
from mamba import after, before, context, description, it

_REPO_ROOT = Path(__file__).resolve().parents[2]

import harness.hooks  # noqa: F401,E402 - registers the hook channel with the installer
import harness.mcp.mcp_server  # noqa: F401,E402 - registers the MCP channel with the installer
from harness.installation.installer import Installer  # noqa: E402
from harness.installation.project_guidelines import guideline_name  # noqa: E402

# A project that keeps acme_domain_driven in its guidelines folder and disables lern_domain_driven.
_ACME = _REPO_ROOT / "harness" / "graph" / "_examples" / "project_guidelines"


def _installed_files(folder: Path) -> str:
    """Every file an install wrote into folder, by its path from folder, one a line."""
    return "\n".join(sorted(path.relative_to(folder).as_posix() for path in folder.rglob("*") if path.is_file()))


def _pattern_install(project: Path) -> tuple[list[str], str]:
    """The guidelines an install of the repository into project's .claude publishes, by name, and the files the install
    of those guidelines writes there."""
    installer = Installer.create(ide="Claude", path=project / ".claude", repo=_REPO_ROOT)
    guidelines = [reference for reference in installer.repository_toolsets() if guideline_name(reference.toolset_class)]
    installer.install(guidelines)
    return [guideline_name(reference.toolset_class) for reference in guidelines], _installed_files(project / ".claude")


with description("an install of the repository into a project"):
    with before.all:
        self.folder = Path(tempfile.mkdtemp(prefix="cdd-install-guidelines-"))
        self.acme = self.folder / "acme"
        shutil.copytree(_ACME, self.acme)
        self.other = self.folder / "other"
        self.other.mkdir()
        self.acme_guidelines, self.acme_files = _pattern_install(self.acme)
        self.other_guidelines, self.other_files = _pattern_install(self.other)

    with after.all:
        shutil.rmtree(self.folder, ignore_errors=True)

    with context("with a project that keeps its own pattern and disables the LERN pattern"):
        with it("should publish its own pattern"):
            expect(self.acme_guidelines).to(contain("acme_domain_driven"))

        with it("should leave out the LERN pattern"):
            expect("lern_domain_driven" in self.acme_guidelines).to(equal(False))

        with it("should write its own pattern's skill beside the shipped patterns'"):
            expect(self.acme_files).to(contain("skills/patterns-acme-domain-driven/SKILL.md"))

        with it("should write no file of the LERN pattern"):
            expect("lern-domain-driven" in self.acme_files).to(equal(False))

    with context("with another project installed from the same checkout"):
        with it("should publish the LERN pattern"):
            expect(self.other_guidelines).to(contain("lern_domain_driven"))

        with it("should not publish the first project's pattern"):
            expect("acme_domain_driven" in self.other_guidelines).to(equal(False))
