# @toolset-manifest python -m tools manifest context_tools.base.base_context_tool:BaseContextTool
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# Do not author behavior from this Python source.
# invoke-new: action generate | context.fidelity discovery
# invoke-edit: action satisfy | toolset: context_tools.base.base_context_tool:BaseContextTool
# invoke-check: action validate | toolset: context_tools.base.base_context_tool:BaseContextTool
"""BaseContextTool - composer + artifact lifecycle; shared face for every concrete domain.

Non-primitive kits (workspace bind, CDRs, grill/sketch/iterate) are called
in-method via lazy providers — not `@` chain decorators. `@action` /
`@instruction` / `@tool` stay; those are primitives.
"""

from __future__ import annotations

import inspect
from pathlib import Path
from typing import TypeVar

from grill_context.grill_context import GrillContext
from iterate.iterate import Iterator
from partition_pipeline.partition_pipeline import PartitionPipeline
from primitives.actions.action import _ActionRunner
from primitives.actions.action import action
from primitives.instructions import Instruction
from primitives.instructions import instruction
from record_decisions.record_decisions import RecordDecisions
from repair.repair import Repair
from scanners.scan import Scan
from sessions import WorkspaceSession
from sketch.sketch import Sketcher
from tools.tool import Toolset

T = TypeVar("T", bound=type)


class BaseContextTool(
    PartitionPipeline,
    Repair,
    Scan,
    WorkspaceSession,
    Toolset,
):
    """# Instructions"""

    @property
    def module_dir(self) -> Path:
        return Path(inspect.getfile(type(self))).resolve().parent

    # -- Lazy providers (non-primitive kits; no @ chain decorators) ----------

    def sketcher(self) -> Sketcher:
        kit = getattr(self, "_sketcher_kit", None)
        if kit is None:
            kit = Sketcher(agent_dir=str(self.module_dir))
            self._sketcher_kit = kit
        return kit

    def grill_context(self) -> GrillContext:
        kit = getattr(self, "_grill_kit", None)
        if kit is None:
            kit = GrillContext()
            self._grill_kit = kit
        return kit

    def iterator(self) -> Iterator:
        kit = getattr(self, "_iterator_kit", None)
        if kit is None:
            kit = Iterator()
            self._iterator_kit = kit
        return kit

    def decisions(self) -> RecordDecisions:
        kit = getattr(self, "_decisions_kit", None)
        if kit is None:
            kit = RecordDecisions()
            self._decisions_kit = kit
        return kit

    # -- Instructions --------------------------------------------------------

    @instruction
    def contexts(self) -> Instruction: ...

    @instruction
    def examples(self) -> Instruction: ...

    @instruction
    def templates(self) -> Instruction: ...

    # -- Lifecycle actions (linear bodies) -----------------------------------

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
    def generate(self) -> str:
        self.workspace_session_bind()
        self.decisions().record_decisions_session()
        self.read_context_index()
        self.record_context_root()
        self.contexts
        self.examples
        self.templates
        self.generate_output()
        self.add_generate_header_to_generated()
        return "When done, run validate."

    @action
    def grill(self) -> str:
        """Grill then generate - pure grill loop, then the host generate body."""
        self.workspace_session_bind()
        self.decisions().record_decisions_session()
        self.grill_context().grill_with_context()
        self.generate()
        return "Grill complete; generate instructions applied."

    @action
    def sketch(self) -> str:
        """Sketch then generate - grill + sketch cadence, then the host generate body."""
        self.workspace_session_bind()
        self.decisions().record_decisions_session()
        """Sketch under session.folder; pass agent_dir={{self.module_dir}} to find_template."""
        self.sketcher().sketch_session()
        self.generate()
        return "Sketch complete; generate instructions applied."

    @action
    def iterate(self) -> str:
        """Iterate then generate - grill + formal generate/validate/one-fix ticks."""
        self.workspace_session_bind()
        self.decisions().record_decisions_session()
        self.iterator().iterate_session()
        self.generate()
        return "Iterate complete; generate instructions applied."

    @action
    def validate(self) -> str:
        self.workspace_session_bind()
        self.contexts
        self.scan()
        return "Validation report for artifacts under {session.path}/."

    @action
    def document(self, paths: list[str]) -> str:
        self.workspace_session_bind()
        self.contexts
        self.templates
        self.scan(paths)
        self.generate_output()
        self.add_generate_header_to_generated()
        return "Document existing state under {session.path}/ - violations flagged, none corrected."

    @action
    def satisfy(self) -> str:
        self.workspace_session_bind()
        self.decisions().record_decisions_session()
        self.contexts
        self.templates
        return "When done, run validate on artifacts under {session.path}/."


BaseContextTool._is_context = True  # type: ignore[attr-defined]
BaseContextTool._is_toolset = True  # type: ignore[attr-defined]
_ActionRunner.instance().validate_toolset(BaseContextTool)


def base_context_tool(cls: T) -> T:
    """Merge a domain class with BaseContextTool."""
    if getattr(cls, "_is_context", False):
        return cls
    if issubclass(cls, BaseContextTool):
        raise TypeError(
            f"{cls.__name__} must use @base_context_tool - do not subclass BaseContextTool directly"
        )
    merged = type(
        cls.__name__,
        (cls, BaseContextTool),
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
