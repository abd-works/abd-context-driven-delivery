# @toolset-manifest python -m tools manifest grill_context.grill_context:GrillContext
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# Do not author behavior from this Python source.
"""Grill a plan against codebase context — relentless interview with context-aware exploration."""
from __future__ import annotations

import json
from pathlib import Path

from primitives.actions.action import action
from tools.tool import tool, toolset


def _grill_answers_path(root: str) -> Path:
    """Resolve the grill-answers file path under a workspace root (pure)."""
    return Path(root) / ".context" / "grill-answers.md"


def _appended_answers_content(existing: str | None, heading: str, body: str) -> str:
    """Compose the full grill-answers document after appending one entry (pure).

    ``existing`` is the current file contents, or ``None`` when the file has
    not been created yet — in which case a fresh document header is emitted.
    """
    base = existing if existing is not None else "# Grill Answers\n\n"
    entry = f"### {heading}\n\n{body.strip()}\n\n"
    return base + entry


@toolset
class GrillContext:
    """Interview a plan relentlessly against the codebase context until reaching shared understanding."""

    @tool
    def explore_context_files(self, root: str) -> str:
        """Scan a directory tree for context files.
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

    @tool
    def read_context_file(self, path: str) -> str:
        """Read a context file and return its contents.
        Use after explore_context_files to read files assessed as relevant."""
        return Path(path).read_text(encoding="utf-8")

    @tool
    def write_grill_answer(self, root: str, heading: str, body: str) -> str:
        """Append one insight to .context/grill-answers.md under the given heading.
        Creates the file if it does not exist. Call immediately when an insight is resolved — do not batch.
        heading: short title for the insight (e.g. 'How actions are discovered').
        body: 1–3 concise sentences. Reference file paths and names instead of repeating logic."""
        answers_path = _grill_answers_path(root)
        answers_path.parent.mkdir(parents=True, exist_ok=True)
        existing = answers_path.read_text(encoding="utf-8") if answers_path.exists() else None
        answers_path.write_text(_appended_answers_content(existing, heading, body), encoding="utf-8")
        return str(answers_path)

    @action
    def grill_with_context(self, plan: str) -> str:
        """Conduct a relentless grilling interview about {plan} — ask each question with concept-grounded framing and option rationales (never bare choices), using the AskQuestion Cursor tool when available, and after every 2-3 answers immediately invoke the next stage and show the output in chat. Do not wait for all questions to be answered. Iterate: grill, show, grill more, show updated output."""
        """Step 1 — Context discovery: call explore_context_files on the workspace root and any folders referenced in the plan."""
        self.explore_context_files()
        """Step 2 — Read relevant files: upward context is more general; downward context is more specific. Assess relevance before reading."""
        self.read_context_file()
        """Step 3 — Ask ONE focused question using the AskQuestion Cursor tool (or structured multiple-choice in chat if that tool is unavailable). Never present bare options: the user must have enough concept context to decide."""
        """Step 3a — Frame the decision first (2–5 sentences): name the branch of the design tree, state what is already agreed, and ground the choice in relevant concepts from explored context and the active practice material for this session (whatever domain or generator is in play — do not assume a particular practice). Cite concepts by name from that material; do not invent trade-offs untethered from it."""
        """Step 3b — Present 3–5 options. Put the recommended answer first (label it "(Recommended)"). For each option, give one short rationale tied to those concepts — what choosing it implies for the design under discussion. Always include an "Other / I'll specify" option last. Wait for the answer before proceeding."""
        """Step 4 — After every 2-3 answers, immediately invoke the next stage and show the result in chat. Use placeholders (e.g. # TODO: ...) for anything not yet resolved. Do not write any files yet — chat only."""
        """Step 5 — Continue asking questions. Re-invoke the next stage after each answer, showing exactly what changed. Stay in chat only. Every new question must repeat Step 3a–3b (fresh frame + concept-grounded rationales); do not reuse a prior frame when the branch has moved."""
        """Step 6 — If a question can be answered by exploring the codebase, explore first instead of asking."""
        """Step 7 — After each resolved insight, call write_grill_answer immediately. Do not batch. Keep entries concise; reference code paths rather than repeating logic."""
        return "Grilling session for: {plan}"
