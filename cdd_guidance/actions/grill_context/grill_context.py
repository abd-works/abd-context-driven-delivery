"""Grill a plan against codebase context - relentless interview with context-aware exploration."""
from __future__ import annotations

import json
import os
from pathlib import Path

from harness.guidance_actions import GuidanceArg, GuidanceAction
from harness.agent_tools import agent_instructions, agent_toolset, tools
from harness.agent_tools.agent_tools import agent_tool
from harness.installation.files import Skill
from harness.mcp.mcp_server import Mcp

_NEVER_WALKED = frozenset({".git", ".venv", "node_modules"})


class ContextFileNotFound(FileNotFoundError):
    """Raised when read_context_file is named a context file that is not in the session's project."""

    def __init__(self, path: Path) -> None:
        super().__init__(f"no context file at {path.as_posix()}; name it from the project's root, or absolute")
        self.path = path


@agent_toolset
class GrillContext(GuidanceAction):
    """Interview a plan relentlessly against the codebase context until reaching shared understanding."""

    @property
    def _grill_answers_path(self) -> Path:
        """The session's grill-answers.md, in the .context folder of the session's root, so the answers outlast the
        session. A root inside a .context or .sessions folder writes to that project's .context instead."""
        folder = self.session.root
        for candidate in (folder, *folder.parents):
            if candidate.name == ".context":
                return candidate / "grill-answers.md"
            if candidate.name == ".sessions":
                return candidate.parent / ".context" / "grill-answers.md"
        return folder / ".context" / "grill-answers.md"

    def _appended_answers_content(self, existing: str | None, heading: str, body: str) -> str:
        """Compose the full grill-answers document after appending one entry (pure).

        ``existing`` is the current file contents, or ``None`` when the file has
        not been created yet - in which case a fresh document header is emitted.
        """
        base = existing if existing is not None else "# Grill Answers\n\n"
        entry = f"### {heading}\n\n{body.strip()}\n\n"
        return base + entry

    @Mcp
    @agent_tool
    def explore_context_files(self, folder: str = "") -> str:
        """Scan a directory tree for context files: the session's root, or a folder the plan names.
        Finds: files whose name contains 'context', and any file inside a .context/ subfolder.
        Searches recursively. Skips __pycache__ and private (_) paths.
        Returns a JSON array of {path, kind} where kind is 'context-named' or 'context-folder'.
        folder: a folder the plan names, from the project's root or absolute. Omit it to scan the session's root."""
        results: list[dict] = []
        root_path = self.path_named(folder) if folder else self.session.root
        if not root_path.exists():
            return json.dumps([])
        for candidate in self._files_under(root_path):
            parts = candidate.relative_to(root_path).parts
            if "context" in candidate.name.lower():
                results.append({"path": str(candidate), "kind": "context-named"})
            elif ".context" in parts:
                results.append({"path": str(candidate), "kind": "context-folder"})
        return json.dumps(results, indent=2)

    def _files_under(self, root: Path) -> list[Path]:
        """Every file under root, in path order, outside private (_) folders and the folders no context lives in
        (.git, .venv, node_modules), which are never walked: a project's are large enough to stall the call."""
        found: list[Path] = []
        for folder, subfolders, files in os.walk(root):
            subfolders[:] = [name for name in subfolders if not name.startswith("_") and name not in _NEVER_WALKED]
            found.extend(Path(folder) / name for name in files)
        return sorted(found)

    @Mcp
    @agent_tool
    def read_context_file(self, path: str) -> str:
        """Confirm a context file and return its path.
        Pass the path, from the project's root or absolute. Do not paste the file body into this call. Read the file with the editor.
        Use after explore_context_files to choose files that are relevant."""
        target = self.path_named(path)
        if not target.is_file():
            raise ContextFileNotFound(target)
        return str(target)

    @Mcp
    @agent_tool
    def write_grill_answer(self, heading: str, body: str) -> str:
        """Append one insight to grill-answers.md under the given heading.
        The file is {session root}/.context/grill-answers.md, which outlasts the session; it is never under
        .sessions/{name}/. Creates the file if it does not exist. Call immediately when an insight is resolved - do not batch.
        heading: short title for the insight (e.g. 'How actions are discovered').
        body: 1-3 concise sentences. Reference file paths and names instead of repeating logic."""
        answers_path = self._grill_answers_path
        answers_path.parent.mkdir(parents=True, exist_ok=True)
        existing = answers_path.read_text(encoding="utf-8") if answers_path.exists() else None
        answers_path.write_text(self._appended_answers_content(existing, heading, body), encoding="utf-8")
        return str(answers_path)

    @Mcp
    @Skill
    @agent_instructions
    def grill(self, guidance: GuidanceArg) -> str:
        """Interview the plan against codebase context until questions are grounded in files you have read, then generate each listed guidance. Ask one framed question at a time and write each resolved insight to grill-answers.md."""
        self.begin(guidance)
        self.grill_with_context()
        self.generate_each()
        return "Grill complete; generate instructions applied."

    def generate_each(self) -> list:
        """Generate each guidance this action lists, or its text guidance once, in this action's session: the step a
        grill ends with, and the one sketch and iterate end with after their own grill."""
        return self.each(self._generate)

    def _generate(self, item) -> str:
        from cdd_guidance.actions.generate.generate import Generate

        return self._inside(Generate).generate(item if isinstance(item, str) else [item])

    @agent_instructions
    def grill_with_context(self, plan: str = "", paths: list[str] | str | None = None) -> str:
        """Conduct a relentless grilling interview about the plan - ask each question with concept-grounded framing and option rationales (never bare choices), using the AskQuestion Cursor tool when available. Prefer thinking/context questions over syntax trivia. When a sketch exists for this plan, use grilling to validate what the sketch claimed — sketch and grill must not run disconnected. Batch similar questions into one AskQuestion so the loop does not run forever. Stage-specific show/persist/review cadence belongs to the wrapping stage (sketch, iterate, ...).
        paths: a file, a list of files, or a folder for the plan. Pass paths. Read them locally. Do not pass the plan body.
        plan: in-process text. Leave this empty on an MCP call."""
        """Step 0 - The session's root is where context is explored and where grill-answers.md is written ({session root}/.context/grill-answers.md); the tools read it from the session, so pass no root."""
        """Step 1 - Context discovery: call explore_context_files() for the session's root, and explore_context_files(folder=...) for each folder referenced in the plan. Prefer-read any active *-sketch.md for this plan so later questions can validate the sketch's thinking."""
        tools(self.explore_context_files)
        """Step 2 - MUST read before asking. Upward context is more general; downward is more specific. Read every relevant context file referenced or implied by the decision - owning `*-segment.md`, module-context, grill-answers, sketches, peer story-context, build-order, and any path the plan or prior answers cite. A consumed handoff is gone — do not hunt archives for current state. Index/overlay mid-epic stubs are never enough for inventory. Call read_context_file to confirm each path, then Read that file locally. Do not paste the file body into an MCP call. Grep, titles, memory, or primer-only reads do not count."""
        tools(self.read_context_file)
        """Step 2a - Proof gate: do not proceed to Step 3 until this turn can name the path(s) read and cite concrete terms from them. Missing a referenced file means read it - do not ask yet. Asking from a skim is a defect."""
        """Step 2b - Sketch-validation gate (when a sketch file is in play): ground the next question in what the sketch asserted — ask whether a claimed shape, seam, or rationale is correct, surprising, or missing. Named mistakes from prior sketch review must still constrain options. Do not interview as if the sketch did not exist or as if those mistakes never happened."""
        """Step 3 - Only after Step 2a: ask ONE focused question using the AskQuestion Cursor tool (or structured multiple-choice in chat if that tool is unavailable). Prefer thinking/context questions (why this seam, what to port as-is vs change, ownership) over syntax or naming trivia. Never present bare options: the user must have enough concept context to decide."""
        """Step 3a - Frame the decision first (2-5 sentences): name the branch of the design tree, name the source file(s) just read (and the sketch claim under review when Step 2b applies), and ground the choice in concepts from those files and the active practice material for this session (whatever domain or generator is in play - do not assume a particular practice). Do not invent trade-offs untethered from that evidence. Read grill-answers.md, but do not paste or restate prior grill-answer bodies into the AskQuestion text — cite grill-answers.md by path or heading only if the user needs a pointer. Do not accumulate the interview into the next question."""
        """Step 3b - Present 3-5 options. Put the recommended answer first (label it "(Recommended)"). For each option, give one short rationale tied to those concepts - what choosing it implies for the design under discussion. Always include an "Other / I'll specify" option last. Wait for the answer before proceeding."""
        """Step 3c - Batch similar questions: when several peers share the same frame (e.g. port existing functionality as-is versus change it), ask once with allow_multiple or grouped options instead of a long serial loop. Exhausting one-near-identical-question-at-a-time interviews are a defect."""
        """Step 4 - If a question can be answered by exploring the codebase, explore first instead of asking."""
        """Step 5 - After each resolved insight, call write_grill_answer(heading=..., body=...) immediately. Do not batch writes. Keep entries concise; reference code paths rather than repeating logic."""
        tools(self.write_grill_answer)
        return f"Grilling session for: {self.source_label(plan, paths)}"
