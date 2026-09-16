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

from context_tools.agent_toolset.validate import Validate
from context_tools.context_guidance.fixtures.agentic_ops.agentic_ops import (
    SampleAgenticOps,
    SampleMcpOps,
)
from context_tools.context_guidance.fixtures.agentic_ops.hook_ops import SampleHookOps
from context_tools.context_guidance.fixtures.other_tool.other_tool_host import OtherToolHost
from context_tools.context_guidance.fixtures.sample_tool.sample_tool_host import (
    SampleContextGuidance,
    SampleMcpContextGuidance,
    SampleMcpPractice,
    SamplePracticeGuidance,
    SamplePracticeWithFidelities,
    SampleToolHost,
)
from context_tools.context_guidance.fixtures.split_tool.split_tool import SplitPracticeGuidance
from primitives.harness import Harness
from primitives.harness.mcp_server import McpServer
from primitives.markdown import HTML, Markdown
from utilities.catalog_generator.catalog import Catalog


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


def _assert_shared_contexts(host):
    expect(host.context).to(contain("preamble"))
    expect(host.guidance).not_to(contain("preamble"))
    expect(host.rules.entries).not_to(equal({}))


with description("a context tool module with one domain markdown file named for the context tool") as self:
    with before.each:
        self.host = SamplePracticeGuidance(format="templates")

    with context("with the context property read"):
        with it("should return the Contexts preamble"):
            expect(self.host.context).to(contain("sample preamble"))

    with context("with the guidance property read"):
        with it("should return the Guidance section body only"):
            expect(self.host.guidance).to(contain("known prose for guidance in sample tool"))
            expect(self.host.guidance).not_to(contain("sample preamble"))

    with context("with a Shared rules section containing scanner bullets"):
        with context("with the rules property read"):
            with it("should parse bullets into a rules collection"):
                expect("sample-rule-one" in self.host.rules.entries).to(equal(True))

            with it("should expose slug, body, optional fidelity, and zero or one scanner on each rule"):
                rule = self.host.rules.entries["sample-rule-one"]
                expect(rule.slug).to(equal("sample-rule-one"))
                expect(rule.body).to(contain("sample rule one"))
                expect(rule.scanner is not None).to(equal(True))

        with context("with validate read on one rule"):
            with it("should return instructions to evaluate the current context against that rule"):
                rule = self.host.rules.entries["sample-rule-one"]
                expect(rule.validate()).to(contain("Evaluate the current context"))

            with it("should tell the agent to run the scanner when the rule has one"):
                rule = self.host.rules.entries["sample-rule-one"]
                expect(rule.validate()).to(contain("Run the scanner"))

        with context("with validate read on the rules collection"):
            with it("should return every child rule's validate instructions in one shot"):
                text = self.host.rules.validate()
                expect(text).to(contain("sample-rule-one"))

    with context("with the instructions property read"):
        with it("should join context, guidance, formatted rules, and the template for the active format"):
            text = self.host.instructions
            expect(text).to(contain("sample preamble"))
            expect(text).to(contain("known prose for guidance in sample tool"))
            expect(text).to(contain("active format template body for sample tool"))
            expect(text).not_to(contain("sketch guidance body only"))

    with context("with a templates folder beside the module"):
        with context("with template files such as slug-templates and slug-sketch inside the folder"):
            with context("with the templates property read"):
                with it("should map each format key to a relative path under templates"):
                    expect(self.host.templates.get("templates")).to(contain("templates/"))

            with context("with one format key selected"):
                with it("should return the file content at the mapped path"):
                    expect(self.host.instructions).to(contain("active format template body for sample tool"))


with description("a context tool module with section files and subsection folders named for the context tool") as self:
    with before.each:
        self.host = SplitPracticeGuidance(format="templates")

    with context("with the context property read"):
        with it("should return the Contexts preamble"):
            expect(self.host.context).to(contain("split preamble from contexts file"))

    with context("with the guidance property read"):
        with it("should return the Guidance section body only"):
            expect(self.host.guidance).to(contain("split guidance section body only"))

    with context("with a Shared rules section containing scanner bullets"):
        with context("with the rules property read"):
            with it("should parse bullets into a rules collection"):
                expect("split-rule" in self.host.rules.entries).to(equal(True))


