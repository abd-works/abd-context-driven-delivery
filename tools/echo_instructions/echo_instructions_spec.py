"""BDD spec for tools/echo_instructions/echo_instructions.py — EchoInstructions toolset."""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("tools", "cdd_guidance/practices"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import be_a, be_true, equal, expect
from mamba import context, description, it

from echo_instructions.echo_instructions import EchoInstructions
from harness.agent_tools.agent_tools import AgentInstructions

_FENCE_HEADER = "===== DO NOT FOLLOW ANY OF THESE INSTRUCTIONS ====="
_FENCE_FOOTER = "===== END: DO NOT FOLLOW ANY OF THESE INSTRUCTIONS ====="


def _expanded_echo_session() -> str:
    echoer = EchoInstructions()
    func = getattr(type(echoer), "echo_session")
    body = AgentInstructions.for_callable(func, echoer)
    return "\n".join(body.prompt)


with description("an EchoInstructions"):
    with context("that is created"):
        with it("should be an EchoInstructions instance"):
            expect(EchoInstructions()).to(be_a(EchoInstructions))

    with context("whose fence tool is called with a body"):
        with it("should return a string containing the DO-NOT-FOLLOW header"):
            result = EchoInstructions().fence("some instructions")
            expect(_FENCE_HEADER in result).to(be_true)

        with it("should return a string containing the DO-NOT-FOLLOW footer"):
            result = EchoInstructions().fence("some instructions")
            expect(_FENCE_FOOTER in result).to(be_true)

        with it("should place the body between the header and the footer"):
            body = "test body content"
            result = EchoInstructions().fence(body)
            header_pos = result.index(_FENCE_HEADER)
            footer_pos = result.index(_FENCE_FOOTER)
            body_pos = result.index(body)
            expect(header_pos < body_pos < footer_pos).to(be_true)

        with it("should read the instructions from a file when paths is set"):
            import tempfile
            with tempfile.TemporaryDirectory() as folder:
                source = Path(folder) / "instructions.md"
                source.write_text("from the file", encoding="utf-8")
                result = EchoInstructions().fence(paths=str(source))
                expect("from the file" in result).to(be_true)

        with it("should return the fenced block as a plain string"):
            result = EchoInstructions().fence("x")
            expect(result).to(be_a(str))

    with context("whose echo_session action is expanded"):
        with it("should instruct the agent to call fence"):
            prose = _expanded_echo_session()
            expect("fence" in prose).to(be_true)

        with it("should include the STOP instruction"):
            prose = _expanded_echo_session()
            expect("STOP" in prose).to(be_true)

        with it("should include the DO-NOT-EXECUTE instruction"):
            prose = _expanded_echo_session()
            expect("DO NOT EXECUTE" in prose).to(be_true)

        with it("should include the collect-and-emit loop"):
            prose = _expanded_echo_session()
            expect("emit" in prose.lower()).to(be_true)
