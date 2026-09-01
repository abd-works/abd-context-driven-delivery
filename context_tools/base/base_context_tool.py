# @toolset-manifest python -m tools manifest context_tools.base.base_context_tool:BaseContextTool
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
# Do not author behavior from this Python source.
# invoke-new: action generate | context.fidelity discovery
# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""BaseContextTool - composer + artifact lifecycle; shared face for every concrete domain.

Non-primitive kits are held as plain instance attributes and called through
them (``self.workspace.…``, ``self.scanner.…``, …) — not MI-as-self and not
``@`` chain decorators. Domains subclass this class directly.
``@agent_instructions`` / ``@instruction`` / ``@agent_tool`` stay (primitives only).
Lifecycle generate / validate / document / satisfy / render / createRule live
on the kits under ``context_tools/actions/``.
"""

from __future__ import annotations

import inspect
from pathlib import Path
from typing import ClassVar

from harness.harness_tool import skill
from primitives.actions.action import _ActionRunner
from primitives.actions.action import AgenticToolset
from primitives.actions.action import agent_instructions
from primitives.instructions import Instruction
from primitives.instructions import instruction
from agent.agent import AgentSession, InMemoryRepo, Repo, Workspace
from scan.scan import Scan
from scan.scanner_collection import ScannerCollection
from tools.tool import resource

_REPO_ROOT = Path(__file__).resolve().parents[2]
_WORKSPACE_SESSION_KIT = _REPO_ROOT / "utilities" / "workspace"


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
        self._workspace_path = workspace or path or "."
        self.workspace = self._build_workspace(self._workspace_path)
        self._agent_session: AgentSession | None = None
        self.scanner = Scan.bound_to(self)
        if self._session_name:
            self._open_session(name=self._session_name, path=path or "")

    def _build_workspace(self, path: str) -> Workspace:
        root = Path(path).resolve()
        repo = InMemoryRepo(root, Repo.Worktree(root, "main"))
        workspace = Workspace(path=root, repos=[repo], primary_repo=repo)
        self._load_path_overrides(workspace, root)
        return workspace

    @staticmethod
    def _load_path_overrides(workspace: Workspace, root: Path) -> None:
        index = root / ".context" / "context-index.md"
        if not index.is_file():
            return
        for line in index.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped.startswith("|"):
                continue
            parts = [part.strip() for part in stripped.strip("|").split("|")]
            if len(parts) < 3:
                continue
            tool, fidelity, row_path = parts[0], parts[1], parts[2]
            if tool in {"tool", "---", "*(none)*"} or tool.startswith("---"):
                continue
            if not tool or not fidelity or not row_path:
                continue
            workspace.upsert_path(tool, fidelity, row_path)

    def _resolve_context_root(self, workspace_path: Path) -> Path:
        override = self.workspace.lookup_path("agent", "contextRoot")
        if override is not None:
            return override
        root = workspace_path.resolve()
        context = root / ".context"
        if context.is_dir():
            return context
        return root

    def _open_session(self, name: str = "", path: str = "") -> AgentSession:
        working = Path((path or self._workspace_path or ".").strip()).resolve()
        effective_name = (name or self._session_name or "").strip()
        folder = working / ".agent_sessions" / (effective_name or "default")
        session = self.workspace.open(
            name=effective_name or None,
            context_root=self._resolve_context_root(working),
            open_existing=folder.is_dir(),
        )
        self._agent_session = session
        self._session_name = session.name
        return session

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        cls._is_context = True  # type: ignore[attr-defined]
        cls._is_toolset = True  # type: ignore[attr-defined]
        _ActionRunner.instance().validate_toolset(cls)
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
            if not callable(getattr(cls, action_name, None)):
                continue
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

    def _scanner_collection(self) -> ScannerCollection:
        return ScannerCollection(
            module_dir=self.module_dir,
            root_path=self.module_dir / "scanners",
        )
   
    @property
    @resource
    def active(self) -> AgentSession | None:
        """The current agent session — exposes AgentSession as a host resource."""
        return self._agent_session

    @instruction(override=True)
    def session_guidance(self) -> Instruction:
        """Session layout prose — workspace_session.md."""
        if self._agent_session is None:
            raise ValueError("No current work session — call open first")
        return Instruction(
            "# Session Guidance",
            _WORKSPACE_SESSION_KIT,
            domain_slug="workspace_session",
        )

    # -- Instructions --------------------------------------------------------
    @instruction
    def contexts(self) -> Instruction: ...

    @instruction
    def examples(self) -> Instruction: ...

    @instruction
    def templates(self) -> Instruction: ...

    @instruction
    def scaffold(self) -> Instruction: ...

    # -- Guidance (contexts, examples, templates). Lifecycle lives on Generate / Validate / Document / Satisfy / Render. ---
    @skill
    @agent_instructions
    def guidance(self) -> str:
        """Provide guidance from contexts, examples, and templates."""
        self.contexts
        self.examples
        self.templates
        return ""

    def generate_output(self) -> str:
        """Empty default. Domain tools override; Generate.generate calls this per tool."""
        return ""

    def generate_fixes_from_validate(self) -> str:
        """Empty default. Satisfy calls this per tool after validate."""
        return ""

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


BaseContextTool._is_context = True  # type: ignore[attr-defined]
BaseContextTool._is_toolset = True  # type: ignore[attr-defined]
_ActionRunner.instance().validate_toolset(BaseContextTool)