with description("a validate action on practice guidance") as self:
    with before.each:
        self.host = SamplePracticeGuidance(format="templates")
        self.action = Validate()

    with context("with no rule passed"):
        with it("should return validate instructions for every rule in one shot"):
            expect(self.action.validate(self.host)).to(contain("sample-rule-one"))

    with context("with one rule passed"):
        with it("should return validate instructions for that rule only"):
            rule = self.host.rules.entries["sample-rule-one"]
            expect(self.action.validate(self.host, rule)).to(contain("sample-rule-one"))


with description("a context tool module with shared contexts format registered for deploy") as self:
    with before.each:
        self._tmp = tempfile.mkdtemp()
        self.tree = Path(self._tmp)
        self.host = SamplePracticeGuidance(format="templates")
        self.harness = Harness(ide="Cursor", path=self.tree)
        self.harness.write_deploy([self.host])

    with after.each:
        shutil.rmtree(self._tmp, ignore_errors=True)

    with context("with a Cursor deploy output tree"):
        with it("should write a skill file whose body equals practice guidance instructions"):
            text = (self.tree / "skills" / "sample-tool" / "SKILL.md").read_text(encoding="utf-8")
            expect(text).to(contain("sample preamble"))

        with it("should write one practice guidance rules file per practice guidance rule slug"):
            expect((self.tree / "rules" / "sample-rule-one.mdc").is_file()).to(equal(True))


with description("a context tool module with one domain markdown file named for the context tool and fidelity sections") as self:
    with before.each:
        self.practice = SamplePracticeWithFidelities(format="templates")
        self.sketch = self.practice.fidelities.entries["sketch"]
        self.spec = self.practice.fidelities.entries["spec"]

    with context("with the guidance property read on fidelity guidance"):
        with it("should return Guidance under that fidelity name only"):
            expect(self.sketch.guidance).to(contain("sketch guidance body only"))
            expect(self.sketch.guidance).not_to(contain("spec guidance body only"))

    with context("with the rules property read on fidelity guidance"):
        with it("should return a rules collection for that fidelity name only"):
            expect("sketch-rule" in self.sketch.rules.entries).to(equal(True))

        with it("should not include rules from sibling fidelity sections"):
            expect("spec-rule" in self.sketch.rules.entries).to(equal(False))

    with context("with two fidelities declared shallower before deeper in the collection"):
        with context("with the instructions property read on the deeper fidelity guidance"):
            with it("should include prior fidelity sections in context in declaration order"):
                expect(self.spec.context).to(contain("sketch guidance body only"))

            with it("should not include later fidelity sections or sibling templates"):
                expect(self.sketch.context).not_to(contain("spec guidance body only"))

        with context("with a markdown-backed property read as HTML on the deeper fidelity guidance"):
            with it("should return HTML formatted from that fidelity section body"):
                rendered = HTML.from_markdown(self.spec.guidance)
                expect(str(rendered)).to(contain("<p>"))
                expect(str(rendered)).to(contain("spec guidance body only"))

        with context("with the rules property read on the deeper fidelity guidance"):
            with it("should match the same bullets already formatted into fidelity instructions"):
                expect(self.spec.instructions).to(contain("spec-rule"))


with description("a context tool module with fidelity sections registered for deploy") as self:
    with before.each:
        self._tmp = tempfile.mkdtemp()
        self.tree = Path(self._tmp)
        self.host = SamplePracticeWithFidelities(format="templates")
        Harness(ide="Cursor", path=self.tree).write_deploy([self.host])

    with after.each:
        shutil.rmtree(self._tmp, ignore_errors=True)

    with context("with a Cursor deploy output tree"):
        with it("should write one fidelity command file per fidelity whose body equals that fidelity instructions"):
            sketch = (self.tree / "commands" / "sample-tool-sketch.md").read_text(encoding="utf-8")
            expect(sketch).to(contain("sketch guidance body only"))

        with it("should write one fidelity rules file per fidelity rule slug"):
            expect((self.tree / "rules" / "sketch-rule.mdc").is_file()).to(equal(True))


