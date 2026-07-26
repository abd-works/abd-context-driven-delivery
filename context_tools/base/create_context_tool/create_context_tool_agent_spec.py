# @agent-spec-manifest python -m tools agent-spec context_tools/base/create_context_tool/create_context_tool_agent_spec.py
# Agent reading this file: run in chat via Task subagents (runner + judge).
# harness: in_chat
# session: context_tools/.agent_bdd_sessions/car-chronicle.json
"""BDD agent spec for create_context_tool-behavior.md — CarChronicle generate and repair."""

from pathlib import Path

from expects import be_true, equal, expect
from mamba import after, before, context, description, it

from agent_bdd import agent

_REPO_ROOT = Path(__file__).resolve().parents[3]
_SESSIONS = Path(__file__).resolve().parents[2] / ".agent_bdd_sessions"
_CAR_ROOT = (
    "context_tools/base/create_context_tool/examples/car_chronicle"
)
_OUTPUT_DIR = _REPO_ROOT / _CAR_ROOT / "output"
_CAR_CHRONICLE_PY = f"{_CAR_ROOT}/car_chronicle.py"
_CAR_TOOLSET = (
    "context_tools.base.create_context_tool.examples.car_chronicle.car_chronicle:CarChronicle"
)
_GENERATE_YAML = f"""\
toolset: {_CAR_TOOLSET}
action: generate
"""
_REPAIR_YAML = f"""\
toolset: {_CAR_TOOLSET}
action: repair
arguments:
  asset: {_CAR_ROOT}/output/driving-log.md
  violation: Scanner use-driving-voice — chronicle reads like a spec sheet
"""


with description("a CarChronicle generator"):
    with context("with agent and generate action"):
        with before.all:
            self._agent = agent(_REPO_ROOT, _SESSIONS / "car-chronicle.json")
            self.session = self._agent.__enter__()
            self.session.instruct(f"Read {_CAR_CHRONICLE_PY} from the workspace.")
            self.generate_response = self.session.instruct_run(
                "Using shell, run exactly: python -m tools run -\n"
                "Pipe this YAML on stdin:\n"
                f"{_GENERATE_YAML}\n"
                "Return the complete fenced YAML stdout from the CLI.",
                timeout_seconds=120,
            )
            self.chronicle_result = self.session.instruct(
                "Follow the generate instructions and write a driving chronicle entry "
                "for one trip from the Hazzard County garage to the courthouse.",
                timeout_seconds=300,
            )

        with after.all:
            self._agent.__exit__(None, None, None)

        with it("should parse the generate action response with instructions"):
            expect(self.generate_response.ok).to(be_true)
            expect(self.generate_response.action).to(equal("generate"))
            expect(self.generate_response.instructions is not None).to(be_true)

        with it("should name session tools on the generate action tools list"):
            tools = self.generate_response.tools or []
            expect("read_context_index" in tools).to(be_true)
            expect("record_context_root" in tools).to(be_true)

        with it("should inline driving-voice guidance in generate instructions"):
            instructions = str(self.generate_response.instructions).lower()
            expect(
                "driving voice" in instructions or "use-driving-voice" in instructions
            ).to(be_true)

        with it("should write a markdown chronicle under car_chronicle/output"):
            chronicle_files = list(_OUTPUT_DIR.glob("*.md")) if _OUTPUT_DIR.is_dir() else []
            session_text = self.chronicle_result.stdout.lower()
            wrote_file = len(chronicle_files) > 0
            mentioned_output = f"{_CAR_ROOT}/output" in session_text or wrote_file
            expect(mentioned_output).to(be_true)
            if wrote_file:
                body = chronicle_files[0].read_text(encoding="utf-8").lower()
                expect("route" in body or "miles" in body).to(be_true)

        with it("should judge the chronicle as a first-person driving log"):
            chronicle_files = list(_OUTPUT_DIR.glob("*.md")) if _OUTPUT_DIR.is_dir() else []
            chronicle_text = (
                chronicle_files[0].read_text(encoding="utf-8")
                if chronicle_files
                else self.chronicle_result.stdout
            )
            verdict = self.session.ai_judge(
                chronicle_text,
                "The chronicle should be a first-person driving log entry with a named route, "
                "mileage or odometer numbers, and the car's personality.",
            )
            expect(verdict.passed()).to(be_true)

    with context("with agent and repair action"):
        with before.all:
            self._repair_agent = agent(_REPO_ROOT, _SESSIONS / "car-chronicle-repair.json")
            self.repair_session = self._repair_agent.__enter__()
            self.repair_session.instruct(f"Read {_CAR_CHRONICLE_PY} from the workspace.")
            self.repair_response = self.repair_session.instruct_run(
                "Using shell, run exactly: python -m tools run -\n"
                "Pipe this YAML on stdin:\n"
                f"{_REPAIR_YAML}\n"
                "Return the complete fenced YAML stdout from the CLI.",
                timeout_seconds=120,
            )

        with after.all:
            self._repair_agent.__exit__(None, None, None)

        with it("should parse the repair action response with instructions"):
            expect(self.repair_response.ok).to(be_true)
            expect(self.repair_response.action).to(equal("repair"))
            expect(self.repair_response.instructions is not None).to(be_true)

        with it("should name scan on the repair action tools list"):
            tools = self.repair_response.tools or []
            expect("scan" in tools).to(be_true)

        with it("should inline repair.md generator-fix and example-folder guidance"):
            instructions = str(self.repair_response.instructions).lower()
            expect("fix the generator" in instructions).to(be_true)
            expect("descriptive-folder" in instructions).to(be_true)
            expect("delete `runs/`" in instructions).to(be_true)
            expect("do not hand-edit" in instructions).to(be_true)

        with it("should substitute asset and violation arguments in repair instructions"):
            instructions = str(self.repair_response.instructions)
            expect(f"{_CAR_ROOT}/output/driving-log.md" in instructions).to(be_true)
            expect("use-driving-voice" in instructions).to(be_true)
