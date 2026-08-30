# @toolset-manifest python -m tools manifest grill_context.grill_context:GrillContext
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
# Do not author behavior from this Python source.
"""Grill a plan against codebase context - relentless interview with context-aware exploration."""
from __future__ import annotations

import json
from pathlib import Path

from harness.harness_tool import prompt
from lifecycle import LifecycleAction
from primitives.actions.action import agent_instructions, agentic_toolset
from tools.tool import agent_tool
from workspace import docs_dir


@agentic_toolset
class GrillContext(LifecycleAction):
    """Interview a plan relentlessly against the codebase context until reaching shared understanding."""

    def _grill_answers_path(self, root: str) -> Path:
        """Resolve grill-answers.md under the durable docs dir (pure).

        Survives multiple sessions: ``{path}/.context/grill-answers.md``.
        ``root`` may be ``session.path``, ``session.docs_dir``, or ``session.folder``
        — all resolve to the same ``.context`` file.
        """
        return docs_dir(root) / "grill-answers.md"

    def _appended_answers_content(self, existing: str | None, heading: str, body: str) -> str:
        """Compose the full grill-answers document after appending one entry (pure).

        ``existing`` is the current file contents, or ``None`` when the file has
        not been created yet - in which case a fresh document header is emitted.
        """
        base = existing if existing is not None else "# Grill Answers\n\n"
        entry = f"### {heading}\n\n{body.strip()}\n\n"
        return base + entry

    @agent_tool
    def explore_context_files(self, root: str) -> str:
        """Scan a directory tree for context files.
        root defaults to session.path (working area) so durable .context docs are visible.
        Finds: files whose name contains 'context', and any file inside a .context/ subfolder.
        Searches recursively. Skips __pycache__ and private (_) paths.
        Returns a JSON array of {path, kind} where kind is 'context-named' or 'context-folder'."""
        results: list[dict] = []
        root_path = Path(root)
        if not root_path.exists():
            return json.dumps([])
        for candidate in sorted(root_path.rglob("*")):
            if not candidate.is_file():
                continue
            parts = candidate.relative_to(root_path).parts
            if any(part.startswith("__") or part.startswith("_") for part in parts[:-1]):
                continue
            if "context" in candidate.name.lower():
                results.append({"path": str(candidate), "kind": "context-named"})
            elif ".context" in parts:
                results.append({"path": str(candidate), "kind": "context-folder"})
        return json.dumps(results, indent=2)

    @agent_tool
    def read_context_file(self, path: str) -> str:
        """Read a context file and return its contents.
        Use after explore_context_files to read files assessed as relevant."""
        return Path(path).read_text(encoding="utf-8")

    @agent_tool
    def write_grill_answer(self, root: str, heading: str, body: str) -> str:
        """Append one insight to grill-answers.md under the given heading.
        root defaults to session.path (or session.docs_dir). File is
        {path}/.context/grill-answers.md — durable across sessions, not under
        sessions/{name}/. If no sprint exists yet: confirm path, suggest slug, open.
        Creates the file if it does not exist. Call immediately when an insight is resolved - do not batch.
        heading: short title for the insight (e.g. 'How actions are discovered').
        body: 1-3 concise sentences. Reference file paths and names instead of repeating logic."""
        answers_path = self._grill_answers_path(root)
        answers_path.parent.mkdir(parents=True, exist_ok=True)
        existing = answers_path.read_text(encoding="utf-8") if answers_path.exists() else None
        answers_path.write_text(self._appended_answers_content(existing, heading, body), encoding="utf-8")
        return str(answers_path)

    @prompt(name="grill")
    @agent_instructions
    def grill(self, tools: list) -> str:
        """Grill then generate - pure grill loop, then the host generate body."""
        self.begin(tools, action="grill")
        self.grill_with_context()
        for host in self.context_tools(tools):
            self._generate().generate(tools=[host])
        self.end()
        return "Grill complete; generate instructions applied."

    def _generate(self):
        from generate.generate import Generate

        return Generate()

    @agent_instructions
    def grill_with_context(self, plan: str) -> str:
        """Conduct a relentless grilling interview about {plan} - ask each question with concept-grounded framing and option rationales (never bare choices), using the AskQuestion Cursor tool when available. Prefer contextual thinking questions over syntax trivia. When a sketch exists for this plan, use grilling to validate what the sketch claimed — sketch and grill must not run disconnected. Batch very similar questions into one AskQuestion so the loop does not run forever. Stage-specific show/persist/review cadence belongs to the wrapping stage (sketch, iterate, ...)."""
        """Step 0 - Resolve roots: explore under session.path; write grill-answers under session.docs_dir ({path}/.context/grill-answers.md). If no sprint exists yet, confirm path with the user, suggest a kebab slug from goal/context, open, then continue. Do not invent a divergent root."""
        """Step 1 - Context discovery: call explore_context_files(root=session.path) and any folders referenced in the plan. Prefer-read any active *-sketch.md for this plan so later questions can validate the sketch's thinking."""
        self.explore_context_files()
        """Step 2 - MUST prove-read before asking. Upward context is more general; downward is more specific. Read every relevant context file referenced or implied by the decision - owning `*-segment.md`, module-context, grill-answers, sketches, peer story-context, build-order, and any path the plan or prior answers cite. A consumed handoff is gone — do not hunt archives for current state. Index/overlay mid-epic stubs are never enough for inventory. Call read_context_file (or Read) on each - chunk large files. Grep, titles, memory, or primer-only reads do not count."""
        self.read_context_file()
        """Step 2a - Proof gate: do not proceed to Step 3 until this turn can name the path(s) read and cite concrete terms from them. Missing a referenced file means read it - do not ask yet. Asking from a skim is a defect."""
        """Step 2b - Sketch-validation gate (when a sketch file is in play): ground the next question in what the sketch asserted — ask whether a claimed shape, seam, or rationale is correct, surprising, or missing. Named mistakes from prior sketch review must still constrain options. Do not interview as if the sketch did not exist or as if those mistakes never happened."""
        """Step 3 - Only after Step 2a: ask ONE focused question using the AskQuestion Cursor tool (or structured multiple-choice in chat if that tool is unavailable). Prefer thinking/context questions (why this seam, what to port as-is vs change, ownership) over syntax or naming trivia. Never present bare options: the user must have enough concept context to decide."""
        """Step 3a - Frame the decision first (2-5 sentences): name the branch of the design tree, name the source file(s) just read (and the sketch claim under review when Step 2b applies), and ground the choice in concepts from those files and the active practice material for this session (whatever domain or generator is in play - do not assume a particular practice). Do not invent trade-offs untethered from that evidence. Prove-read grill-answers.md, but do not paste or restate prior grill-answer bodies into the AskQuestion text — cite grill-answers.md by path or heading only if the user needs a pointer. Do not accumulate the interview into the next question."""
        """Step 3b - Present 3-5 options. Put the recommended answer first (label it "(Recommended)"). For each option, give one short rationale tied to those concepts - what choosing it implies for the design under discussion. Always include an "Other / I'll specify" option last. Wait for the answer before proceeding."""
        """Step 3c - Batch similar questions: when several peers share the same frame (e.g. port existing functionality as-is versus change it), ask once with allow_multiple or grouped options instead of a long serial loop. Exhausting one-near-identical-question-at-a-time interviews are a defect."""
        """Step 4 - If a question can be answered by exploring the codebase, explore first instead of asking."""
        """Step 5 - After each resolved insight, call write_grill_answer(root=session.path, ...) immediately. Do not batch writes. Keep entries concise; reference code paths rather than repeating logic."""
        self.write_grill_answer()
        return "Grilling session for: {plan}"