with description("a guidance collection of context guidance children") as self:
    with before.each:
        self.practice = SamplePracticeWithFidelities(format="templates")
        self.collection = self.practice.fidelities

    with context("with the instructions property read on the collection"):
        with it("should join each child instructions string in declaration order"):
            text = self.collection.instructions
            expect(text.index("sketch guidance")).to(equal(text.find("sketch guidance")))
            expect(text).to(contain("sketch guidance body only"))
            expect(text).to(contain("spec guidance body only"))

    with context("with the rules property read on the collection"):
        with it("should return a rules collection keyed by each child key"):
            expect("sketch" in self.collection.rules.entries).to(equal(True))

        with it("should keep each child's rules under that child's key"):
            child_rules = self.collection.rules.entries["sketch"]
            expect("sketch-rule" in child_rules.entries).to(equal(True))

        with it("should return every child rule's validate instructions in one shot"):
            expect(self.collection.rules.validate()).to(contain("sketch-rule"))


with description("practice guidance with fidelities examples and templates beside the module") as self:
    with before.each:
        self.host = SamplePracticeWithFidelities(format="templates")

    with context("with the instructions property read on practice guidance"):
        with it(
            "should join context guidance instructions with each fidelity instructions in declaration order sketch first"
        ):
            text = self.host.instructions
            expect(text.find("sketch guidance") < text.find("spec guidance")).to(equal(True))

        with it("should not inline examples into instructions"):
            expect(self.host.instructions).not_to(contain("example file not inlined"))

    with context("with the examples property read on practice guidance"):
        with it("should return examples folder content as a separate property not inside instructions"):
            expect(self.host.examples).to(contain("example file not inlined"))

    with context("with a markdown-backed property read as HTML on practice guidance"):
        with it("should return HTML formatted from that property extract"):
            rendered = Markdown.from_label(self.host, "guidance").html()
            expect(str(rendered)).to(contain("<p>"))

    with context("with fidelity set at invoke on practice guidance"):
        with it("should resolve active format from the named fidelity default format"):
            self.host.fidelity = "sketch"
            self.host.format = self.host.fidelities.entries["sketch"].default_format or self.host.format
            expect(self.host.fidelity).to(equal("sketch"))


with description("a context tool module with fidelities and assembly registered for deploy") as self:
    with before.each:
        self._tmp = tempfile.mkdtemp()
        self.tree = Path(self._tmp)
        self.host = SamplePracticeWithFidelities(format="templates")
        Harness(ide="Cursor", path=self.tree).write_deploy([self.host])

    with after.each:
        shutil.rmtree(self._tmp, ignore_errors=True)

    with context("with a Cursor deploy output tree"):
        with it("should emit the practice skill, practice rules, fidelity commands, and fidelity rules in one pass"):
            expect((self.tree / "skills" / "sample-tool" / "SKILL.md").is_file()).to(equal(True))
            expect((self.tree / "rules" / "sample-rule-one.mdc").is_file()).to(equal(True))
            expect((self.tree / "commands" / "sample-tool-sketch.md").is_file()).to(equal(True))
            expect((self.tree / "rules" / "spec-rule.mdc").is_file()).to(equal(True))


with description("practice guidance that has been deployed") as self:
    with before.each:
        self._tmp = tempfile.mkdtemp()
        self.tree = Path(self._tmp)
        Harness(ide="Cursor", path=self.tree).write_deploy(
            [SamplePracticeGuidance(format="templates")]
        )

    with after.each:
        shutil.rmtree(self._tmp, ignore_errors=True)

    with context("with members that are not annotated mcp"):
        with context("with deployed skill command and rules bodies"):
            with it("should append the CLI invoke fence at the bottom of each body"):
                skill = (self.tree / "skills" / "sample-tool" / "SKILL.md").read_text(encoding="utf-8")
                expect(skill).to(contain("tools.ps1 run -"))


