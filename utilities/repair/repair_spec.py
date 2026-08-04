"""BDD spec for Repair kit - action expansion on BaseContextTool hosts."""

import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("primitives", "utilities", "context_tools"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import be_true, equal, expect
from mamba import after, before, context, description, it

from primitives.actions.action import _ActionRunRequest, _ActionRunner
from primitives.instructions import Instruction
from primitives.instructions import _path_for_name
from tools.tool import Toolset, _ToolsetLoader

_KIT_DIR = Path(__file__).resolve().parent
_CAR_CHRONICLE_DIR = (
    _REPO_ROOT
    / "context_tools"
    / "create_context_tool"
    / "examples"
    / "car_chronicle"
)
_CAR_CHRONICLE_TOOLSET = (
    "context_tools.create_context_tool.examples.car_chronicle.car_chronicle:CarChronicle"
)
_LIFECYCLE_DIR = _REPO_ROOT / "context_tools" / "base"


def _expand(
    instance: Toolset,
    action_name: str,
    *,
    toolset_path: str,
    arguments: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return _ActionRunner.instance().invoke_action(
        _ActionRunRequest(
            request={"toolset": toolset_path, "context": {}},
            toolset_path=toolset_path,
            action_name=action_name,
            context={},
            arguments=arguments or {},
            instance=instance,
        )
    )


def _section(name: str) -> str:
    return Instruction(_path_for_name(_KIT_DIR, name), _KIT_DIR).expand()


def _lifecycle(name: str) -> str:
    return Instruction(_path_for_name(_LIFECYCLE_DIR, name), _LIFECYCLE_DIR).expand()


with description("Repair kit prose"):
    with it("should resolve repair from kit markdown"):
        text = _section("repair")
        expect("Iterate until **validate** passes" in text or "# Repair" in text).to(
            be_true
        )


with description("Repair on a BaseContextTool host"):
    with context("repair expanded on CarChronicle"):
        with before.all:
            cls = _ToolsetLoader.instance().load(_CAR_CHRONICLE_TOOLSET)
            self.host = cls()
            self.contexts = Instruction(
                "\u00a7 Contexts", _CAR_CHRONICLE_DIR, domain_slug="car_chronicle"
            ).expand()
            self.examples = Instruction(
                "examples", _CAR_CHRONICLE_DIR, domain_slug="car_chronicle"
            ).expand()
            self.template = Instruction(
                "car_chronicle-templates",
                _CAR_CHRONICLE_DIR,
                domain_slug="car_chronicle",
            ).expand()
            self.response = _expand(
                self.host,
                "repair",
                toolset_path=_CAR_CHRONICLE_TOOLSET,
                arguments={
                    "asset": (
                        "context_tools/create_context_tool/examples/car_chronicle/output/driving-log.md"
                    ),
                    "violation": (
                        "Scanner: use-driving-voice - chronicle reads like a spec sheet"
                    ),
                },
            )

        with it("should set action to repair"):
            expect(self.response["action"]).to(equal("repair"))

        with it("should name scan on tools"):
            expect(self.response["tools"]).to(equal(["scan"]))

        with it("should inline repair prose"):
            expect(
                "Iterate until **validate** passes" in self.response["instructions"]
            ).to(be_true)
            expect(
                "<domain>/examples/<descriptive-folder>/"
                in self.response["instructions"]
            ).to(be_true)
            expect(
                "Delete `runs/` when the repair is done"
                in self.response["instructions"]
            ).to(be_true)

        with it("should inline root-cause-fix prose"):
            instructions = self.response["instructions"]
            expect("Fix the root cause" in instructions).to(be_true)
            expect("Do not hand-edit" in instructions).to(be_true)
            expect("re-run **generate**" in instructions).to(be_true)
            expect("wait for approval before" in instructions).to(be_true)

        with it("should inline contexts examples and template for root cause"):
            expect(self.contexts in self.response["instructions"]).to(be_true)
            expect(self.examples in self.response["instructions"]).to(be_true)
            expect(self.template in self.response["instructions"]).to(be_true)

        with it("should substitute asset and violation arguments"):
            instructions = self.response["instructions"]
            expect(
                "context_tools/create_context_tool/examples/car_chronicle/output/driving-log.md"
                in instructions
            ).to(be_true)
            expect("use-driving-voice" in instructions).to(be_true)

        with it("should nest validate prose"):
            expect(_lifecycle("validate") in self.response["instructions"]).to(be_true)


with description("log_mistake and log_correction tools"):
    with context("that has a host with a named session"):
        with before.each:
            self.tmp_dir = Path(tempfile.mkdtemp())
            cls = _ToolsetLoader.instance().load(_CAR_CHRONICLE_TOOLSET)
            self.host = cls(path=str(self.tmp_dir), session="test")
            self.log_path = (
                self.tmp_dir / ".context" / "sessions" / "test" / "mistakes.log"
            )

        with after.each:
            shutil.rmtree(str(self.tmp_dir), ignore_errors=True)

        with it("should create mistakes.log when it does not exist"):
            self.host.log_mistake(
                artifact="some/file.md",
                rule="test-rule",
                wrong="bad thing happened",
                original="old",
            )
            expect(self.log_path.is_file()).to(be_true)

        with it("should write the artifact into the entry"):
            self.host.log_mistake(
                artifact="some/file.md",
                rule="test-rule",
                wrong="bad thing happened",
                original="old",
            )
            content = self.log_path.read_text(encoding="utf-8")
            expect("artifact: some/file.md" in content).to(be_true)

        with it("should leave the entry open with no improved output yet"):
            self.host.log_mistake(
                artifact="some/file.md",
                rule="test-rule",
                wrong="bad thing happened",
                original="old",
            )
            content = self.log_path.read_text(encoding="utf-8")
            expect("status: open" in content).to(be_true)

        with it("should append a second entry when the log already exists"):
            self.host.log_mistake(artifact="a.md", rule="r1", wrong="w1", original="o1")
            self.host.log_mistake(artifact="b.md", rule="r2", wrong="w2", original="o2")
            content = self.log_path.read_text(encoding="utf-8")
            expect(content.count("artifact: ")).to(equal(2))

        with it("should complete the matching entry via log_correction, by entry_id"):
            entry_id = self.host.log_mistake(
                artifact="a.md", rule="r1", wrong="w1", original="o1"
            )
            self.host.log_correction(entry_id=entry_id, improved="i1")
            content = self.log_path.read_text(encoding="utf-8")
            expect("status: fixed" in content).to(be_true)
            expect("improved: |\n  i1" in content).to(be_true)

        with it("should keep multiple open mistakes distinct until each is completed"):
            first_id = self.host.log_mistake(
                artifact="a.md", rule="r1", wrong="w1", original="o1"
            )
            second_id = self.host.log_mistake(
                artifact="b.md", rule="r2", wrong="w2", original="o2"
            )
            self.host.log_correction(entry_id=second_id, improved="i2")
            content = self.log_path.read_text(encoding="utf-8")
            expect(content.count("status: open")).to(equal(1))
            expect(content.count("status: fixed")).to(equal(1))
            expect(first_id == second_id).to(equal(False))


class _FakeWorkspace:
    """Minimal stand-in for Session - only .folder is used by Repair/MistakeLog."""

    def __init__(self, folder: Path) -> None:
        self.folder = folder


class _StubScanner:
    """Deterministic scan() double: any file whose content contains 'bad' violates."""

    def scan(self, paths: list) -> str:
        ok = all("bad" not in Path(path).read_text(encoding="utf-8") for path in paths)
        return str({"ok": ok, "rules": ["stub-rule"], "violations": []})


with description("MistakeLog"):
    with before.each:
        self.tmp_dir = Path(tempfile.mkdtemp())
        self.log_path = self.tmp_dir / "sessions" / "repair-evals-loop" / "mistakes.log"

    with after.each:
        shutil.rmtree(str(self.tmp_dir), ignore_errors=True)

    with it("should render tool and fidelity onto an appended entry"):
        from repair.repair import MistakeEntry, MistakeLog

        MistakeLog(self.log_path).append(
            MistakeEntry(
                entry_id="e1",
                artifact="a.md",
                rule="r1",
                wrong="w1",
                original="o1",
                improved="i1",
                tool="Stories",
                fidelity="story_map",
            )
        )
        content = self.log_path.read_text(encoding="utf-8")
        expect("tool: Stories" in content).to(be_true)
        expect("fidelity: story_map" in content).to(be_true)

    with it("should parse every appended entry back, tool and fidelity included"):
        from repair.repair import MistakeEntry, MistakeLog

        log = MistakeLog(self.log_path)
        log.append(
            MistakeEntry(
                entry_id="e1",
                artifact="a.md",
                rule="r1",
                wrong="w1",
                original="o1",
                improved="i1",
                tool="Repair",
                fidelity="story_map",
            )
        )
        entries = log.parse()
        expect(len(entries)).to(equal(1))
        expect(entries[0].artifact).to(equal("a.md"))
        expect(entries[0].tool).to(equal("Repair"))
        expect(entries[0].fidelity).to(equal("story_map"))

    with it("should complete an open entry via its entry_id, in place"):
        from repair.repair import MistakeEntry, MistakeLog

        log = MistakeLog(self.log_path)
        log.append(
            MistakeEntry(
                entry_id="e1", artifact="a.md", rule="r1", wrong="w1", original="o1",
                tool="Repair", fidelity="story_map",
            )
        )
        log.complete("e1", improved="i1", status="fixed")
        entries = log.parse()
        expect(len(entries)).to(equal(1))
        expect(entries[0].improved).to(equal("i1"))
        expect(entries[0].status).to(equal("fixed"))

    with it("should raise when completing an entry_id that was never logged"):
        from repair.repair import MistakeLog

        log = MistakeLog(self.log_path)
        try:
            log.complete("missing-id", improved="i1")
            raised = False
        except ValueError:
            raised = True
        expect(raised).to(be_true)

    with it("should name the archive from the shared tool and fidelity when entries agree"):
        from repair.repair import MistakeEntry, MistakeLog

        log = MistakeLog(self.log_path)
        log.append(
            MistakeEntry(
                entry_id="e1",
                artifact="a.md",
                rule="r1",
                wrong="w1",
                original="o1",
                improved="i1",
                tool="Repair",
                fidelity="story_map",
            )
        )
        repo_root = self.tmp_dir / "repo"
        destination = log.archive(str(repo_root))
        expect("repair-story_map-" in destination.name).to(be_true)
        expect(destination.is_file()).to(be_true)

    with it("should delete the source log once the archive write succeeds"):
        from repair.repair import MistakeEntry, MistakeLog

        log = MistakeLog(self.log_path)
        log.append(
            MistakeEntry(
                entry_id="e1", artifact="a.md", rule="r1", wrong="w1", original="o1", improved="i1",
                tool="Repair", fidelity="story_map",
            )
        )
        log.archive(str(self.tmp_dir / "repo"))
        expect(self.log_path.is_file()).to(equal(False))

    with it("should fall back to the session name when fidelity disagrees"):
        from repair.repair import MistakeEntry, MistakeLog

        log = MistakeLog(self.log_path)
        log.append(
            MistakeEntry(
                entry_id="e1", artifact="a.md", rule="r1", wrong="w1", original="o1", improved="i1",
                tool="Repair", fidelity="story_map",
            )
        )
        log.append(
            MistakeEntry(
                entry_id="e2", artifact="b.md", rule="r2", wrong="w2", original="o2", improved="i2",
                tool="Repair", fidelity="model",
            )
        )
        destination = log.archive(str(self.tmp_dir / "repo"))
        expect("repair-repair_evals_loop-" in destination.name).to(be_true)


with description("RegressionExample and RegressionReport"):
    with before.each:
        self.tmp_dir = Path(tempfile.mkdtemp())
        self.examples_root = self.tmp_dir / "examples"

    with after.each:
        shutil.rmtree(str(self.tmp_dir), ignore_errors=True)

    with it("should pass a fixture whose faulty side still violates and repaired side is clean"):
        from repair.repair import RegressionExample

        example_dir = self.examples_root / "inheritance-crosses-class"
        example_dir.mkdir(parents=True)
        (example_dir / "faultyAsset").write_text("bad", encoding="utf-8")
        (example_dir / "repairedAsset").write_text("good", encoding="utf-8")
        result = RegressionExample(example_dir).verify(_StubScanner())
        expect(result["passed"]).to(equal(True))

    with it("should fail a fixture whose repaired side regressed back to violating"):
        from repair.repair import RegressionExample

        example_dir = self.examples_root / "regressed-case"
        example_dir.mkdir(parents=True)
        (example_dir / "faultyAsset").write_text("bad", encoding="utf-8")
        (example_dir / "repairedAsset").write_text("still bad", encoding="utf-8")
        result = RegressionExample(example_dir).verify(_StubScanner())
        expect(result["repaired_still_clean"]).to(equal(False))
        expect(result["passed"]).to(equal(False))

    with it("should summarize every example folder directly under examples_root"):
        from repair.repair import RegressionReport

        for name in ("case-one", "case-two"):
            folder = self.examples_root / name
            folder.mkdir(parents=True)
            (folder / "faultyAsset").write_text("bad", encoding="utf-8")
            (folder / "repairedAsset").write_text("good", encoding="utf-8")
        report = RegressionReport(self.examples_root).verify_examples(_StubScanner())
        expect(report.summary()).to(equal("Regression clean: 2/2 example(s) still hold."))

    with it("should name any example that regressed in the summary"):
        from repair.repair import RegressionReport

        good = self.examples_root / "case-good"
        good.mkdir(parents=True)
        (good / "faultyAsset").write_text("bad", encoding="utf-8")
        (good / "repairedAsset").write_text("good", encoding="utf-8")
        bad = self.examples_root / "case-bad"
        bad.mkdir(parents=True)
        (bad / "faultyAsset").write_text("bad", encoding="utf-8")
        # repairedAsset missing entirely -> fails verify
        report = RegressionReport(self.examples_root).verify_examples(_StubScanner())
        expect("case-bad" in report.summary()).to(be_true)
        expect("FAILED" in report.summary()).to(be_true)


with description("Repair verify_regression and archive_mistakes tools"):
    with before.each:
        self.tmp_dir = Path(tempfile.mkdtemp())

    with after.each:
        shutil.rmtree(str(self.tmp_dir), ignore_errors=True)

    with it("should report a clean regression summary via the real tool"):
        from repair.repair import Repair

        examples_root = self.tmp_dir / "examples"
        folder = examples_root / "case-one"
        folder.mkdir(parents=True)
        (folder / "faultyAsset").write_text("bad", encoding="utf-8")
        (folder / "repairedAsset").write_text("good", encoding="utf-8")
        repairer = Repair(workspace=_FakeWorkspace(self.tmp_dir), scanner=_StubScanner())
        summary = repairer.verify_regression(str(examples_root))
        expect("clean" in summary.lower()).to(be_true)

    with it("should move the sprint's mistakes.log under the repo root archive"):
        from repair.repair import Repair

        sprint_folder = self.tmp_dir / "sessions" / "repair-evals-loop"
        repairer = Repair(workspace=_FakeWorkspace(sprint_folder))
        entry_id = repairer.log_mistake(
            artifact="a.md", rule="r1", wrong="w1", original="o1",
            tool="Repair", fidelity="story_map",
        )
        repairer.log_correction(entry_id=entry_id, improved="i1")
        repo_root = self.tmp_dir / "repo"
        destination = repairer.archive_mistakes(str(repo_root))
        expect(Path(destination).is_file()).to(be_true)
        expect((sprint_folder / "mistakes.log").is_file()).to(equal(False))


with description("Repair.improve action"):
    with before.all:
        cls = _ToolsetLoader.instance().load(_CAR_CHRONICLE_TOOLSET)
        self.host = cls()
        self.response = _expand(
            self.host,
            "improve",
            toolset_path=_CAR_CHRONICLE_TOOLSET,
            arguments={},
        )

    with it("should set action to improve"):
        expect(self.response["action"]).to(equal("improve"))

    with it("should name log_mistake and log_correction on tools"):
        tools = self.response["tools"]
        expect("log_mistake" in tools).to(be_true)
        expect("log_correction" in tools).to(be_true)

    with it("should list repair as a deferred tool step, not inline its loop"):
        # improve flips self.mode = "tool" before self.repair(...), so the nested
        # action is listed by name instead of eagerly inlining the whole repair.md
        # loop on every improve() call.
        instructions = self.response["instructions"]
        expect("repair" in self.response["tools"]).to(be_true)
        expect("Iterate until **validate** passes" in instructions).to(equal(False))

    with it("should not reference verify_regression or archive_mistakes directly - they are discovered as sub-agents instead"):
        tools = self.response["tools"]
        expect("verify_regression" in tools).to(equal(False))
        expect("archive_mistakes" in tools).to(equal(False))

    with it("should inline the improve.md roadmap"):
        instructions = self.response["instructions"]
        expect("Log the mistake, the moment it's spotted" in instructions).to(be_true)
        expect("Log the correction, once the fix lands" in instructions).to(be_true)
        expect("Root-cause and fix it" in instructions).to(be_true)
        expect("Offer regression, non-blocking" in instructions).to(be_true)
        expect("Offer to archive, once satisfied" in instructions).to(be_true)

    with it("should require user approval before applying a root-cause fix"):
        instructions = self.response["instructions"]
        expect("wait for approval before" in instructions).to(be_true)

    with it("should never run the root-cause step on its own"):
        instructions = self.response["instructions"]
        expect("This never runs on its own" in instructions).to(be_true)


with description("Repair sub-agent tools"):
    with it("should discover repair, verify_regression, and archive_mistakes as non-blocking sub-agents, not normal tools"):
        from repair.repair import Repair
        from sub_agent.sub_agent import discover_sub_agent_tools

        repairer = Repair(workspace=_FakeWorkspace(Path(tempfile.mkdtemp())))
        discovered = discover_sub_agent_tools(repairer)
        for name in ("repair", "verify_regression", "archive_mistakes"):
            expect(name in discovered).to(be_true)
            entry = discovered[name].signature_entry
            expect(entry["kind"]).to(equal("sub_agent"))
            expect(entry["launch"]).to(equal("non_blocking"))

    with it("should carry the repair.md instructions for the repair sub-agent"):
        from repair.repair import Repair
        from sub_agent.sub_agent import discover_sub_agent_tools

        repairer = Repair(workspace=_FakeWorkspace(Path(tempfile.mkdtemp())))
        discovered = discover_sub_agent_tools(repairer)
        instructions = discovered["repair"].instructions
        expect("Iterate until **validate** passes" in instructions).to(be_true)

    with it("should carry the verify_regression docstring for the regression sub-agent"):
        from repair.repair import Repair
        from sub_agent.sub_agent import discover_sub_agent_tools

        repairer = Repair(workspace=_FakeWorkspace(Path(tempfile.mkdtemp())))
        discovered = discover_sub_agent_tools(repairer)
        instructions = discovered["verify_regression"].instructions
        expect("faultyAsset" in instructions).to(be_true)

    with it("should still be directly callable as plain Python for tests and scripts"):
        from repair.repair import Repair

        repairer = Repair(workspace=_FakeWorkspace(Path(tempfile.mkdtemp())))
        examples_root = Path(tempfile.mkdtemp()) / "examples"
        summary = repairer.verify_regression(str(examples_root))
        expect("No regression examples found" in summary).to(be_true)
