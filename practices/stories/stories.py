"""Stories generator - multi-fidelity story maps, scenarios, and acceptance tests."""

from __future__ import annotations

import importlib
import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

from practices.stages import DISCOVERY, ENGINEER, SHAPING, SPEC, resolve_stage_fidelity
from practices.workspace_bind import init_practice_guidance
from harness.agent_tools.agent_tools import agent_instructions, agent_toolset
from harness.guidance.guidance import PracticeGuidance
from installation.harness_files.harness_files import skill
from installation.mcp.mcp_server import mcp
from agent_tools.agent_tools import agent_tool  # noqa: F401

if TYPE_CHECKING:
    from practices.clean_engineering.clean_engineering import CleanEngineering
    from tools.diagnose.diagnose import Diagnose

_FIDELITY_FORMAT_DEFAULTS = {
    "scaffold": "markdown",
    "story_map": "markdown",
    "scenarios": "typescript",
    "acceptance_tests": "typescript",
}

# Adapter class path per format - peer channels, same CLI surface.
_CHANNELS: dict[str, tuple[str, str]] = {
    "markdown": ("stories.document.markdown.nodes", "MarkdownStoryMap"),
    "json": ("stories.document.json.nodes", "JsonStoryMap"),
    "drawio": ("stories.diagram.drawio.nodes", "DrawIOStoryMap"),
    "miro": ("stories.diagram.miro.nodes", "MiroStoryMap"),
    "python": ("stories.code.python.python_story_map", "PythonStoryMap"),
    "typescript": ("stories.code.typescript.typescript_story_map", "TypeScriptStoryMap"),
    "java": ("stories.code.java.java_story_map", "JavaStoryMap"),
    "javascript": ("stories.code.javascript.javascript_story_map", "JavaScriptStoryMap"),
}

_SUPPORTED_FORMATS = frozenset(_CHANNELS)
_CODE_FORMATS = frozenset({"python", "typescript", "java", "javascript"})


def _load_channel_class(format_name: str) -> type:
    if format_name not in _CHANNELS:
        raise ValueError(
            f"Unsupported format {format_name!r}. Choose from: {sorted(_CHANNELS)}"
        )
    module_path, attr = _CHANNELS[format_name]
    return getattr(importlib.import_module(module_path), attr)


def _normalize_input(format_name: str, content: Any) -> Any:
    if format_name in _CODE_FORMATS:
        if isinstance(content, dict):
            return content
        if isinstance(content, str):
            return json.loads(content)
        raise TypeError(f"{format_name} transform expects a path->content dict or JSON object")
    if not isinstance(content, str):
        raise TypeError(f"{format_name} transform expects a string")
    return content


def _root_glob_to_prefix(root_glob: str) -> str:
    text = (root_glob or "./").strip().replace("\\", "/")
    if text.endswith("/*"):
        text = text[:-2]
    if text.endswith("/"):
        text = text[:-1]
    if text in ("", ".", "./"):
        return ""
    if text.startswith("./"):
        text = text[2:]
    return text.strip("/")