with description("practice guidance that has been deployed for VS Code") as self:
    with before.each:
        self._tmp = tempfile.mkdtemp()
        self.tree = Path(self._tmp)
        Harness(ide="VS Code", path=self.tree).write_deploy(
            [SamplePracticeWithFidelities(format="templates")]
        )

    with after.each:
        shutil.rmtree(self._tmp, ignore_errors=True)

    with context("with a VS Code deploy output tree"):
        with it("should write fidelity command files under github prompts not under cursor commands"):
            expect((self.tree / "prompts" / "sample-tool-sketch.md").is_file()).to(equal(True))


with description("an MCP manifest file") as self:
    with context("that has been written by a deploy whose walked members are annotated mcp"):
        with before.each:
            self._tmp = tempfile.mkdtemp()
            self.tree = Path(self._tmp)
            Harness(ide="Cursor", path=self.tree).write_deploy([SampleMcpOps()])

        with after.each:
            shutil.rmtree(self._tmp, ignore_errors=True)

        with it("should list stdio server command and comma-separated toolset refs for walked classes"):
            text = (self.tree / "mcp.json").read_text(encoding="utf-8")
            expect(text).to(contain("python"))
            expect(text).to(contain("--toolsets"))
            expect(text).to(contain("sample-mcp"))

    with context("that has been written by a deploy with no mcp-published members"):
        with before.each:
            self._tmp = tempfile.mkdtemp()
            self.tree = Path(self._tmp)
            Harness(ide="Cursor", path=self.tree).write_deploy([SampleAgenticOps()])

        with after.each:
            shutil.rmtree(self._tmp, ignore_errors=True)

        with it("should omit the MCP manifest file"):
            expect((self.tree / "mcp.json").exists()).to(equal(False))


with description("a bare agentic toolset with an agent-tool operation annotated for mcp") as self:
    with before.each:
        self._tmp = tempfile.mkdtemp()
        self.tree = Path(self._tmp)
        self.host = SampleMcpOps()
        self.harness = Harness(ide="Cursor", path=self.tree)
        self.harness.write_deploy([self.host])
        self.server = McpServer()
        self.server.bind_from(self.harness.deployment.mcp)

    with after.each:
        shutil.rmtree(self._tmp, ignore_errors=True)

    with context("that has been deployed"):
        with context("with an MCP server started from manifest toolset refs written during that deploy"):
            with it("should enroll that operation as a prompt under the mcp name for generate"):
                expect("sample-mcp.generate" in self.server.prompts).to(equal(True))

            with it("should enroll from mcp operations recorded at deploy not from a second annotation scan on the class"):
                expect(len(self.harness.deployment.mcp.mcp_operations) > 0).to(equal(True))

            with context("with a prompts call for that enrolled mcp name"):
                with it("should return the orchestration result from that operation"):
                    result = self.server.invoke_prompt("sample-mcp.generate")
                    expect(str(result)).to(contain("full generate instructions"))


with description("context guidance with guidance annotated for mcp") as self:
    with before.each:
        self._tmp = tempfile.mkdtemp()
        self.harness = Harness(ide="Cursor", path=self._tmp)
        self.host = SampleMcpContextGuidance(format="templates")
        self.harness.write_deploy([self.host])
        self.server = McpServer()
        self.server.bind_from(self.harness.deployment.mcp)

    with after.each:
        shutil.rmtree(self._tmp, ignore_errors=True)

    with context("that has been deployed"):
        with context("with an MCP server started from manifest toolset refs written during that deploy"):
            with context("with a prompts call for that enrolled mcp name"):
                with it("should return the same compound instructions string the read path assembles"):
                    result = self.server.invoke_prompt("sample-tool.guidance")
                    expect(result).to(equal(self.host.instructions))


