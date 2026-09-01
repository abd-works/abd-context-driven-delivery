"""CLI run accepts a toolset class ref — no request YAML file."""
import os
import subprocess
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
from tools.repo_paths import pythonpath_entries, write_venv_pth


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
                    "guidance",
                    "--fidelity",
                    "code",
                ]
            )
            expect(code).to(equal(0))
            expect(response.get("ok")).to(equal(True))
            expect(response.get("action")).to(equal("guidance"))
            expect(bool(response.get("instructions"))).to(equal(True))

        with it("should expand catalog story_map.yaml through the Generate kit"):
            catalog = _REPO_ROOT / "catalog" / "manifests" / "stories" / "story_map.yaml"
            code, response = _run_cli(["run", str(catalog)])
            expect(code).to(equal(0))
            expect(response.get("ok")).to(equal(True))
            expect(response.get("toolset")).to(equal("generate.generate:Generate"))
            expect(response.get("action")).to(equal("generate"))
            expect(response.get("error")).not_to(equal("unknown action"))
            expect(bool(response.get("instructions"))).to(equal(True))

        with it("should expand catalog model.yaml through the Generate kit"):
            catalog = (
                _REPO_ROOT / "catalog" / "manifests" / "clean_engineering" / "model.yaml"
            )
            code, response = _run_cli(["run", str(catalog)])
            expect(code).to(equal(0))
            expect(response.get("ok")).to(equal(True))
            expect(response.get("toolset")).to(equal("generate.generate:Generate"))
            expect(response.get("error")).not_to(equal("unknown action"))

    with context("given a class reference with neither tool nor action"):
        with it("should fail without writing a request file"):
            code, response = _run_cli(["run", _CAR])
            expect(code).to(equal(1))
            expect(response.get("ok")).to(equal(False))


_SUB_AGENT = "tools.examples.parallel_runner.parallel_runner:ParallelRunner"


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


with description("this checkout's tools package"):
    with context("when the venv pth is written for this repo"):
        with it("should list only paths under this repo"):
            entries = pythonpath_entries(_REPO_ROOT)
            expect(entries[0]).to(equal(str(_REPO_ROOT.resolve())))
            for entry in entries:
                expect(Path(entry).resolve().is_relative_to(_REPO_ROOT.resolve())).to(equal(True))

        with it("should make a fresh python -m tools import this repo"):
            write_venv_pth(_REPO_ROOT / ".venv", _REPO_ROOT)
            py = _REPO_ROOT / ".venv" / "Scripts" / "python.exe"
            env = {k: v for k, v in os.environ.items() if k.upper() != "PYTHONPATH"}
            env["PYTHONIOENCODING"] = "utf-8"
            out = subprocess.check_output(
                [str(py), "-c", "import tools; print(tools.__file__)"],
                env=env,
                text=True,
            )
            expect(str(_REPO_ROOT.resolve()).lower() in out.strip().lower()).to(equal(True))
            expect("paradise-mobile" in out.lower()).to(equal(False))
