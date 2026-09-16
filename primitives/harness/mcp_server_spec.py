"""BDD spec — MCP manifest and McpServer bind / invoke."""
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
from context_tools.context_guidance.fixtures.sample_tool.sample_tool_host import (
    SampleMcpContextGuidance,
    SampleMcpPractice,
)
from primitives.harness import Harness
from primitives.harness.mcp_server import McpServer


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
        self.host = SampleMcpContextGuidance(format="markdown")
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
        self.host = SampleMcpPractice(format="markdown")
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
        self.host = SampleMcpPractice(format="markdown")
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
