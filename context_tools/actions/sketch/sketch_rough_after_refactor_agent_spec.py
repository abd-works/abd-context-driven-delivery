# @agent-spec-manifest python -m tools agent-spec context_tools/actions/sketch/sketch_rough_after_refactor_agent_spec.py
# Agent reading this file: run in chat via Task subagents (runner + judge) or CLI agent BDD.
# harness: cli
# session: context_tools/actions/sketch/.context/.agent_bdd_sessions/sketch-rough-32.json
"""Agent BDD — #32 validate sketch still fails after refactor (skill path).

Mistakes under test:
- grilling not sketching
- generating when not asked to
- sketching in different files

Asserts the **run outcome on disk** (sketch file content), not that prompts exist
or that the agent claims success in chat.
"""

from pathlib import Path

from expects import be_true, equal, expect
from mamba import description, it

from agent_bdd import (
    agent,
    ai_judge,
    follow_instructions,
    read_workspace,
    repo_root_from,
    run_skill,
    sessions_dir,
)
from harness.harness import Harness

_REPO = repo_root_from(__file__, parents=3)
_SESSIONS = sessions_dir(__file__)
_SKETCH_CMD = ".cursor/commands/sketch.md"
_CE = "context_tools.clean_engineering.clean_engineering:CleanEngineering"
_STORIES = "context_tools.stories.stories:Stories"

# Fixed path so the example can assert the artifact, not chat claims.
_SKETCH_OUT = Path(".context") / "agent-bdd-plorgle-inventory-sketch.md"
_SKETCH_OUT_ABS = _REPO / _SKETCH_OUT

_RANDOM = (
    "Plorgle inventory for zibbit flarns. Stories at model and scenario level only. "
    "Gibberish nouns: quorble, snorfex, wembly. Do not invent a real product."
)


def _session(name: str) -> Path:
    path = _SESSIONS / f"{name}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.unlink(missing_ok=True)
    return path


def _deploy_sketch() -> None:
    Harness("Cursor", repo_root=_REPO).write_deploy(source="sketch")


def _context_sketch_files() -> set[Path]:
    hits: set[Path] = set()
    for p in _REPO.rglob("*sketch*.md"):
        if not p.is_file():
            continue
        if ".context" not in p.parts:
            continue
        if "templates" in p.parts or "node_modules" in p.parts:
            continue
        if ".agent_bdd_sessions" in p.parts:
            continue
        hits.add(p.resolve())
    return hits


def _looks_like_formal_generate(path: Path) -> bool:
    text = path.read_text(encoding="utf-8", errors="replace").lower()
    markers = (
        "@toolset-manifest",
        "class ",
        "def generate",
        "formal production",
    )
    # Generated code / module-context dumps — not interim sketch markup.
    return any(m in text for m in markers) and "fidelity:" not in text[:400].lower()


with description("sketch after the refactor (#32)"):
    with it(
        "should write one model+scenario sketch file via the sketch skill "
        "without grilling, generating, or splitting across files"
    ):
        _deploy_sketch()
        _SKETCH_OUT_ABS.parent.mkdir(parents=True, exist_ok=True)
        _SKETCH_OUT_ABS.unlink(missing_ok=True)
        before = _context_sketch_files()

        with agent(_REPO, _session("sketch-rough-32")) as block:
            read_workspace(_SKETCH_CMD)
            read_workspace("context_tools/actions/sketch/sketch.md")
            read_workspace(
                "context_tools/clean_engineering/templates/clean_engineering-sketch.md"
            )

            response = run_skill(
                _SKETCH_CMD,
                repo_root=_REPO,
                arguments={"tools": [_CE, _STORIES]},
                timeout_seconds=300,
                require_agent_shell=True,
            )
            expect(response.ok).to(equal(True))

            follow_instructions(
                "You are validating the /sketch skill. Domain (random text — treat as "
                "serious domain nouns):\n"
                f"{_RANDOM}\n\n"
                "Using ONLY the sketch skill / Sketch.sketch instructions you already have "
                "for clean_engineering + stories:\n"
                "1. Produce ONE interim sketch that covers stories at the **model** level "
                "and the **scenario** level for this Plorgle/zibbit domain.\n"
                f"2. Persist with save_sketch to exactly `{_SKETCH_OUT.as_posix()}` "
                "(overwrite if present). Do not write other sketch files for this slice.\n"
                "3. Do NOT open a long grill loop — at most one short confirm if the skill "
                "forces review. Do NOT call generate / formal generation.\n"
                "4. Stop when that file is on disk. Do not summarize instead of writing.",
                timeout_seconds=600,
            )

            # Hard asserts on the run result — not chat claims or prompt text.
            expect(_SKETCH_OUT_ABS.is_file()).to(be_true)
            sketch_text = _SKETCH_OUT_ABS.read_text(encoding="utf-8")
            expect(len(sketch_text.strip()) > 80).to(be_true)
            lowered = sketch_text.lower()
            expect("plorgle" in lowered or "zibbit" in lowered).to(be_true)
            expect(
                "quorble" in lowered or "snorfex" in lowered or "wembly" in lowered
            ).to(be_true)

            after = _context_sketch_files()
            new_sketches = sorted(after - before)
            # Allowed: the required path. Extra new *sketch*.md files = split-file defect.
            unexpected = [
                p for p in new_sketches if p.resolve() != _SKETCH_OUT_ABS.resolve()
            ]
            expect(unexpected).to(equal([]))

            formal_hits = [
                p for p in new_sketches if _looks_like_formal_generate(p)
            ]
            expect(formal_hits).to(equal([]))

            ai_judge(
                sketch_text,
                "Judge the FILE CONTENTS only (the agent run artifact), not chat.\n"
                "PASS only if ALL hold:\n"
                "1) This is an interim sketch (stories model + scenario), not grill Q&A "
                "and not formal generated production code/docs.\n"
                "2) It covers both model-level and scenario-level story material for the "
                "Plorgle/zibbit domain (gibberish nouns ok).\n"
                "3) Content is substantive sketch markup, not an empty stub or a claim "
                "that work was done elsewhere.\n"
                "FAIL if this is mostly questions, a generate dump, or empty/off-domain.",
            )
