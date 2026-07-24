# @toolset-manifest python -m tools manifest context_tools.base.context:Context
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# Do not author behavior from this Python source.
"""Build or patch Context domains — scaffold @context toolsets (class Context + @context)."""

from __future__ import annotations

import inspect
from datetime import date
from pathlib import Path
from typing import TypeVar
from primitives.actions.action import _ActionRunner, action
from primitives.instructions import Instruction
from primitives.instructions import instruction
from grill_context import grill_with_context
from iterate import iterate
from record_decisions import record_decisions
from scanners import ScannerCollection
from sketch import sketch
from tools.tool import Toolset, resource, tool
from sessions import Session, SessionLog, log
from context_tools.base.segment_named_entry_completeness import (
    check_named_entries,
    format_report,
    has_expected_entries_marker,
    parse_expected_names,
)

T = TypeVar("T", bound=type)


def _bind_session_log(session: Session) -> None:
    """Point SessionLog at this bout so events land under session.log."""
    if session.name:
        SessionLog.instance().bind(session)


class Context(Toolset):
    """§ Instructions"""

    def __init__(
        self,
        format: str | None = None,
        path: str | None = None,
        session: str | None = None,
    ) -> None:
        super().__init__()
        self.format = format
        working = path if path is not None else "."
        if session:
            self._session = Session.load(working, session)
        else:
            self._session = Session(path=working)
        _bind_session_log(self._session)

    @property
    @resource
    def session(self) -> Session:
        """Current work bout (object).

        - ``session.path`` — working area for durable artifacts
          (partition index → ``{path}/.context/``;
          partitioned chunks + module-local docs → ``{path}/{module}/.context/``;
          generated modules → ``{path}/{module}/``)
        - ``session.name`` / ``session.folder`` — named bout under
          ``{path}/.context/sessions/{name}/`` for process artifacts
          (session.md, grill-answers, engagement sketches, handoff)

        Constructor: ``context.path`` (working area, default ``"."``) and
        ``context.session`` (bout slug). When grill/sketch/handoff needs a bout
        and none is set: confirm ``path`` with the user, suggest a kebab slug
        from goal/context, user confirms, then ``create_session``.
        """
        return self._session

    @tool
    def create_session(
        self,
        name: str,
        goal: str = "",
        fidelities: str = "",
        contexts: str = "",
    ) -> str:
        """Create ``{session.path}/.context/sessions/{name}/session.md`` (Start section).
        Confirm working path and slug with the user first. AI may suggest the slug from
        goal/context; user confirms. Returns the session.md path."""
        self._session = Session(
            path=self._session.path,
            name=name,
            goal=goal,
            fidelities=fidelities,
            contexts=contexts,
        )
        md = self._session.ensure_started(
            goal=goal, fidelities=fidelities, contexts=contexts
        )
        _bind_session_log(self._session)
        return str(md.resolve())

    @tool
    def close_session(self, outcome: str = "", handoff: str = "handoff.md") -> str:
        """Write the End section on session.md (ended, outcome, handoff link).
        Call after handoff is written per the handoff skill. Returns session.md path."""
        md = self._session.close(outcome=outcome, handoff=handoff)
        return str(md.resolve())

    @tool
    def write_to_fix(
        self,
        artifact: str,
        rule: str,
        wrong: str,
        original: str,
        improved: str,
        status: str = "fixed",
        when: str = "",
    ) -> str:
        """Append one entry to ``{session.folder}/to-fix.log`` (creates header if missing).
        Fields: artifact, rule, wrong (one line), original, improved, status, optional when.
        Returns the log path. Prefer calling via action log_fix after the correction."""
        folder = self._session.folder
        path = folder / "to-fix.log"
        folder.mkdir(parents=True, exist_ok=True)
        if not path.is_file():
            bout = self._session.name or "session"
            path.write_text(
                f"# to-fix.log — {bout} bout\n"
                "# Log omissions/errors here. Each entry:\n"
                "#   when, artifact, rule, wrong (one line), original, improved\n"
                '# User phrase "to fix" = failed to do it right; '
                "fix immediately and append an entry.\n\n",
                encoding="utf-8",
            )

        def block(text: str) -> str:
            return "\n".join(
                f"  {line}"
                for line in text.replace("\r\n", "\n").rstrip("\n").split("\n")
            )

        entry = (
            "---\n"
            f"when: {when.strip() or date.today().isoformat()}\n"
            f"artifact: {artifact.strip()}\n"
            f"rule: {rule.strip()}\n"
            f"wrong: {' '.join(wrong.strip().splitlines())}\n"
            "original: |\n"
            f"{block(original)}\n"
            "improved: |\n"
            f"{block(improved)}\n"
            f"status: {status.strip() or 'fixed'}\n"
            "---\n"
        )
        existing = path.read_text(encoding="utf-8")
        sep = "" if existing.endswith("\n\n") else "\n" if existing.endswith("\n") else "\n\n"
        path.write_text(existing + sep + entry, encoding="utf-8")
        return str(path.resolve())

    @action
    def log_fix(
        self,
        artifact: str = "",
        rule: str = "",
        wrong: str = "",
        original: str = "",
        improved: str = "",
        status: str = "fixed",
    ) -> str:
        """base-context/log_fix"""
        self.session
        self.write_to_fix()
        return (
            "After correcting the failure, entry is in {session.folder}/to-fix.log "
            "({{artifact}} / {{rule}})."
        )

    @tool
    def verify_segment_completeness(
        self,
        segment_path: str,
        expected_names: str = "",
        min_body_chars: int = 120,
    ) -> str:
        """Run named-entry completeness on a ``*-segment.md`` chunk.

        Span length alone is a false PASS. Pass ``expected_names`` (newline/comma
        list) or put ``<!-- expected-entries ... -->`` in the segment. Completeness
        FAIL = hard-fail — repair before story inventory. Call after segmenting.
        """
        path = Path(segment_path)
        if not path.is_file():
            return f"completeness: FAIL\nerror: segment not found: {segment_path}\n"
        text = path.read_text(encoding="utf-8", errors="replace")
        if expected_names.strip():
            names = parse_expected_names(expected_names)
        elif has_expected_entries_marker(text):
            names = parse_expected_names(text)
        else:
            return (
                f"segment: {path}\n"
                "completeness: FAIL\n"
                "error: no expected_names argument and no "
                "<!-- expected-entries --> marker in segment\n"
            )
        results = check_named_entries(
            text, names, min_body_chars=int(min_body_chars)
        )
        return format_report(
            str(path.resolve()), results, min_body_chars=int(min_body_chars)
        )

    @property
    def module_dir(self) -> Path:
        return Path(inspect.getfile(type(self))).resolve().parent

    @instruction
    def contexts(self) -> Instruction: ...

    @instruction
    def generate_instructions(self) -> Instruction: ...

    @instruction
    def document_instructions(self) -> Instruction: ...

    @instruction
    def examples(self) -> Instruction: ...

    @instruction
    def templates(self) -> Instruction: ...

    @instruction(override=True)
    def partition_guidance(self) -> str:
        """Domain partition.md when present; otherwise base default guidance."""
        path = self.module_dir / "partition.md"
        if path.is_file():
            return Instruction.ref(self, "partition").expand()
        return (
            "Determine top-level structure based on user suggestion, available context, "
            "skill-provided material, and what is evident in the source. "
            "Keep it thin — only enough to ground partitions; TODOs are fine."
        )

    @action
    def add_generate_header_to_generated(self) -> str:
        """Prepend the following block verbatim as the very first lines of the file you are writing — before any imports, before any code."""
        cls = type(self)
        return (
            '"""\n'
            f"# @toolset-manifest {cls.manifest_command}\n"
            "# Agent reading this file: run line 1 manifest, then python -m tools run -. "
            "Follow response.instructions only.\n"
            f"# invoke-edit: action satisfy | toolset: {cls.manifest_path}\n"
            f"# invoke-check: action validate | toolset: {cls.manifest_path}\n"
            '"""\n'
        )

    @action
    def generate_output(self) -> str:
        """"""
        return ""

    def _scanner_collection(self) -> ScannerCollection:
        return ScannerCollection()

    @record_decisions
    @log
    @action
    def generate(self) -> str:
        """base-context/generate"""
        self.session
        self.contexts
        self.generate_instructions
        self.examples
        self.templates
        self.generate_output()
        self.add_generate_header_to_generated()
        return "When done, run validate."

    @record_decisions
    @grill_with_context
    @action
    def grill(self) -> str:
        """Grill then generate — pure grill loop, then the host generate body."""
        self.generate()
        return "Grill complete; generate instructions applied."

    @record_decisions
    @sketch
    @action
    def sketch(self) -> str:
        """Sketch then generate — grill + sketch cadence, then the host generate body."""
        self.generate()
        return "Sketch complete; generate instructions applied."

    @record_decisions
    @iterate
    @action
    def iterate(self) -> str:
        """Iterate then generate — grill + formal generate/validate/one-fix ticks."""
        self.generate()
        return "Iterate complete; generate instructions applied."

    @action
    def validate(self) -> str:
        """base-context/validate"""
        self.session
        self.contexts
        self.scan()
        return "Validation report for artifacts under {session.path}/."

    @action
    def document(self, paths: list[str]) -> str:
        """base-context/document"""
        self.session
        self.contexts
        self.document_instructions
        self.templates
        self.scan(paths)
        self.generate_output()
        self.add_generate_header_to_generated()
        return "Document existing state under {session.path}/ — violations flagged, none corrected."

    @record_decisions
    @action
    def satisfy(self) -> str:
        """base-context/satisfy"""
        self.session
        self.contexts
        self.templates
        return "When done, run validate on artifacts under {session.path}/."

    @action
    def repair(self, asset: str, violation: str) -> str:
        """base-context/repair"""
        self.session
        self.scan()
        self.contexts
        self.examples
        self.templates
        self.validate()
        return "Repair {{asset}} under {session.path}/ until validate passes."

    @action
    def index(self, context: str, out_root: str | None = None) -> str:
        """base-context/index"""
        self.session
        self.contexts
        self.partition_guidance
        return (
            "Index written for {{context}} under {session.path}/.context/ "
            "(out_root overrides session.path when set)."
        )

    @action
    def segment(self, out_root: str | None = None) -> str:
        """base-context/segment"""
        self.session
        self.contexts
        self.partition_guidance
        self.verify_segment_completeness()
        return (
            "Verbatim source chunks written under {session.path}/{module}/.context/ "
            "from {subject}-index.md (same tree as generated modules). "
            "Named-entry completeness verified (length-only is a false PASS)."
        )

    @action
    def partition(
        self,
        context: str,
        mode: str = "one_go",
        out_root: str | None = None,
    ) -> str:
        """base-context/partition"""
        self.session
        self.contexts
        self.partition_guidance
        self.index(context, out_root)
        self.segment(out_root)
        self.verify_segment_completeness()
        return (
            "Partition of {{context}} finished (mode {{mode}}); "
            "docs under {session.path}/.context/. "
            "Hard fail if any new chunk fails named-entry completeness."
        )

    @tool
    def scan(self, paths: list[str]) -> str:
        """base-context/scan"""
        files = [Path(path) for path in paths]
        report = self._scanner_collection().run(Path.cwd(), files)
        return str(report.to_dict())


Context._is_context = True  # type: ignore[attr-defined]
Context._is_toolset = True  # type: ignore[attr-defined]
_ActionRunner.instance().validate_toolset(Context)


def context(cls: T) -> T:
    """Merge a domain class with Context."""
    if getattr(cls, "_is_context", False):
        return cls
    if issubclass(cls, Context):
        raise TypeError(
            f"{cls.__name__} must use @context — do not subclass Context directly"
        )
    merged = type(
        cls.__name__,
        (cls, Context),
        {
            attribute_name: attribute_value
            for attribute_name, attribute_value in vars(cls).items()
            if attribute_name not in ("__dict__", "__weakref__")
        },
    )
    merged.__doc__ = cls.__doc__
    merged.__module__ = cls.__module__
    merged.__qualname__ = cls.__qualname__
    merged._is_context = True  # type: ignore[attr-defined]
    merged._is_toolset = True  # type: ignore[attr-defined]
    _ActionRunner.instance().validate_toolset(merged)
    return merged
