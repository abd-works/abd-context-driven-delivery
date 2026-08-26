# @toolset-manifest python -m tools manifest context_tools.base.base_context_tool:BaseContextTool
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# Do not author behavior from this Python source.
# invoke-new: action generate | context.fidelity discovery
# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""BaseContextTool - composer + artifact lifecycle; shared face for every concrete domain.

Non-primitive kits are held as plain instance attributes and called through
them (``self.workspace.…``, ``self.scanner.…``, …) — not MI-as-self and not
``@`` chain decorators. Domains subclass this class directly.
``@agent_instructions`` / ``@instruction`` / ``@agent_tool`` stay (primitives only). Host
``@agent_tool`` / ``@resource`` wrappers forward to kits so agents can still invoke
them on the domain toolset.
"""

from __future__ import annotations

import inspect
from pathlib import Path
from typing import ClassVar

from primitives.actions.action import _ActionRunner
from primitives.actions.action import AgenticToolset
from primitives.actions.action import agent_instructions
from primitives.instructions import Instruction
from primitives.instructions import instruction
from record_decisions.record_decisions import RecordDecisions
from scanners.scan import Scan
from workspace.workspace import Turn, Workspace, WorkSession
from workspace import SessionLog
from tools.tool import resource
from tools.tool import agent_tool


class BaseContextTool(AgenticToolset):
    """# Instructions"""

    SHAPING: ClassVar[str] = "shaping"
    DISCOVERY: ClassVar[str] = "discovery"
    SPEC: ClassVar[str] = "spec"
    ENGINEER: ClassVar[str] = "engineer"

    # Chat/command stage names → canonical stage keys used in ``fidelities``.
    STAGE_ALIASES: ClassVar[dict[str, str]] = {
        "scaffold": SHAPING,
        "discovery": DISCOVERY,
        "specification": SPEC,
        "spec": SPEC,
        "engineering": ENGINEER,
        "engineer": ENGINEER,
    }

    fidelities: ClassVar[dict[str, str] | None] = None
    _fidelity_format_defaults: ClassVar[dict[str, str]] = {}
    supported_formats: ClassVar[frozenset[str]] = frozenset()

    @classmethod
    def resolve_fidelity(cls, fidelity: str) -> str:
        """Map a CDD stage name to this tool's concrete fidelity.

        Accepts stage command names (``discovery`` / ``specification`` /
        ``engineering``), short stage keys (``spec`` / ``engineer``), or an
        already-concrete fidelity. Stage names look up ``cls.fidelities``.
        """
        stage = cls.STAGE_ALIASES.get(fidelity, fidelity)
        mapping = cls.fidelities or {}
        if stage in mapping:
            return mapping[stage]
        return fidelity

    def __init__(
        self,
        format: str | None = None,
        path: str | None = None,
        session: str | None = None,
        workspace: str | None = None,
    ) -> None:
        super().__init__()
        self.format = format
        self._raw_path = path
        self._session_name = session or ""
        root = workspace or path or "."
        self.workspace = Workspace(str(root))
        self.workspace.load()
        self.turn = Turn()
        self.scanner = Scan()
        self.decisions = RecordDecisions()
        if self._session_name:
            self.workspace.open(
                self,
                name=self._session_name,
                path=path or "",
            )

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        cls._is_context = True  # type: ignore[attr-defined]
        cls._is_toolset = True  # type: ignore[attr-defined]
        _ActionRunner.instance().validate_toolset(cls)
        # Auto-generate generate_{f} / validate_{f} / satisfy_{f} whenever
        # a subclass declares a ``fidelities`` class dict.
        if "fidelities" in cls.__dict__ and isinstance(cls.__dict__["fidelities"], dict):
            cls._generate_fidelity_methods()

    @classmethod
    def _generate_fidelity_methods(cls) -> None:
        """Add generate_{f}, validate_{f}, satisfy_{f} for every fidelity in cls.fidelities.

        Plain Python methods (not @agent_instructions); each one calls ``_set_fidelity``
        then delegates to the named lifecycle action.
        """
        fidelity_names: set[str] = set(cls.fidelities.values())  # type: ignore[union-attr]
        for action_name in ("generate", "validate", "satisfy"):
            for fidelity_name in fidelity_names:
                method_name = f"{action_name}_{fidelity_name}"
                if not hasattr(cls, method_name):
                    def _make(act: str, fid: str):
                        def _fidelity_method(self):
                            self._set_fidelity(fid)
                            return getattr(self, act)()
                        _fidelity_method.__name__ = f"{act}_{fid}"
                        _fidelity_method.__qualname__ = f"{cls.__qualname__}.{act}_{fid}"
                        return _fidelity_method
                    setattr(cls, method_name, _make(action_name, fidelity_name))
    
    def _set_fidelity(self, fidelity_name: str) -> None:
        """Update self.fidelity and resolve the matching default format.

        Used by generated fidelity methods (generate_{f}, validate_{f}, …) to
        switch fidelity at runtime without reconstructing the toolset instance.
        Stage names (discovery / specification / engineering) are mapped via
        ``resolve_fidelity`` first. Format is only updated when the resolved
        name appears in the subclass's ``_fidelity_format_defaults``; otherwise
        self.format is left unchanged.
        """
        resolved = type(self).resolve_fidelity(fidelity_name)
        self.fidelity = resolved
        defaults: dict[str, str] = getattr(type(self), "_fidelity_format_defaults", {})
        if resolved in defaults:
            self.format = defaults[resolved]

    # -- workspace  ----------------
    default_workspace_folder: str = "."
    context_index_key: str = ""
    
    @property
    def module_dir(self) -> Path:
        return Path(inspect.getfile(type(self))).resolve().parent
   
    @property
    @resource
    def active(self) -> WorkSession | None:
        """The current work session — exposes currentWorkSession as a host resource."""
        return self.workspace.current_work_session

    @instruction(override=True)
    def session_guidance(self) -> Instruction:
        """Delegate to WorkSession — prose lives in workspace_session.md."""
        current = self.workspace.current_work_session
        if current is None:
            raise ValueError("No current work session — call open first")
        return Instruction.ref(current, "session_guidance")

    # -- Instructions --------------------------------------------------------
    @instruction
    def contexts(self) -> Instruction: ...

    @instruction
    def examples(self) -> Instruction: ...

    @instruction
    def templates(self) -> Instruction: ...

    @instruction
    def scaffold(self) -> Instruction: ...

    # -- Lifecycle actions (core host only; grill/sketch/iterate/partition are kit-owned) ---
    @agent_instructions
    def generate(self) -> str:
        self.workspace.open(self)
        self.turn.open(self, action="generate")
        self.decisions.record_decisions_session()
        self.contexts
        self.examples
        self.templates
        self.generate_output()
        self.add_generate_header_to_generated()
        SessionLog.instance().append(
            toolset=type(self).manifest_path,
            name="generate",
            summary="generate",
            ok=True,
            role="run",
        )
        self.turn.finish_turn()
        return "When done, run validate."

    @agent_instructions
    def generate_fixes_from_validate(self) -> str:
        self.generate
        self.decisions.record_decisions_session()
        self.examples
        self.templates
        self.generate_output()
        return ""

    @agent_instructions
    def add_generate_header_to_generated(self) -> str:
        """Prepend the following block verbatim as the very first lines of the file you are writing - before any imports, before any code."""
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

    @agent_instructions
    def generate_output(self) -> str:
        """"""
        return ""

    @agent_instructions
    def document(self, paths: list[str]) -> str:
        self.workspace.open(self)
        self.turn.open(self, action="document")
        self.contexts
        self.templates
        self.scanner.scan(paths)
        self.generate_output()
        self.add_generate_header_to_generated()
        SessionLog.instance().append(
            toolset=type(self).manifest_path,
            name="document",
            summary="document",
            ok=True,
            role="run",
        )
        self.turn.finish_turn()
        return "Document existing state under {session.path}/ - violations flagged, none corrected."

    @agent_instructions
    def validate(self) -> str:
        self.workspace.open(self)
        self.turn.open(self, action="validate")
        self.contexts
        self.scanner.scan()
        SessionLog.instance().append(
            toolset=type(self).manifest_path,
            name="validate",
            summary="validate",
            ok=True,
            role="run",
        )
        self.turn.finish_turn()
        return "Validation report for artifacts under {session.path}/."

    @agent_tool
    def scan(self, paths: list[str]) -> str:
        """scan"""
        result = self.scanner.scan(paths)
        SessionLog.instance().append(
            toolset=getattr(type(self), "manifest_path", type(self).__name__),
            name="scan",
            summary="scan",
            ok=True,
            role="run",
        )
        return result

    @agent_tool
    def render(self, format: str, content: str = "") -> dict:
        """Render already-generated output into ``format``.

        ``format`` must be one this tool supports (markdown, json, drawio, …).
        ``content`` is the already-generated artifact in the current format
        (``self.format``). Subclasses with channel/transform code override
        this method and convert in-process — do not use a generic rewrite.
        """
        supported = type(self).supported_formats
        if format not in supported:
            raise ValueError(
                f"Unsupported format {format!r}. Choose from: {sorted(supported)}"
            )
        raise ValueError(
            f"{type(self).__name__} has no programmatic renderer for {format!r}"
        )

    @agent_instructions
    def satisfy(self) -> str:
        self.mode = "tool"
        self.validate()
        self.generate_fixes_from_validate()
        SessionLog.instance().append(
            toolset=type(self).manifest_path,
            name="satisfy",
            summary="satisfy",
            ok=True,
            role="run",
        )
        self.turn.finish_turn()
        return "When done, run validate on artifacts under {session.path}/."

    @agent_instructions
    def createRule(self, failed: str, wanted: str) -> str:
        """createRule"""
        self.turn.open(self, action="createRule")
        self.contexts
        self.examples
        self.templates
        SessionLog.instance().append(
            toolset=type(self).manifest_path,
            name="createRule",
            summary="createRule",
            ok=True,
            role="run",
        )
        self.turn.finish_turn()
        return (
            "Write a new named rule and matching scanner into this tool. "
            "Then run that rule via scan on the asset and detect a failure "
            "that matches the Mistake."
        )

    @agent_tool
    def begin_turn(self, action: str = "") -> str:
        """Open a workspace turn on the current work session."""
        if self.workspace.current_work_session is None:
            self.workspace.open(self)
        turn = self.turn.open(self, action=action)
        return turn.id

    @agent_tool
    def finish_turn(
        self, prompt: str = "", result: str = "", context: str = ""
    ) -> str:
        """Finish the open workspace turn; commits on the session branch when dirty."""
        current = self.workspace.current_work_session
        if current is None or current.open_turn is None:
            raise RuntimeError("no open turn — call begin_turn first")
        commit = current.open_turn.finish(
            prompt=prompt, result=result, context=context
        )
        return commit.sha if commit else ""

    @agent_tool
    def record_mistake(
        self,
        artifact: str,
        rule: str,
        wrong: str,
        original: str,
        introducing_commit: str,
        entry_id: str = "",
        tool: str = "",
        fidelity: str = "",
    ) -> str:
        """Annotate a mistake on the introducing commit (git-primary)."""
        import uuid

        current = self.workspace.current_work_session
        if current is None or current.open_turn is None:
            raise RuntimeError("no open turn — call begin_turn first")
        eid = entry_id or uuid.uuid4().hex[:8]
        current.open_turn.record_mistake(
            entry_id=eid,
            artifact=artifact.replace("\\", "/"),
            rule=rule,
            wrong=wrong,
            original=original,
            tool=tool or getattr(type(self), "context_index_key", "") or "bdd",
            fidelity=fidelity or getattr(self, "fidelity", "") or "",
            introducing_commit=introducing_commit,
        )
        return eid

    @agent_tool
    def record_correction(
        self,
        entry_id: str = "",
        improved: str = "",
        how: str = "",
        status: str = "fixed",
        entry_ids: list[str] | None = None,
    ) -> str:
        """Link a correction to mistake entry ids on the open turn."""
        current = self.workspace.current_work_session
        if current is None or current.open_turn is None:
            raise RuntimeError("no open turn — call begin_turn first")
        ids = list(entry_ids or [])
        if entry_id and entry_id not in ids:
            ids.append(entry_id)
        if not ids:
            raise ValueError("record_correction requires entry_id or entry_ids")
        current.open_turn.record_correction(
            entry_ids=ids,
            improved=improved,
            how=how,
            status=status,
        )
        return ids[0]


BaseContextTool._is_context = True  # type: ignore[attr-defined]
BaseContextTool._is_toolset = True  # type: ignore[attr-defined]
_ActionRunner.instance().validate_toolset(BaseContextTool)
