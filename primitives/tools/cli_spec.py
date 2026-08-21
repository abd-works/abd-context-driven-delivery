"""CLI run accepts a toolset class ref — no request YAML file."""
import sys
from io import StringIO
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("primitives", "utilities", "context_tools", "context_tools/actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import equal, expect
from mamba import context, description, it

from agent_bdd.yaml_fence import load_fenced
from tools.cli import _ToolsCli


def _run_cli(argv: list[str]) -> tuple[int, dict]:
    stdout = StringIO()
    stderr = StringIO()
    saved_out, saved_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = stdout, stderr
        code = _ToolsCli().main(argv)
    finally:
        sys.stdout, sys.stderr = saved_out, saved_err
    body = stdout.getvalue()
    parsed = load_fenced(body) if body.strip() else {}
    return code, parsed if isinstance(parsed, dict) else {"raw": body}


_CAR = "tools.examples.car:Car"
_CAR_CONTEXT = [
    "--context",
    "make=Toyota",
    "--context",
    "model=Camry",
    "--context",
    "year=2020",
    "--context",
    "personality=calm",
]


with description("python -m tools run"):
    with context("given a toolset class reference and a tool"):
        with it("should invoke the tool without a request YAML file"):
            code, response = _run_cli(
                ["run", _CAR, "--tool", "start", *_CAR_CONTEXT]
            )
            expect(code).to(equal(0))
            expect(response.get("ok")).to(equal(True))
            expect(response.get("tool")).to(equal("start"))
            expect((response.get("resources") or {}).get("running")).to(equal(True))

        with it("should pass --arg values into the tool"):
            code, response = _run_cli(
                [
                    "run",
                    _CAR,
                    "--tool",
                    "speak",
                    *_CAR_CONTEXT,
                    "--arg",
                    "line=hello",
                ]
            )
            expect(code).to(equal(0))
            expect("hello" in str(response.get("result"))).to(equal(True))

    with context("given a toolset class reference and an action"):
        with it("should expand the action and put --fidelity on context"):
            code, response = _run_cli(
                [
                    "run",
                    "context_tools.clean_engineering.clean_engineering:CleanEngineering",
                    "--action",
                    "grill",
                    "--fidelity",
                    "code",
                ]
            )
            expect(code).to(equal(0))
            expect(response.get("ok")).to(equal(True))
            expect(response.get("action")).to(equal("grill"))
            expect(bool(response.get("instructions"))).to(equal(True))

    with context("given a class reference with neither tool nor action"):
        with it("should fail without writing a request file"):
            code, response = _run_cli(["run", _CAR])
            expect(code).to(equal(1))
            expect(response.get("ok")).to(equal(False))


_SUB_AGENT = "sub_agent.examples.parallel_runner.parallel_runner:ParallelRunner"


with description("the tools CLI"):
    with context("that is given a sub_agent tool name"):
        with it("should invoke the method and return its result"):
            code, response = _run_cli(
                [
                    "run",
                    _SUB_AGENT,
                    "--tool",
                    "run_analysis",
                    "--arg",
                    "target=demo",
                ]
            )
            expect(code).to(equal(0))
            expect(response.get("ok")).to(equal(True))
            expect(response.get("tool")).to(equal("run_analysis"))
            expect(response.get("result")).to(equal("analysed:demo"))
