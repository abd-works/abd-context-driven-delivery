"""BDD spec — guidance resource model."""
import shutil
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("context_tools", "primitives", "utilities"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import contain, equal, expect
from mamba import after, before, context, description, it

from context_tools.context_guidance.fixtures.agentic_ops.agentic_ops import (
    SampleAgenticOps,
    SampleMcpOps,
)
from context_tools.context_guidance.fixtures.other_tool.other_tool_host import OtherToolHost
from context_tools.context_guidance.fixtures.sample_tool.sample_tool_host import (
    SampleContextGuidance,
    SampleMcpContextGuidance,
    SampleToolHost,
)
from primitives.harness import Harness
from primitives.markdown import HTML, Markdown


with description("a co-located markdown file beside a host module"):
    with context("with a section heading that matches a property label"):
        with context("with a string property on the host backed by that section"):
            with it("should return the section body when the property is read"):
                host = SampleToolHost()
                text = host.guidance
                expect(text).to(contain("known prose for guidance in sample tool"))
                expect(text).not_to(contain("sample preamble"))

    with context("with known prose written in the module markdown file for that label"):
        with context("with the property read on the host in that module"):
            with it("should return that prose"):
                host = SampleToolHost()
                expect(host.guidance).to(contain("known prose for guidance in sample tool"))

        with context("with an identically named section in a different module folder"):
            with it(
                "should not return prose from the other module file when the host belongs to this module"
            ):
                host = SampleToolHost()
                other = OtherToolHost()
                expect(host.guidance).to(contain("known prose for guidance in sample tool"))
                expect(host.guidance).not_to(contain("prose from the other module only"))
                expect(other.guidance).to(contain("prose from the other module only"))
                expect(other.guidance).not_to(contain("known prose for guidance in sample tool"))

    with context("with a markdown-backed string property"):
        with context("with that property read as HTML"):
            with it("should return HTML formatted from that section body"):
                host = SampleToolHost()
                rendered = Markdown.from_label(host, "guidance").html()
                expect(type(rendered)).to(equal(HTML))
                expect(str(rendered)).to(contain("known prose for guidance in sample tool"))
                expect(str(rendered)).to(contain("<p>"))


with description("context guidance"):
    with context("with the instructions property read"):
        with it(
            "should join context, guidance, formatted rules, and the template for the active format"
        ):
            host = SampleContextGuidance(format="templates")
            text = host.instructions
            expect(text).to(contain("sample preamble"))
            expect(text).to(contain("known prose for guidance in sample tool"))
            expect(text).to(contain("sample-rule-one"))
            expect(text).to(contain("active format template body for sample tool"))

        with it(
            "should expose instructions as one compound property not as a single markdown label"
        ):
            host = SampleContextGuidance(format="templates")
            expect(host.instructions).not_to(equal(host.context))
            expect(host.instructions).not_to(equal(host.guidance))
            expect(host.instructions).to(contain(host.context.strip()))
            expect(host.instructions).to(contain(host.guidance.strip()))


with description("a toolset module with several agent-instructions operations"):
    with context("with the instructions property read on a loaded instance"):
        with it("should assemble one compound instructions string from each registered operation"):
            host = SampleAgenticOps()
            text = host.instructions
            keys = set(host.instructions_registry)
            expect(text).to(contain("compound generate instructions"))
            expect(text).to(contain("compound sketch instructions"))
            expect("generate" in keys).to(equal(True))
            expect("sketch" in keys).to(equal(True))


def _skill_names(tree: Path) -> set[str]:
    return {path.parent.name for path in tree.joinpath("skills").glob("*/SKILL.md")}


def _command_names(tree: Path) -> set[str]:
    folder = tree / "commands"
    if not folder.is_dir():
        return set()
    return {path.stem for path in folder.glob("*.md")}


with description("a bare agentic toolset registered for deploy") as self:
    with before.each:
        self._tmp = tempfile.mkdtemp()
        self.tree = Path(self._tmp)
        self.harness = Harness(ide="Cursor", path=self.tree)
        self.harness.write_deploy([SampleAgenticOps()])

    with after.each:
        shutil.rmtree(self._tmp, ignore_errors=True)

    with context("with a Cursor deploy output tree"):
        with it("should write one skill file per agent-instructions operation marked for skill"):
            expect(_skill_names(self.tree)).to(contain("generate"))

        with it("should write one command file per agent-instructions operation marked for command"):
            expect(_command_names(self.tree)).to(contain("sketch"))

        with it(
            "should write a skill or command for an agent-tool operation only when that operation is also marked skill or command"
        ):
            expect(_skill_names(self.tree)).to(contain("listed"))
            ping = list(self.tree.rglob("*ping*"))
            expect(ping).to(equal([]))

        with it("should not write a context guidance skill or fidelity commands"):
            expect(_skill_names(self.tree)).not_to(contain("sample_tool"))
            expect(_command_names(self.tree)).not_to(contain("sample-ops-behavior"))

    with context("with a deploy output tree"):
        with it(
            "should render skill and command bodies from the same instructions strings the read path assembles"
        ):
            skill_text = (self.tree / "skills" / "generate" / "SKILL.md").read_text(encoding="utf-8")
            command_text = (self.tree / "commands" / "sketch.md").read_text(encoding="utf-8")
            host = SampleAgenticOps()
            expect(skill_text).to(contain("compound generate instructions"))
            expect(command_text).to(contain("compound sketch instructions"))
            expect(host.instructions).to(contain("compound generate instructions"))


with description("a bare agentic toolset with mcp-published operations registered for deploy") as self:
    with before.each:
        self._tmp = tempfile.mkdtemp()
        self.tree = Path(self._tmp)
        self.harness = Harness(ide="Cursor", path=self.tree)
        self.harness.write_deploy([SampleMcpOps()])

    with after.each:
        shutil.rmtree(self._tmp, ignore_errors=True)

    with context("with a deployed skill file for an mcp-published agent-instructions operation"):
        with it("should still write the skill file so there is a slash command"):
            expect((self.tree / "skills" / "generate" / "SKILL.md").is_file()).to(equal(True))

        with it("should put the context section at the top of the file"):
            text = (self.tree / "skills" / "generate" / "SKILL.md").read_text(encoding="utf-8")
            expect(text.index("Use MCP tool:") >= 0).to(equal(True))

        with it("should not put the full instructions in that file"):
            text = (self.tree / "skills" / "generate" / "SKILL.md").read_text(encoding="utf-8")
            expect(text).not_to(contain("full generate instructions that must not appear"))

        with it("should place one MCP invoke tail after the context section"):
            text = (self.tree / "skills" / "generate" / "SKILL.md").read_text(encoding="utf-8")
            expect(text).to(contain("Use MCP tool:"))

        with it(
            "should name the tool as the toolset slug and operation with the method parameter signature in backticks"
        ):
            text = (self.tree / "skills" / "generate" / "SKILL.md").read_text(encoding="utf-8")
            expect(text).to(contain("`sample-mcp.generate"))

        with it("should not append the CLI tools.ps1 invoke fence"):
            text = (self.tree / "skills" / "generate" / "SKILL.md").read_text(encoding="utf-8")
            expect(text).not_to(contain("tools.ps1"))

    with context("with a deployed command file for an mcp-published command operation"):
        with it("should write the context section plus MCP invoke tail — not the full command body"):
            text = (self.tree / "commands" / "sketch.md").read_text(encoding="utf-8")
            expect(text).to(contain("Use MCP tool:"))
            expect(text).not_to(contain("full sketch instructions that must not appear"))

    with context("with a deploy output tree for hosts whose members are annotated mcp"):
        with it("should record each mcp-published operation for server enrollment"):
            names = [op.mcp_name for op in self.harness.deployment.mcp.mcp_operations]
            expect(names).to(contain("sample-mcp.generate"))
            expect(names).to(contain("sample-mcp.sketch"))

        with it("should not bind tool handlers during deploy"):
            server_bound = getattr(self.harness.deployment.mcp, "_bound", False)
            expect(server_bound).to(equal(False))


with description("context guidance registered for deploy") as self:
    with before.each:
        self._tmp = tempfile.mkdtemp()
        self.tree = Path(self._tmp)
        self.host = SampleContextGuidance(format="templates")
        self.harness = Harness(ide="Cursor", path=self.tree)
        self.harness.write_deploy([self.host])

    with after.each:
        shutil.rmtree(self._tmp, ignore_errors=True)

    with context("with a Cursor deploy output tree"):
        with it("should write a skill file whose body equals context guidance instructions"):
            skill = self.tree / "skills" / "sample-tool" / "SKILL.md"
            expect(skill.is_file()).to(equal(True))
            expect(skill.read_text(encoding="utf-8")).to(contain(self.host.instructions.split("\n")[0]))

        with it("should write one rules file per rule slug"):
            rule = self.tree / "rules" / "sample-rule-one.mdc"
            expect(rule.is_file()).to(equal(True))
            expect(rule.read_text(encoding="utf-8")).to(contain("sample rule one"))


with description("context guidance with mcp-published guidance registered for deploy") as self:
    with before.each:
        self._tmp = tempfile.mkdtemp()
        self.tree = Path(self._tmp)
        self.harness = Harness(ide="Cursor", path=self.tree)
        self.harness.write_deploy([SampleMcpContextGuidance(format="templates")])

    with after.each:
        shutil.rmtree(self._tmp, ignore_errors=True)

    with context("with a deployed practice skill when guidance is mcp-published"):
        with it("should write the context section plus MCP invoke tail — not practice guidance instructions"):
            text = (self.tree / "skills" / "sample-tool" / "SKILL.md").read_text(encoding="utf-8")
            expect(text).to(contain("Use MCP tool:"))
            expect(text).to(contain("sample preamble"))
            expect(text).not_to(contain("active format template body for sample tool"))

    with context("with a deploy output tree for hosts whose members are annotated mcp"):
        with it("should record each mcp-published operation for server enrollment"):
            names = [op.mcp_name for op in self.harness.deployment.mcp.mcp_operations]
            expect(names).to(contain("sample-tool.guidance"))

        with it("should not bind tool handlers during deploy"):
            expect(getattr(self.harness.deployment.mcp, "_bound", False)).to(equal(False))