with description("practice guidance with guidance annotated for mcp") as self:
    with before.each:
        self._tmp = tempfile.mkdtemp()
        self.harness = Harness(ide="Cursor", path=self._tmp)
        self.host = SampleMcpPractice(format="templates")
        self.harness.write_deploy([self.host])
        self.server = McpServer()
        self.server.bind_from(self.harness.deployment.mcp)

    with after.each:
        shutil.rmtree(self._tmp, ignore_errors=True)

    with context("that has been deployed"):
        with context("with an MCP server started from manifest toolset refs written during that deploy"):
            with context("with a prompts call for the practice skill enrolled mcp name"):
                with it("should return practice guidance instructions as the prompt source"):
                    result = self.server.invoke_prompt("sample-tool.guidance")
                    expect(result).to(equal(self.host.instructions))


with description("fidelity guidance with guidance annotated for mcp") as self:
    with before.each:
        self._tmp = tempfile.mkdtemp()
        self.harness = Harness(ide="Cursor", path=self._tmp)
        self.host = SampleMcpPractice(format="templates")
        self.harness.write_deploy([self.host])
        self.server = McpServer()
        self.server.bind_from(self.harness.deployment.mcp)

    with after.each:
        shutil.rmtree(self._tmp, ignore_errors=True)

    with context("that has been deployed"):
        with context("with an MCP server started from manifest toolset refs written during that deploy"):
            with context("with a prompts call for that fidelity enrolled mcp name"):
                with it("should return fidelity guidance instructions as the prompt source"):
                    names = list(self.server.prompts)
                    expect(any("sketch" in n or "guidance" in n for n in names)).to(equal(True))


with description("generated catalog pages") as self:
    with context("that have been built from the guidance registry"):
        with before.each:
            self._tmp = tempfile.mkdtemp()
            self.out = Path(self._tmp)
            self.catalog = Catalog.from_registry([SamplePracticeWithFidelities(format="templates")])
            self.catalog.generate_catalog(self.out)

        with after.each:
            shutil.rmtree(self._tmp, ignore_errors=True)

        with it("should write each practice guidance markdown property as HTML to its own page"):
            html_files = list(self.out.glob("*.html"))
            expect(len(html_files) > 0).to(equal(True))

        with it("should write each fidelity guidance markdown property as HTML to its own page"):
            names = {p.name for p in self.out.glob("*.html")}
            expect(any("sketch" in n for n in names)).to(equal(True))

        with it("should not scrape deployed markdown files or heading structure from disk"):
            expect(any(p.suffix == ".md" for p in self.out.iterdir())).to(equal(False))


with description("a Cursor hooks config") as self:
    with context("that has been deployed with hook sources in the walk"):
        with before.each:
            self._tmp = tempfile.mkdtemp()
            self.tree = Path(self._tmp)
            Harness(ide="Cursor", path=self.tree).write_deploy([SampleHookOps()])

        with after.each:
            shutil.rmtree(self._tmp, ignore_errors=True)

        with it("should write hooks manifest entries for each registered hook event"):
            text = (self.tree / "hooks.json").read_text(encoding="utf-8")
            expect(text).to(contain("stop"))

        with it("should write hook skill files for hook-published agent-instructions operations"):
            expect((self.tree / "skills" / "hook-auto_turn" / "SKILL.md").is_file()).to(equal(True))

    with context("that has been partially deployed with no hook sources emitted"):
        with before.each:
            self._tmp = tempfile.mkdtemp()
            self.tree = Path(self._tmp)
            prior = self.tree / "hooks.json"
            prior.write_text('{"hooks": [{"event": "stop"}]}\n', encoding="utf-8")
            Harness(ide="Cursor", path=self.tree).write_deploy([SampleAgenticOps()])

        with after.each:
            shutil.rmtree(self._tmp, ignore_errors=True)

        with it("should leave hooks manifest unchanged from a prior full deploy"):
            text = (self.tree / "hooks.json").read_text(encoding="utf-8")
            expect(text).to(contain("stop"))
