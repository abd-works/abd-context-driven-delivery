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
from repair.repair import Repair
from scanners.scan import Scan
from sub_agent.sub_agent import sub_agent
from workspace.session_log import log
from workspace.workspace_session import Session
from sketch.sketch import Sketcher
from tools.tool import resource
from tools.tool import tool


class BaseContextTool(AgenticToolset):
    """# Instructions"""

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
        self.repairer = Repair(workspace=self.workspace, scanner=self.scanner)


    #  -- Stage / Fidelity ----------------
    SHAPING:   ClassVar[str] = "shaping"
    DISCOVERY: ClassVar[str] = "discovery"
    SPEC:      ClassVar[str] = "spec"
    ENGINEER:  ClassVar[str] = "engineer"
 
    fidelities: ClassVar[dict[str, str] | None] = None
    _fidelity_format_defaults: ClassVar[dict[str, str]] = {}

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
        Format is only updated when fidelity_name appears in the subclass's
        ``_fidelity_format_defaults`` class dict; otherwise self.format is
        left unchanged.
        """
        self.fidelity = fidelity_name
        defaults: dict[str, str] = getattr(type(self), "_fidelity_format_defaults", {})
        if fidelity_name in defaults:
            self.format = defaults[fidelity_name]

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
        return self.workspace.ensure_session(
            name=name,
            goal=goal,
            fidelities=fidelities,
            contexts=contexts,
            path=path,
        )

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
        return self.workspace.create_session(
            name=name,
            goal=goal,
            fidelities=fidelities,
            contexts=contexts,
            path=path,
        )

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
        self.partitioner.partition(
            context, mode, out_root, slug=self.domain_slug, scaffold=self.scaffold
        )
        return (
            "Partition of {{context}} finished (mode {{mode}}); "
            "docs under {session.path}/.context/. "
            "Hard fail if any new chunk fails named-entry completeness."
        )

    @action
    def grill(self) -> str:
        """Grill then generate - pure grill loop, then the host generate body."""
        self.workspace.open()
        self.decisions.record_decisions_session()
        self.grill_context.grill_with_context()
        self.generate()
        return "Grill complete; generate instructions applied."

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
        self.decisions.record_decisions_session()
        self.contexts
        self.examples
        self.templates
        self.generate_output()
        self.add_generate_header_to_generated()
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

    @action
    def document(self, paths: list[str]) -> str:
        self.workspace.open()
        self.contexts
        self.templates
        self.scanner.scan(paths)
        self.generate_output()
        self.add_generate_header_to_generated()
        return "Document existing state under {session.path}/ - violations flagged, none corrected."

    @action
    def iterate(self) -> str:
        """Iterate then generate - grill + formal generate/validate/one-fix ticks."""
        self.workspace.open()
        self.decisions.record_decisions_session()
        self.iterator.iterate_session()
        self.generate()
        return "Iterate complete; generate instructions applied."

    @action
    def validate(self) -> str:
        self.workspace.open()
        self.contexts
        self.scanner.scan()
        return "Validation report for artifacts under {session.path}/."

    @tool
    def scan(self, paths: list[str]) -> str:
        """scan"""
        return self.scanner.scan(paths)

    @action
    def satisfy(self) -> str:
        self.mode = "tool"
        self.validate()
        self.generate_fixes_from_validate()
        return "When done, run validate on artifacts under {session.path}/."
    
    @sub_agent
    @action
    def repair(self, asset: str, violation: str) -> str:
        """repair"""
        self.scan()
        self.contexts
        self.examples
        self.templates
        self.repairer.repair(asset, violation)
        return "Repair {{asset}} under {session.path}/ until validate passes."
    
    @tool
    def log_mistake(
        self,
        artifact: str,
        rule: str,
        wrong: str,
        original: str,
        when: str = "",
    ) -> str:
        """log_mistake"""
        return self.repairer.log_mistake(
            artifact=artifact,
            rule=rule,
            wrong=wrong,
            original=original,
            when=when,
            tool=type(self).__name__,
            fidelity=getattr(self, "fidelity", "") or "",
        )

    @tool
    def log_correction(self, entry_id: str, improved: str, status: str = "fixed") -> str:
        """log_correction"""
        return self.repairer.log_correction(entry_id, improved, status)

    @action
    def improve(self) -> str:
        """improve"""
        self.contexts
        self.examples
        self.templates
        self.repairer.improve()
        return "Read the roadmap above for log_mistake -> log_correction -> repair -> regression -> archive."

    @sub_agent
    @tool
    def verify_regression(self, examples_root: str) -> str:
        """verify_regression"""
        return self.repairer.verify_regression(examples_root)

    @sub_agent
    @tool
    def archive_mistakes(self, repo_root: str) -> str:
        """archive_mistakes"""
        return self.repairer.archive_mistakes(repo_root)

BaseContextTool._is_context = True  # type: ignore[attr-defined]
BaseContextTool._is_toolset = True  # type: ignore[attr-defined]
_ActionRunner.instance().validate_toolset(BaseContextTool)