@agent_toolset
class Stories(PracticeGuidance):
    """# Instructions"""

    domain_slug = "stories"
    default_workspace_folder: str = "tests"
    context_index_key: str = "stories"
    _fidelity_format_defaults = _FIDELITY_FORMAT_DEFAULTS
    supported_formats = _SUPPORTED_FORMATS

    STAGE_TO_FIDELITY = {
        SHAPING: "scaffold",
        DISCOVERY: "story_map",
        SPEC: "scenarios",
        ENGINEER: "acceptance_tests",
    }

    @classmethod
    def resolve_fidelity(cls, fidelity: str) -> str:
        return resolve_stage_fidelity(fidelity, cls.STAGE_TO_FIDELITY)

    def __init__(
        self,
        fidelity: str = "story_map",
        format: str | None = None,
        path: str | None = None,
        session: str | None = None,
        workspace: str | None = None,
    ) -> None:
        fidelity = type(self).resolve_fidelity(fidelity)
        if fidelity not in _FIDELITY_FORMAT_DEFAULTS:
            raise ValueError(
                f"Unsupported fidelity {fidelity!r}. Choose from: {sorted(_FIDELITY_FORMAT_DEFAULTS)}"
            )
        resolved_format = format if format is not None else _FIDELITY_FORMAT_DEFAULTS[fidelity]
        if resolved_format not in _SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported format {resolved_format!r}. Choose from: {sorted(_SUPPORTED_FORMATS)}"
            )
        init_practice_guidance(
            self,
            format=resolved_format,
            path=path,
            session=session,
            workspace=workspace,
            fidelity=fidelity,
            stage_to_fidelity=self.STAGE_TO_FIDELITY,
        )

    def diagnostic(self) -> "Diagnose":
        """Diagnose companion — common six-phase loop as a tool (not inlined)."""
        # lazy import: keeps diagnose optional at module load
        from tools.diagnose.diagnose import Diagnose

        return Diagnose()

    def ce(self) -> "CleanEngineering":
        """CleanEngineering companion at code fidelity — used at acceptance_tests fidelity
        to generate or update matching production class implementations after writing specs.
        Invoke as a tool (not inlined into stories guidance). Passes this Stories instance's
        own format through to CleanEngineering when CE recognizes it as a code channel
        (typescript, java, javascript, python) - e.g. format="typescript" here means the
        companion writes TypeScript, not CE's unrelated Python default."""
        from practices.clean_engineering.clean_engineering import CleanEngineering

        ce_format = self.format if self.format in _CODE_FORMATS else None
        instance = CleanEngineering(
            fidelity="code",
            format=ce_format,
            path=self.path,
            session=(
                self.workspace.current_work_session.name
                if self.workspace.current_work_session
                else ""
            ),
            workspace=self.workspace.path,
        )
        instance.mode = "tool"
        return instance

    def _resolve_tests_root(self) -> str | None:
        """Workspace-relative prefix for code renders. ``None`` → default ``tests``."""
        from tools.workspace.context_index import ContextIndex

        workspace_path = Path(self.workspace.path).resolve()
        key = getattr(type(self), "context_index_key", "") or ""
        indexed = ContextIndex.lookup_root(workspace_path, key) if key else None
        if indexed:
            return _root_glob_to_prefix(indexed)

        deploy = self._deploy_folder_prefix()
        if deploy is not None:
            return deploy
        return None

    def _deploy_folder_prefix(self) -> str | None:
        """Infer colocated output root from ``path`` when it targets story artifacts."""
        if not self.path:
            return None
        workspace = Path(self.workspace.path).resolve()
        raw = Path(self.path)
        if not raw.is_absolute():
            raw = (workspace / raw).resolve()

        deploy: Path | None = None
        if raw.is_file() and raw.name in ("story-scenarios.md", "story-map.md"):
            deploy = raw.parent
        elif raw.is_dir():
            if (raw / "story-scenarios.md").is_file():
                deploy = raw
            elif (raw / "story-map.md").is_file():
                deploy = raw

        if deploy is None:
            return None
        try:
            rel = deploy.resolve().relative_to(workspace)
        except ValueError:
            return None
        rel_str = rel.as_posix()
        return "" if rel_str in (".", "") else rel_str

    def _make_target(self, target_format: str):
        target_cls = _load_channel_class(target_format)
        if target_format in _CODE_FORMATS:
            return target_cls(tests_root=self._resolve_tests_root())
        return target_cls()

    @property
    @mcp
    @skill
    @agent_instructions
    def instructions(self) -> str:
        """Provide guidance for creating story maps, scenarios, and acceptance tests.
        At scaffold fidelity: write epic, sub-epic, and story names only.
        At story_map fidelity: write the story map and thin-slice only.
        At scenarios fidelity: write main-flow scenarios (single or multiple per story) with optional variations; fixtures live in examples/ and givens.ts at the lowest shared epic/sub-epic/story folder beside story-scenarios.md (use tests/ only when that is the chosen output root).
        At acceptance_tests fidelity: write tests/{epic}/{sub-epic}/{story}.{tier}.ts (one GWT file per story per seam, no story folder). After writing each acceptance test, use Clean Engineering at code fidelity to ensure the test is properly written, then to write the underlying code sufficient to make the test pass, then run the code and refactor according to Clean Engineering rules.
        If the same acceptance scenario is still RED after 2 consecutive fix attempts — stop guessing. Call diagnostic().diagnose() before a third fix (tier wiring, stale Story constant, vocabulary drift, or transform that fixed the map while the leaf still fails)."""
        return super().instructions

    @property
    @agent_instructions
    def guidance(self) -> str:
        """Expand this practice's Guidance section, then code-fidelity Clean Engineering at acceptance_tests."""
        text = super().guidance
        if self.fidelity != "acceptance_tests":
            return text
        self.ce().guidance
        return (
            "After writing each acceptance test, use Clean Engineering at code fidelity "
            "to ensure the test is properly written, then to write the underlying code "
            "sufficient to make the test pass. Run the code, then refactor according to "
            "Clean Engineering rules."
        )

    @mcp
    @agent_tool
    def transform(self, source_format: str, target_format: str, content: str) -> dict:
        """Parse content from source_format into the canonical StoryMap, then render into target_format.
        All formatters are peer channels. Sideways format move at the same fidelity.
        At acceptance_tests fidelity: after transforming story artifacts, call ce().transform() or call guidance on the CE companion and pass that companion to this action as a separate tools run."""
        source_cls = _load_channel_class(source_format)
        source = source_cls()
        target = self._make_target(target_format)
        parsed_input = _normalize_input(source_format, content)
        canonical = source.parse(parsed_input)
        if source_format == "markdown" and target_format in _CODE_FORMATS:
            from practices.stories.document.markdown.nodes import MarkdownScenario
            scenarios = MarkdownScenario.parse_text(content, self.path or "story-scenarios.md")
            canonical.attach_scenarios(scenarios)
        rendered = target.render(canonical)
        return {"format": target_format, "content": rendered}

    @mcp
    @agent_tool
    def render(self, format: str, content: str = "") -> dict:
        """Render already-generated story output into ``format`` via channel parse/render."""
        source = None
        if not content:
            if self.path:
                p = Path(self.path)
                if p.is_file():
                    content = p.read_text(encoding="utf-8")
                    if p.suffix == ".md":
                        source = "markdown"
                    elif p.suffix == ".json":
                        source = "json"
                    elif p.suffix in (".ts", ".tsx"):
                        source = "typescript"
                    elif p.suffix == ".js":
                        source = "javascript"
                elif p.is_dir():
                    for name in ("story-scenarios.md", "story-map.md"):
                        if (p / name).exists():
                            content = (p / name).read_text(encoding="utf-8")
                            source = "markdown"
                            break
            if not content:
                raise ValueError("content is required — pass the already-generated artifact or a valid path")
        if not source:
            source = self.format or "markdown"
        return self.transform(source, format, content)

    @mcp
    @agent_tool
    def render_chunks(self, content: str, chunk_size: int = 80) -> dict:
        """Render story map into Miro SVG chunks for incremental board upload.

        Use instead of transform/render when the target is a Miro board.
        Each chunk is a valid SVG string with single-quoted attribute values
        (safe for MCP JSON transport). Call canvas_create_from_svg with
        is_repository=True for each chunk in the returned list, in order.

        Returns {"format": "miro", "chunk_count": N, "chunks": [svg, ...]}.
        """
        if not content:
            raise ValueError("content is required — pass the story map artifact")
        source_fmt = self.format or "markdown"
        source_cls = _load_channel_class(source_fmt)
        target_cls = _load_channel_class("miro")
        source = source_cls()
        target = target_cls()
        canonical = source.parse(_normalize_input(source_fmt, content))
        chunks = target.render_chunks(canonical, chunk_size)
        return {"format": "miro", "chunk_count": len(chunks), "chunks": chunks}

    @agent_tool
    @mcp
    def render_miro(
        self,
        content: str,
        board_id: str,
        token: str = "",
        scale: float = 1.5,
        origin_x: float = 0.0,
        origin_y: float = 6000.0,
        clear_ids: str = "",
    ) -> dict:
        """Upload a story map directly to a Miro board via the REST API.

        Shapes are placed at exact board coordinates — no chunking, no stacking.
        Each shape is created as a Miro rectangle/round_rectangle with correct
        position (x/y centre, relative to canvas_center), size, colour, and label.

        Args:
            content: story map markdown (or other source format matching this instance).
            board_id: the board ID from the Miro URL (e.g. ``uXjVHuiSsAA=``).
            token: Miro PAT. Falls back to MIRO_TOKEN env var or ~/.miro-token.
                   Get a token at https://miro.com/app/settings/user-profile/apps
            scale: SVG units → Miro board units multiplier (default 1.5; story items
                   become 75×75 board units). Increase for larger / more readable items.
            origin_x: board X of the story-map top-left corner (default 0).
            origin_y: board Y of the story-map top-left corner (default 6000, below
                      most existing content).
            clear_ids: comma-separated Miro shape IDs to delete before uploading.
                       Use to clean up a previous broken upload.

        Returns:
            {"board_id", "shape_count", "scale", "origin", "ids": {semantic_id: miro_id}}.

        Estimated time: ~3 min for 541 shapes (350 ms delay between API calls).
        """
        from practices.stories.diagram.miro.api import MiroApiClient
        from practices.stories.diagram.miro.uploader import MiroUploader

        if not content:
            raise ValueError("content is required")
        if not board_id:
            raise ValueError("board_id is required")

        source_fmt = self.format or "markdown"
        source_cls = _load_channel_class(source_fmt)
        target_cls = _load_channel_class("miro")
        canonical = source_cls().parse(_normalize_input(source_fmt, content))

        client = MiroApiClient(token=token or None)
        uploader = MiroUploader(client)

        if clear_ids:
            ids_to_clear = [i.strip() for i in clear_ids.split(",") if i.strip()]
            deleted = uploader.clear(board_id, ids_to_clear)
        else:
            deleted = 0

        result = uploader.upload(
            canonical,
            board_id,
            scale=scale,
            origin_x=origin_x,
            origin_y=origin_y,
        )
        result["deleted"] = deleted
        return result
