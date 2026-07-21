# @agent-spec-manifest python -m tools agent-spec clean_code/clean_code_agent_spec.py
# Agent reading this file: run in chat via Task subagents (runner + judge).
# harness: in_chat
# session: clean_code/.sessions/clean-code-manifest.json
"""BDD agent spec for clean-code — agent runs manifest from clean_code.py header and invokes CleanCode."""

from pathlib import Path

from expects import be_true, equal, expect
from mamba import after, before, context, description, it

from agent_bdd import agent
from agent_bdd.agent_cli_bdd import looks_like_tools_run_output

_REPO_ROOT = Path(__file__).resolve().parent.parent
_SESSIONS = Path(__file__).resolve().parent / ".sessions"
_CLEAN_CODE_PY = "clean_code/clean_code.py"
_GENERATE_YAML = """\
toolset: clean_code.clean_code:CleanCode
context:
  format: python
action: generate
"""
_VALIDATE_YAML = """\
toolset: clean_code.clean_code:CleanCode
context:
  format: python
action: validate
"""


with description("a Clean Code generator"):
    with context("with a toolset applied"):
        with context("with agent"):
            with before.all:
                self._agent = agent(_REPO_ROOT, _SESSIONS / "clean-code-manifest.json")
                self.session = self._agent.__enter__()
                self.manifest_result = self.session.instruct(
                    "Run the manifest command from the @toolset-manifest comment at the top of "
                    f"{_CLEAN_CODE_PY}. Show the manifest output."
                )

            with after.all:
                self._agent.__exit__(None, None, None)

            with it("should load manifest listing generate validate and satisfy actions"):
                manifest_text = self.manifest_result.stdout.lower()
                expect("generate" in manifest_text).to(be_true)
                expect("validate" in manifest_text).to(be_true)
                expect("satisfy" in manifest_text).to(be_true)

            with it("should load manifest listing scan tool"):
                manifest_text = self.manifest_result.stdout.lower()
                expect("scan" in manifest_text).to(be_true)
                expect("scanners" in manifest_text).not_to(be_true)

        with context("with agent and generate workflow"):
            with before.all:
                self._workflow_agent = agent(_REPO_ROOT, _SESSIONS / "clean-code-generate.json")
                self.workflow = self._workflow_agent.__enter__()
                self.generate_response = self.workflow.instruct_run(
                    "Using shell, run exactly: python -m tools run -\n"
                    "Pipe this YAML on stdin:\n"
                    f"{_GENERATE_YAML}"
                    "Return the complete fenced YAML stdout from the CLI.",
                    timeout_seconds=120,
                )
                self.build_result = self.workflow.instruct(
                    "Follow the generate instructions from the CLI response: write a minimal "
                    "Python Cart module that holds line items and computes a subtotal. "
                    "Save it under packages/.",
                    timeout_seconds=300,
                )

            with after.all:
                self._workflow_agent.__exit__(None, None, None)

            with it("should parse the generate action response with instructions"):
                expect(self.generate_response.ok).to(be_true)
                expect(self.generate_response.action).to(equal("generate"))
                expect(self.generate_response.instructions is not None).to(be_true)

            with it("should not name scan on the generate action tools list"):
                tools = self.generate_response.tools or []
                expect("scan" in tools).not_to(be_true)

            with it("should write a python module under packages"):
                packages = _REPO_ROOT / "packages"
                py_files = list(packages.rglob("*.py")) if packages.is_dir() else []
                session_text = self.build_result.stdout
                wrote_under_packages = "packages" in session_text.lower() or len(py_files) > 0
                expect(wrote_under_packages).to(be_true)

        with context("with agent and validate workflow"):
            with before.all:
                self._validate_agent = agent(_REPO_ROOT, _SESSIONS / "clean-code-validate.json")
                self.validate_session = self._validate_agent.__enter__()
                self.validate_session.instruct_run(
                    "Using shell, run exactly: python -m tools run -\n"
                    "Pipe this YAML on stdin:\n"
                    f"{_GENERATE_YAML}"
                    "Return the complete fenced YAML stdout from the CLI.",
                    timeout_seconds=120,
                )
                self.validate_session.instruct(
                    "Follow the generate instructions: write a minimal Python Cart module "
                    "with line items and subtotal under packages/.",
                    timeout_seconds=300,
                )
                self.validate_response = self.validate_session.instruct_run(
                    "Using shell, run exactly: python -m tools run -\n"
                    "Pipe this YAML on stdin:\n"
                    f"{_VALIDATE_YAML}"
                    "Return the complete fenced YAML stdout from the CLI.",
                    timeout_seconds=120,
                )
                self.validate_result = self.validate_session.instruct(
                    "Follow the validate instructions: run scan on the Cart module under packages/. "
                    "Report pass or fail per concept — do not fix violations.",
                    timeout_seconds=240,
                )

            with after.all:
                self._validate_agent.__exit__(None, None, None)

            with it("should parse the validate action response with instructions"):
                expect(self.validate_response.ok).to(be_true)
                expect(self.validate_response.action).to(equal("validate"))
                expect(self.validate_response.instructions is not None).to(be_true)

            with it("should name scan on the validate action tools list"):
                tools = self.validate_response.tools or []
                expect("scan" in tools).to(be_true)

            with it("should invoke scan while validating the Cart module"):
                tool_runs = [
                    capture
                    for capture in self.validate_session.session_shell_captures
                    if "tools run" in capture.command.lower() or _looks_like_tools_run_output(capture.output)
                ]
                combined = "\n".join(
                    f"{capture.command}\n{capture.output}" for capture in tool_runs
                )
                combined = combined + "\n" + self.validate_result.stdout
                expect("scan" in combined.lower()).to(be_true)
