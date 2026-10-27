"""Sketch prompts served through a stood-up MCP host. Heavy: each case starts the host."""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("tools", "cdd_guidance/practices", "cdd_guidance/actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.modules.pop("sketch", None)

from expects import contain, equal, expect
from mamba import description, it


with description("an MCP sketch prompt"):
    with it("should return sketch instructions for prose that contains a colon"):
        from harness.mcp.mcp_server import McpHost

        repo = Path(__file__).resolve().parents[3]
        host = McpHost.standup(repo / ".cursor" / "mcp.json", repo=repo)
        prose = "Three client perspectives: prospect onboarding and active account."
        result = str(host._runtime.invoke_prompt("sketch.sketch", {"guidance": prose}))
        expect(result).to(contain("Conduct a relentless grilling interview"))
        expect("ModuleNotFoundError" in result).to(equal(False))

    with it("should inline listed practice rules into the sketch instructions"):
        from harness.mcp.mcp_server import McpHost

        repo = Path(__file__).resolve().parents[3]
        host = McpHost.standup(repo / ".cursor" / "mcp.json", repo=repo)
        result = str(
            host._runtime.invoke_prompt(
                "sketch.sketch",
                {"guidance": ["cdd_guidance.practices.bdd.bdd:Bdd"]},
            )
        )
        expect(result).to(contain("observable-behavior"))

    with it("should include each practice sketch template and rules"):
        from harness.mcp.mcp_server import McpHost

        repo = Path(__file__).resolve().parents[3]
        host = McpHost.standup(repo / ".cursor" / "mcp.json", repo=repo)
        result = str(
            host._runtime.invoke_prompt(
                "sketch.sketch",
                {"guidance": ["stories", "clean-engineering-model"]},
            )
        )
        expect(result).to(contain("verb-noun-format"))
        expect(result).to(contain("shape-classes-around-resources"))
        expect(result).to(contain("Sketch the story hierarchy"))
        expect(result).to(contain("terse indent notation"))
