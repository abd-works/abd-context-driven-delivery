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
``@action`` / ``@instruction`` / ``@tool`` stay (primitives only). Host
``@tool`` / ``@resource`` wrappers forward to kits so agents can still invoke
them on the domain toolset.
"""

from __future__ import annotations

import inspect
from pathlib import Path
from typing import ClassVar

from grill_context.grill_context import GrillContext
from iterate.iterate import Iterator
from partition.partition import Partition
from primitives.actions.action import _ActionRunner
from primitives.actions.action import AgenticToolset
from primitives.actions.action import action
from primitives.instructions import Instruction
from primitives.instructions import instruction
from record_decisions.record_decisions import RecordDecisions
from eval.session import Repair
from scanners.scan import Scan
from sub_agent.sub_agent import sub_agent
from workspace.session_log import log
from workspace.workspace_session import Session
from sketch.sketch import Sketcher
from tools.tool import resource
from tools.tool import tool


class BaseContextTool(AgenticToolset):
    """# Instructions"""

    SHAPING: ClassVar[str] = "shaping"
    DISCOVERY: ClassVar[str] = "discovery"
    SPEC: ClassVar[str] = "spec"
    ENGINEER: ClassVar[str] = "engineer"

    # Chat/command stage names → canonical stage keys used in ``fidelities``.
    STAGE_ALIASES: ClassVar[dict[str, str]] = {
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
        self.workspace = Session(
            format=self.format,
            path=path,
            session=session,
            workspace=workspace,
            context_index_key=getattr(type(self), "context_index_key", ""),
            default_workspace_folder=getattr(
                type(self), "default_workspace_folder", "."
            ),
        )
        self.scanner = Scan()
        self.sketcher = Sketcher(agent_dir=str(self.module_dir))
        self.grill_context = GrillContext()
        self.iterator = Iterator()
        self.decisions = RecordDecisions()
        self.partitioner = Partition()
        self._bind_eval()
        self.repairer = Repair(session=self.eval, scanner=self.scanner, host=self)

    def _bind_eval(self) -> None:
        """Attach ``self.eval`` when the workspace session has path/folder/name.

        Also binds ``SessionLog`` to this workspace so that every subsequent
        ``@log``-decorated tool or action forwards a ``ToolCall`` to the open
        eval Turn (via ``SessionLog.append → eval.record_tool_call``).
        """
        from eval.session import Session as EvalSession

        name = getattr(self.workspace, "name", None)
        if not name:
            self.eval = None
            if hasattr(self.workspace, "eval"):
                self.workspace.eval = None  # type: ignore[attr-defined]
            if getattr(self, "repairer", None) is not None:
                self.repairer.session = None
            return
        try:
            _ = self.workspace.folder
        except ValueError:
            self.eval = None
            if getattr(self, "repairer", None) is not None:
                self.repairer.session = None
            return
        try:
            self.eval = EvalSession(workspace=self.workspace)
        except Exception:
            self.eval = None
            if getattr(self, "repairer", None) is not None:
                self.repairer.session = None
            return
        self.workspace.eval = self.eval  # type: ignore[attr-defined]
        # Bind SessionLog so @log-decorated runs forward ToolCalls to the eval Turn.
        from workspace.session_log import SessionLog

        SessionLog.instance().bind(self.workspace)
        # Persist context so the Cursor stop hook can call finish_eval_turn.
        self._write_eval_state()
        if getattr(self, "repairer", None) is not None:
            self.repairer.session = self.eval
            self.repairer.host = self

    def _write_eval_state(self) -> None:
        """Write ~/.cursor/cdd_eval_state.json so the stop hook can close the turn."""
        import json as _json
        import pathlib as _pathlib

        state_dir = _pathlib.Path.home() / ".cursor"
        state_dir.mkdir(parents=True, exist_ok=True)
        state = {
            "cdd_repo": str(_pathlib.Path(__file__).resolve().parent.parent.parent),
            "toolset_path": f"{type(self).__module__}:{type(self).__name__}",
            "path": self._raw_path,
            "session": getattr(self.workspace, "name", None),
        }
        try:
            (state_dir / "cdd_eval_state.json").write_text(
                _json.dumps(state, indent=2), encoding="utf-8"
            )
        except Exception:
            pass

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

        Plain Python methods (not @action); each one calls ``_set_fidelity``
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
    def active(self) -> Session:
        """The current workspace session — exposes the session as a host resource."""
        return self.workspace

    @instruction(override=True)
    def session_guidance(self) -> Instruction:
        """Delegate to Session — prose lives in workspace_session.md."""
        return Instruction.ref(self.workspace, "session_guidance")

    @tool
    def read_context_index(self) -> str:
        """read_context_index"""
        return self.workspace.read_context_index()

    @tool
    def record_context_root(self, root: str = "", note: str = "") -> str:
        """record_context_root"""
        return self.workspace.record_context_root(root=root, note=note)

    @tool
    def ensure_session(
        self,
        name: str = "",
        goal: str = "",
        fidelities: str = "",
        contexts: str = "",
        path: str = "",
    ) -> str:
        """ensure_session"""
        result = self.workspace.ensure_session(
            name=name,
            goal=goal,
            fidelities=fidelities,
            contexts=contexts,
            path=path,
        )
        self._bind_eval()
        return result

    @tool
    def create_session(
        self,
        name: str,
        goal: str = "",
        fidelities: str = "",
        contexts: str = "",
        path: str = "",
    ) -> str:
        """create_session"""
        result = self.workspace.create_session(
            name=name,
            goal=goal,
            fidelities=fidelities,
            contexts=contexts,
            path=path,
        )
        self._bind_eval()
        return result

    @tool
    def close_session(self, outcome: str = "", handoff: str = "handoff.md") -> str:
        """close_session"""
        return self.workspace.close_session(outcome=outcome, handoff=handoff)

    # -- Instructions --------------------------------------------------------
    @instruction
    def contexts(self) -> Instruction: ...

    @instruction
    def examples(self) -> Instruction: ...

    @instruction
    def templates(self) -> Instruction: ...

    @instruction
    def scaffold(self) -> Instruction: ...

    # -- Lifecycle actions  -----------------------------------
    @log
    @action
    def partition(
        self,
        context: str,
        mode: str = "one_go",
        out_root: str | None = None,
    ) -> str:
        """partition"""
        self.active
        self.session_guidance
        self.contexts
        self.begin_eval_turn()
        self.partitioner.partition(
            context, mode, out_root, slug=self.domain_slug, scaffold=self.scaffold
        )
        self.finish_eval_turn()
        return (
            "Partition of {{context}} finished (mode {{mode}}); "
            "docs under {session.path}/.context/. "
            "Hard fail if any new chunk fails named-entry completeness."
        )

    @log
    @action
    def grill(self) -> str:
        """Grill then generate - pure grill loop, then the host generate body."""
        self.workspace.open()
        self.decisions.record_decisions_session()
        self.grill_context.grill_with_context()
        self.generate()
        return "Grill complete; generate instructions applied."

    @log
    @action
    def sketch(self) -> str:
        """Sketch then generate - grill + sketch cadence, then the host generate body."""
        self.workspace.open()
        self.decisions.record_decisions_session()
        """Sketch under session.folder; pass agent_dir={{self.module_dir}} to find_template."""
        self.sketcher.sketch_session()
        self.generate()
        return "Sketch complete; generate instructions applied."

    @log
    @action
    def generate(self) -> str:
        self.workspace.open()
        self.begin_eval_turn()
        self.decisions.record_decisions_session()
        self.contexts
        self.examples
        self.templates
        self.generate_output()
        self.add_generate_header_to_generated()
        self.finish_eval_turn()
        return "When done, run validate."

    @action
    def generate_fixes_from_validate(self) -> str:
        self.generate
        self.decisions.record_decisions_session()
        self.examples
        self.templates
        self.generate_output()
        return ""

    @action
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

    @action
    def generate_output(self) -> str:
        """"""
        return ""

    @log
    @action
    def document(self, paths: list[str]) -> str:
        self.workspace.open()
        self.begin_eval_turn()
        self.contexts
        self.templates
        self.scanner.scan(paths)
        self.generate_output()
        self.add_generate_header_to_generated()
        self.finish_eval_turn()
        return "Document existing state under {session.path}/ - violations flagged, none corrected."

    @log
    @action
    def iterate(self) -> str:
        """Iterate then generate - grill + formal generate/validate/one-fix ticks."""
        self.workspace.open()
        self.decisions.record_decisions_session()
        self.iterator.iterate_session()
        self.generate()
        return "Iterate complete; generate instructions applied."

    @log
    @action
    def validate(self) -> str:
        self.workspace.open()
        self.begin_eval_turn()
        self.contexts
        self.scanner.scan()
        self.finish_eval_turn()
        return "Validation report for artifacts under {session.path}/."

    @log
    @tool
    def scan(self, paths: list[str]) -> str:
        """scan"""
        return self.scanner.scan(paths)

    @tool
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

    @log
    @action
    def satisfy(self) -> str:
        self.mode = "tool"
        self.validate()
        self.generate_fixes_from_validate()
        return "When done, run validate on artifacts under {session.path}/."

    @log
    @sub_agent
    @action
    def repair(self, asset: str, violation: str) -> str:
        """repair"""
        self.begin_eval_turn()
        self.scan()
        self.contexts
        self.examples
        self.templates
        self.repairer.repair(asset, violation)
        self.finish_eval_turn()
        return "Repair {{asset}} under {session.path}/ until validate passes."

    @log
    @tool
    def log_mistake(
        self,
        artifact: str,
        rule: str,
        wrong: str,
        original: str,
        when: str = "",
    ) -> str:
        """log_mistake — records through Repair onto session.yaml and session/mistakes/."""
        if self.eval is None:
            raise ValueError("No eval session — open a named session first")
        tool_name = type(self).__name__
        fidelity = getattr(self, "fidelity", "") or ""
        return self.repairer.log_mistake(
            artifact=artifact,
            rule=rule,
            wrong=wrong,
            original=original,
            tool=tool_name,
            fidelity=fidelity,
        )

    @log
    @tool
    def log_correction(self, entry_id: str, improved: str, status: str = "fixed") -> str:
        """log_correction — Correction.apply through Repair; writes repairedAsset beside the Mistake."""
        if self.eval is None:
            raise ValueError("No eval session — open a named session first")
        return self.repairer.log_correction(
            entry_id=entry_id, improved=improved, status=status
        )

    @tool
    def begin_eval_turn(self) -> str:
        """Open the eval Turn. Listed on generate / validate / document / partition / repair / createRule."""
        if self.eval is None:
            return ""
        return self.eval.begin_turn().id

    @tool
    def finish_eval_turn(
        self, prompt: str = "", result: str = "", context: str = ""
    ) -> str:
        """Close the open eval Turn. Listed on generate / validate / document / partition / repair / createRule."""
        if self.eval is None:
            return ""
        closed = self.eval.finish_turn(prompt, result, context)
        return closed.id if closed is not None else ""

    @log
    @action
    def createRule(self, failed: str, wanted: str) -> str:
        """createRule"""
        self.begin_eval_turn()
        self.contexts
        self.examples
        self.templates
        self.finish_eval_turn()
        return (
            "Write a new named rule and matching scanner into this tool. "
            "Then run that rule via scan on the asset and detect a failure "
            "that matches the Mistake."
        )

BaseContextTool._is_context = True  # type: ignore[attr-defined]
BaseContextTool._is_toolset = True  # type: ignore[attr-defined]
_ActionRunner.instance().validate_toolset(BaseContextTool)
