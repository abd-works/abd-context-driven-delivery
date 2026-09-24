"""catalog_generator - discover-and-render primitives for the CDD HTML catalog.

Wraps the real object model directly (Toolset.tools, AgentToolSet.agent_tools,
BaseContextTool.fidelities) - there is no separate scraped schema. See
``catalog/cdd-catalog-plan.md`` and ``catalog/cdd-catalog-sketch.md`` for the
full design; this module implements the "Assemble Catalog Page Data" epic's
four discover-step stories:

- ``load_registry`` - Load Context Tool And Utility Registry
- ``scrape_fidelities`` - Scrape Fidelity Keys, Format Defaults, And Guidance Sections
- ``resolve_lifecycle_actions`` - Resolve Lifecycle Action Source Dir And Calls Via AST Walk
- ``skill_slash_name`` - Collect Skill Slash-Command Map From SKILL Frontmatter

It also implements "Render Self-Contained Catalog Pages" (``CatalogTool`` /
``CatalogAction`` / ``CatalogFidelity`` / ``CatalogContextTool`` /
``CatalogUtility`` / ``Catalog``, each with one ``generate_catalog(...)``
operation - see the sketch's Clean Engineering pass), "Make Catalog Output
Portable" (``git_blob_url``, ``resolve_repo_remote``, ``write_page``, ``build_run_request``), and
"Configure Illustrated Examples" (``parse_illustrated_examples``,
``extract_whole_file``, ``extract_heading_section``, ``extract_comment_tag``).
"""
from __future__ import annotations

import ast
import importlib
import inspect
import logging
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

from harness.guidance.guidance import FidelityGuidance
from harness.agent_tools import agent_tool, agent_toolset
from installation.files import skill
from harness.mcp.mcp_server import mcp

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SKILLS_DIR = _REPO_ROOT / ".cursor" / "skills"
_SKILL_NAME_RE = re.compile(r"^name:\s*(.+?)\s*$", re.MULTILINE)

# -- Registry ---------------------------------------------------------------
#
# Hardcoded per the plan's "Registry (context tools + utilities)" section -
# verified against the real classes on disk. CDD is the header row; the
# other five are the board's context-tool rows.

CONTEXT_TOOL_REGISTRY: tuple[tuple[str, str, str], ...] = (
    ("Context-driven delivery", "practices.cdd.cdd", "Cdd"),
    ("Stories", "practices.stories.stories", "Stories"),
    ("Clean Engineering", "practices.clean_engineering.clean_engineering", "CleanEngineering"),
    ("User Experience", "practices.ux.ux", "Ux"),
    ("Behavior-Driven Development", "practices.bdd.bdd", "Bdd"),
    ("Domain-Driven Design", "practices.ddd.ddd", "Ddd"),
)

# Harness owns generate (replaces the old deploy_agent_skills utility).
UTILITY_REGISTRY: tuple[tuple[str, str, str], ...] = (
    ("harness", "installer.installer", "Harness"),
    ("diagnose", "diagnose.diagnose", "Diagnose"),
    ("echo", "echo.echo", "Echo"),
    ("handoff", "handoff.handoff", "Handoff"),
    ("workspace", "workspace.workspace", "WorkSession"),
    ("sub_agent", "sub_agent.sub_agent", "SubAgent"),
)

@dataclass
class RegistryEntry:
    """One resolved registry row - a real, importable class, not a stub."""

    display_name: str
    module_path: str
    class_name: str
    cls: type = type

    def _load_class(self) -> type:
        module = importlib.import_module(self.module_path)
        return getattr(module, self.class_name)

    def toolset_name(self) -> str:
        import re

        return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", self.cls.__name__).lower()

    def fidelity_cards(self) -> list[str]:
        from catalog_generator.foundry_chrome import cap_card

        cards: list[str] = []
        for stage, fid_name in (getattr(self.cls, "fidelities", {}) or {}).items():
            cards.append(
                cap_card(
                    fid_name,
                    f"fidelities/{self.toolset_name()}-{fid_name}.html",
                    f"{self.display_name} · {stage}",
                    label="Fidelity",
                )
            )
        return cards

    def write_context_tool_page(self, catalog: Catalog) -> None:
        from catalog_generator.foundry_chrome import page_shell

        owner = self.cls()
        skill_name = SkillSlashName().resolve(owner.toolset_name) or owner.toolset_name
        guidances = CatalogFidelityGuidance.scrape(self.cls)
        context_tool = catalog.catalog_context_tool
        context_tool.owner = owner
        context_tool.display_name = self.display_name
        context_tool.skill_name = skill_name
        context_tool.guidances = guidances
        body = context_tool.generate_catalog()
        catalog._tool_bodies.append(body)
        catalog._current_entry = self
        catalog._current_owner = owner
        catalog._current_skill_name = skill_name
        catalog._prepare_tool_kanban()
        page = page_shell(
            title=f"{self.display_name} — CDD Catalog",
            h1=self.display_name,
            tagline="Context tool",
            body_inner=body,
            commons_prefix="../commons/",
            nav_prefix="../",
            nav_current="context-tools",
            kanban_embed=catalog._kanban_embed(),
        )
        CatalogPage(catalog.out_root).write(f"context-tools/{owner.toolset_name}.html", page)
        catalog._write_fidelity_pages(guidances)

    def write_utility_page(self, catalog: Catalog) -> None:
        from catalog_generator.foundry_chrome import page_shell

        try:
            owner: object = self.cls()
        except TypeError as error:
            logging.debug("Utility %s is not constructible: %s", self.display_name, error)
            owner = self.cls
        catalog.catalog_utility.owner = owner
        catalog.catalog_utility.display_name = self.display_name
        body = catalog.catalog_utility.generate_catalog()
        catalog._utility_bodies.append(body)
        page = page_shell(
            title=f"{self.display_name} — utility",
            h1=self.display_name,
            tagline="Utility",
            body_inner=body,
            commons_prefix="../commons/",
            nav_prefix="../",
            nav_current="tools",
            show_hero=False,
            body_wrap_class="skill-detail-page",
            kanban_embed=catalog._kanban_embed(),
        )
        CatalogPage(catalog.out_root).write(f"tools/{self.display_name}.html", page)

def load_registry() -> tuple[list[RegistryEntry], list[RegistryEntry]]:
    """Resolve every context-tool and utility registry row to a real class.

    Returns ``(practices, utilities)``. Resolution failures raise
    (``ImportError`` / ``AttributeError``) immediately - "nothing missing"
    is a hard fail at discover time, not a silently dropped row.
    """
    practices: list[RegistryEntry] = []
    for name, module_path, class_name in CONTEXT_TOOL_REGISTRY:
        entry = RegistryEntry(name, module_path, class_name)
        entry.cls = entry._load_class()
        practices.append(entry)
    utilities: list[RegistryEntry] = []
    for name, module_path, class_name in UTILITY_REGISTRY:
        entry = RegistryEntry(name, module_path, class_name)
        entry.cls = entry._load_class()
        utilities.append(entry)
    return practices, utilities

# -- Fidelity scraping --------------------------------------------------------

_GUIDANCE_MISSING = "Guidance missing"

_FORMAT_DIR_ALIASES: dict[str, tuple[str, ...]] = {
    "markdown": ("md", "markdown"),
    "python": ("py", "python"),
    "javascript": ("js", "javascript"),
    "typescript": ("ts", "typescript"),
    "java": ("java",),
    "html": ("html",),
    "drawio": ("drawio",),
}

_FORMAT_FILE_EXT: dict[str, str] = {
    "markdown": ".md",
    "md": ".md",
    "python": ".py",
    "py": ".py",
    "javascript": ".js",
    "js": ".js",
    "typescript": ".ts",
    "ts": ".ts",
    "java": ".java",
}

# CDD stage key → frontmatter fidelity tokens used in template YAML/headers.
_STAGE_FRONTMATTER_TOKENS: dict[str, tuple[str, ...]] = {
    "discovery": ("discovery",),
    "spec": ("exploration", "specification", "spec"),
    "engineer": ("engineering", "engineer"),
}

class TemplateFrontmatter:
    """Tokens in a template file's leading YAML or ``# ---`` comment block."""

    def tokens(self, text: str) -> set[str]:
        self._blob = _template_frontmatter_blob(text).lower()
        self._token_set: set[str] = set()
        for key in ("fidelity", "artifact", "format"):
            self._key = key
            self._collect_key_tokens()
        return self._token_set

    def _collect_key_tokens(self) -> None:
        blob = self._blob
        key = self._key
        listed = re.search(rf"{key}\s*:\s*\[([^\]]*)\]", blob)
        if listed:
            self._add_bracket_tokens(listed.group(1))
            return
        scalar = re.search(rf"{key}\s*:\s*([^\n]+)", blob)
        if not scalar:
            return
        tok = scalar.group(1).strip().strip("\"'").lower()
        if tok:
            self._token_set.add(tok)

    def _add_bracket_tokens(self, raw: str) -> None:
        for part in raw.split(","):
            tok = part.strip().strip("\"'").lower()
            if tok:
                self._token_set.add(tok)


class CatalogFidelityGuidance(FidelityGuidance):
    """Live FidelityGuidance plus the scraped ``##`` section for catalog pages."""

    def __init__(
        self,
        name: str = "",
        default_format: str | None = "",
        section: str = "",
        overview: str = "",
    ) -> None:
        super().__init__(name=name, default_format=default_format or "")
        self.section = section
        self.tool_overview = overview

    @property
    def key(self) -> str:
        return self.name

    @property
    def guidance(self) -> str:  # type: ignore[override]
        return self.section

    @property
    def overview(self) -> str:  # type: ignore[override]
        return self.tool_overview

    def write_catalog_page(self, catalog: Catalog) -> None:
        from catalog_generator.foundry_chrome import display_label, page_shell

        entry = catalog._current_entry
        owner = catalog._current_owner
        fidelity = catalog.catalog_context_tool.catalog_fidelity
        fidelity.fidelity_name = self.key
        fidelity.owner = owner
        fidelity.skill_name = catalog._current_skill_name
        fidelity.guidance = self.guidance
        fidelity.overview = self.overview
        fidelity.tool_display_name = entry.display_name
        fidelity.default_format = self.default_format
        fid_body = fidelity.generate_catalog()
        catalog._prepare_fidelity_kanban(self.key)
        fid_page = page_shell(
            title=f"{display_label(self.key)} — {entry.display_name}",
            h1=display_label(self.key),
            tagline=f"{entry.display_name} · fidelity",
            body_inner=fid_body,
            commons_prefix="../commons/",
            nav_prefix="../",
            nav_current="fidelities",
            show_hero=False,
            body_wrap_class="skill-detail-page",
            kanban_embed=catalog._kanban_embed(),
        )
        CatalogPage(catalog.out_root).write(
            f"fidelities/{owner.toolset_name}-{self.key}.html",
            fid_page,
        )

    @classmethod
    def scrape(cls, practice: type) -> list[CatalogFidelityGuidance]:
        """For every fidelity on ``practice``, resolve default format and ``##`` body."""
        from harness.markdown import Markdown

        keys = cls._fidelity_keys(practice)
        if not keys:
            return []
        module_dir = Path(importlib_module_file(practice.__module__)).resolve().parent
        guide_path = module_dir / f"{module_dir.name}.md"
        guide_text = guide_path.read_text(encoding="utf-8") if guide_path.is_file() else ""
        overview = extract_tool_overview(guide_text) if guide_text else ""
        results: list[CatalogFidelityGuidance] = []
        for fidelity_key in keys:
            section = HeadingSection(guide_text).extract(fidelity_key) if guide_text else None
            default_format = Markdown(None, "").fidelity_format(section) if section else None
            if not default_format:
                default_format = getattr(practice, "_fidelity_format_defaults", {}).get(
                    fidelity_key
                )
            results.append(
                cls(
                    name=fidelity_key,
                    default_format=default_format,
                    section=section if section is not None else _GUIDANCE_MISSING,
                    overview=overview,
                )
            )
        return results

    @classmethod
    def _fidelity_keys(cls, practice: type) -> list[str]:
        declared = practice.__dict__.get("fidelities")
        if isinstance(declared, dict):
            return list(declared.values())
        instance = practice()
        bag = getattr(instance, "fidelities", None)
        entries = getattr(bag, "entries", None)
        if isinstance(entries, dict):
            return [
                getattr(child, "name", None) or getattr(child, "fidelity", key)
                for key, child in entries.items()
            ]
        return []


def _template_frontmatter_blob(text: str) -> str:
    """Return the leading frontmatter block (YAML or ``# ---`` comment form)."""
    lines = text.splitlines()
    if not lines:
        return ""
    if lines[0].strip() == "---":
        end = next((i for i, ln in enumerate(lines[1:], 1) if ln.strip() == "---"), None)
        return "\n".join(lines[1:end]) if end is not None else ""
    if lines[0].strip() in ("# ---", "#---"):
        blob: list[str] = []
        for ln in lines[1:]:
            stripped = ln.strip()
            if stripped in ("# ---", "#---", "---"):
                break
            blob.append(stripped[2:].lstrip() if stripped.startswith("#") else stripped)
        return "\n".join(blob)
    return ""

def _slug_variants(domain_slug: str) -> list[str]:
    variants = [domain_slug]
    for alt in (domain_slug.replace("_", "-"), domain_slug.replace("-", "_")):
        if alt not in variants:
            variants.append(alt)
    return variants


class HeadingSection:
    """Body under one markdown heading, up to the next heading of that level."""

    def __init__(self, markdown: str, level: int = 2) -> None:
        self.markdown = markdown
        self.level = level

    def extract(self, heading: str) -> str | None:
        marker = "#" * self.level + " "
        lines = self.markdown.splitlines()
        start = None
        for i, line in enumerate(lines):
            if line.strip().lower() == (marker + heading).lower():
                start = i + 1
                break
        if start is None:
            return None
        end = len(lines)
        heading_re = re.compile(r"^#{1," + str(self.level) + r"}\s")
        for i in range(start, len(lines)):
            if heading_re.match(lines[i]):
                end = i
                break
        return "\n".join(lines[start:end]).strip()


class GitCitation:
    """Git blob URLs — the only source citation shape catalog pages emit."""

    def __init__(self, repo_url: str = "", ref: str = "") -> None:
        self.repo_url = repo_url
        self.ref = ref

    @classmethod
    def normalize(cls, repo_url: str) -> str:
        url = repo_url.strip()
        if url.startswith("git@"):
            host_and_path = url[len("git@"):]
            hostname, _, path = host_and_path.partition(":")
            url = f"https://{hostname}/{path}"
        if url.endswith(".git"):
            url = url[: -len(".git")]
        return url

    @classmethod
    def from_checkout(cls, repo_root: Path | None = None) -> GitCitation:
        root = repo_root or _REPO_ROOT
        repo_url = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=root, capture_output=True, text=True, check=True,
        ).stdout.strip()
        ref = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root, capture_output=True, text=True, check=True,
        ).stdout.strip()
        return cls(cls.normalize(repo_url), ref)

    def blob_url(self, path: Path, lines: tuple[int, int] | None = None) -> str:
        try:
            relative = path.resolve().relative_to(_REPO_ROOT)
        except ValueError:
            relative = path
        posix_path = relative.as_posix()
        url = f"{self.repo_url.rstrip('/')}/blob/{self.ref}/{posix_path}"
        if lines:
            start, end = lines
            url += f"#L{start}-L{end}" if end != start else f"#L{start}"
        return url

    def blob_url_for_callable(self, func: object) -> str:
        source_file = Path(inspect.getsourcefile(func))  # type: ignore[arg-type]
        _, start_line = inspect.getsourcelines(func)  # type: ignore[arg-type]
        end_line = start_line + len(inspect.getsource(func).splitlines()) - 1  # type: ignore[arg-type]
        return self.blob_url(source_file, (start_line, end_line))


class CatalogPage:
    """One generated HTML page written under an output root."""

    def __init__(self, out_root: Path) -> None:
        self.out_root = Path(out_root)

    def write(self, relative_path: str, html: str) -> Path:
        target = self.out_root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(html, encoding="utf-8")
        return target


class SkillSlashName:
    """Slash-invocable skill name from deployed SKILL.md frontmatter."""

    def resolve(self, module_dir_name: str) -> str | None:
        for candidate in (module_dir_name, module_dir_name.replace("_", "-")):
            skill_md = _SKILLS_DIR / candidate / "SKILL.md"
            if not skill_md.is_file():
                continue
            match = _SKILL_NAME_RE.search(skill_md.read_text(encoding="utf-8"))
            if match:
                return match.group(1)
        return None


def extract_tool_overview(markdown: str) -> str:
    """Prose under the opening H1 until Shared rules / first fidelity ``##``.

    Skips the Fidelity|Default Format|Produce index table — that is not the
    overview the fidelity page should lead with.
    """
    if not markdown.strip():
        return ""
    lines = markdown.splitlines()
    start = 0
    if lines and lines[0].startswith("# "):
        start = 1
    body_lines: list[str] = []
    for line in lines[start:]:
        stripped = line.strip()
        if stripped.lower() in ("## shared rules", "## scaffold"):
            break
        if re.match(r"^##\s+\S", stripped) and not stripped.lower().startswith("## shared"):
            break
        body_lines.append(line)
    while body_lines and not body_lines[-1].strip():
        body_lines.pop()
    return "\n".join(body_lines).strip()

def importlib_module_file(module_path: str) -> str:
    """Thin wrapper so ``scrape_fidelities`` needs only one import surface."""
    module = importlib.import_module(module_path)
    return module.__file__  # type: ignore[return-value]

# -- Lifecycle action resolution (AST walk) ----------------------------------

_ACTION_DECORATOR_NAME = "agent_instructions"

# Plan: emit top-level lifecycle actions; skip override hooks.
# ``generate_fixes_from_validate`` is a satisfy helper, not its own catalog action.
# ``improve`` sits after ``repair`` — same peer kit (``tools/repair/``),
# distinct guide (``improve.md``); the improve loop is catalogued as its own
# action, not folded into repair.
_LIFECYCLE_ACTION_SKIP = frozenset({
    "generate_output",
    "add_generate_header_to_generated",
    "generate_fixes_from_validate",
})

_LIFECYCLE_ACTIONS = frozenset({
    "generate",
    "document",
    "validate",
    "satisfy",
    "createRule",
})

_KIT_LIFECYCLE_SPECS: tuple[tuple[str, Path, str], ...] = (
        ("partition", _REPO_ROOT / "actions" / "partition" / "partition.py", "partition"),
        ("grill", _REPO_ROOT / "actions" / "grill_context" / "grill_context.py", "grill_context"),
        ("sketch", _REPO_ROOT / "actions" / "sketch" / "sketch.py", "sketch"),
        ("iterate", _REPO_ROOT / "actions" / "iterate" / "iterate.py", "iterate"),
        ("generate", _REPO_ROOT / "actions" / "generate" / "generate.py", "generate"),
        ("document", _REPO_ROOT / "actions" / "document" / "document.py", "document"),
        ("validate", _REPO_ROOT / "actions" / "validate" / "validate.py", "validate"),
        ("satisfy", _REPO_ROOT / "actions" / "satisfy" / "satisfy.py", "satisfy"),
        ("repair", _REPO_ROOT / "actions" / "improvement" / "improvement.py", "improvement"),
        ("createRule", _REPO_ROOT / "actions" / "validate" / "validate.py", "validate"),
    )

class ActionResolution:
    """One public lifecycle ``@agent_instructions``'s resolved delegate dir and same-instance calls."""

    def __init__(
        self,
        name: str = "",
        source_dir: Path | None = None,
        calls: list[str] | None = None,
    ) -> None:
        self.name = name
        self.source_dir = source_dir if source_dir is not None else Path()
        self.calls = calls if calls is not None else []
        self.tree: ast.Module | None = None
        self.body: list[ast.stmt] = []
        self.class_name = ""
        self.action_names: set[str] = set()
        self.node: ast.FunctionDef | None = None
        self._peer_kit_attrs: dict[str, str] = {}
        self._call_pairs: list[tuple[str, str]] = []
        self._kit_name = ""
        self._kit_path = Path()
        self._kit_dir_name = ""
        self._action_calls: list[str] = []

    def _decorator_names(self) -> set[str]:
        names: set[str] = set()
        if self.node is None:
            return names
        for dec in self.node.decorator_list:
            target = dec.func if isinstance(dec, ast.Call) else dec
            if isinstance(target, ast.Name):
                names.add(target.id)
            elif isinstance(target, ast.Attribute):
                names.add(target.attr)
        return names

    def _public_action_methods(self) -> list[ast.FunctionDef]:
        methods: list[ast.FunctionDef] = []
        if self.tree is None:
            return methods
        for node in self.tree.body:
            self._append_public_actions(node, methods)
        return methods

    def _append_public_actions(self, node: ast.stmt, methods: list[ast.FunctionDef]) -> None:
        if not isinstance(node, ast.ClassDef):
            return
        for item in node.body:
            self._maybe_append_action(item, methods)

    def _maybe_append_action(self, item: ast.stmt, methods: list[ast.FunctionDef]) -> None:
        if not isinstance(item, ast.FunctionDef):
            return
        if item.name.startswith("_") or item.name in _LIFECYCLE_ACTION_SKIP:
            return
        self.node = item
        if _ACTION_DECORATOR_NAME in self._decorator_names():
            methods.append(item)

    def _init_peer_kit_attrs(self) -> dict[str, str]:
        """Map ``self.<attr> = <ClassName>(...)`` assignments in ``__init__``."""
        self._peer_kit_attrs = {}
        if self.tree is None:
            return self._peer_kit_attrs
        for node in self.tree.body:
            if isinstance(node, ast.ClassDef):
                self._collect_class_init_peer_kits(node)
        return self._peer_kit_attrs

    def _collect_class_init_peer_kits(self, class_node: ast.ClassDef) -> None:
        for item in class_node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                self._collect_init_assignments(item)

    def _collect_init_assignments(self, init_fn: ast.FunctionDef) -> None:
        for stmt in ast.walk(init_fn):
            self._record_peer_kit_assignment(stmt)

    def _record_peer_kit_assignment(self, stmt: ast.AST) -> None:
        if not isinstance(stmt, ast.Assign) or len(stmt.targets) != 1:
            return
        target = stmt.targets[0]
        if not self._is_self_attr(target):
            return
        call_func = stmt.value.func if isinstance(stmt.value, ast.Call) else None
        if isinstance(call_func, ast.Name):
            self._peer_kit_attrs[target.attr] = call_func.id

    def _is_self_attr(self, target: ast.AST) -> bool:
        return (
            isinstance(target, ast.Attribute)
            and isinstance(target.value, ast.Name)
            and target.value.id == "self"
        )

    def _import_module_for_class(self) -> str | None:
        """Find ``from <module> import <class_name>`` at module top level."""
        if self.tree is None:
            return None
        for node in self.tree.body:
            found = self._module_from_import(node)
            if found is not None:
                return found
        return None

    def _module_from_import(self, node: ast.stmt) -> str | None:
        if not isinstance(node, ast.ImportFrom) or not node.module:
            return None
        for alias in node.names:
            if alias.name == self.class_name:
                return node.module
        return None

    def _double_attr_calls(self) -> list[tuple[str, str]]:
        """Every ``self.<attr>.<method>(...)`` call's ``(<attr>, <method>)`` pair."""
        self._call_pairs = []
        for stmt in self.body:
            self._collect_double_attr_from_stmt(stmt)
        return self._call_pairs

    def _collect_double_attr_from_stmt(self, stmt: ast.stmt) -> None:
        for node in ast.walk(stmt):
            self._record_double_attr_call(node)

    def _record_double_attr_call(self, node: ast.AST) -> None:
        if not isinstance(node, ast.Call):
            return
        func = node.func
        if not isinstance(func, ast.Attribute):
            return
        owner = func.value
        if (
            isinstance(owner, ast.Attribute)
            and isinstance(owner.value, ast.Name)
            and owner.value.id == "self"
        ):
            self._call_pairs.append((owner.attr, func.attr))

    def _same_instance_action_calls(self) -> list[str]:
        """Every ``self.<method>()`` call that names another public action."""
        self._action_calls = []
        for stmt in self.body:
            self._collect_same_instance_from_stmt(stmt)
        return self._action_calls

    def _collect_same_instance_from_stmt(self, stmt: ast.stmt) -> None:
        for node in ast.walk(stmt):
            self._record_same_instance_call(node)

    def _record_same_instance_call(self, node: ast.AST) -> None:
        if not isinstance(node, ast.Call):
            return
        func = node.func
        if not isinstance(func, ast.Attribute):
            return
        if not isinstance(func.value, ast.Name) or func.value.id != "self":
            return
        if func.attr in self.action_names and func.attr not in self._action_calls:
            self._action_calls.append(func.attr)

    def _guidance_action_calls(self) -> list[str]:
        """``guidance.<method>()`` or ``Generate().generate(...)`` dispatch."""
        self._action_calls = []
        for stmt in self.body:
            self._collect_guidance_from_stmt(stmt)
        return self._action_calls

    def _collect_guidance_from_stmt(self, stmt: ast.stmt) -> None:
        for node in ast.walk(stmt):
            self._record_guidance_call(node)

    def _record_guidance_call(self, node: ast.AST) -> None:
        if not isinstance(node, ast.Call):
            return
        func = node.func
        if not isinstance(func, ast.Attribute):
            return
        if func.attr not in self.action_names or func.attr in self._action_calls:
            return
        value = func.value
        if isinstance(value, ast.Name) and value.id in {"guidance", "host"}:
            self._action_calls.append(func.attr)
        elif func.attr == "generate":
            self._action_calls.append(func.attr)

    def _example_value(self, name: str, type_str: str) -> object:
        compact = type_str.replace(" ", "")
        if compact.endswith("|None") or compact == "None":
            return None
        if compact.startswith("list["):
            return []
        return f"<{name}>"

    def _resolve_actions_from_source(self, path: Path) -> list[tuple[str, ast.FunctionDef]]:
        self.tree = ast.parse(path.read_text(encoding="utf-8"))
        methods = self._public_action_methods()
        if self.action_names:
            methods = [m for m in methods if m.name in self.action_names]
        return [(m.name, m) for m in methods]

    def _resolve_kit_lifecycle_actions(self) -> list[ActionResolution]:
        results: list[ActionResolution] = []
        for name, path, dir_name in _KIT_LIFECYCLE_SPECS:
            self._kit_name = name
            self._kit_path = path
            self._kit_dir_name = dir_name
            resolution = self._resolution_for_kit()
            if resolution is not None:
                results.append(resolution)
        return results

    def _resolution_for_kit(self) -> ActionResolution | None:
        self.action_names = {self._kit_name}
        methods = self._resolve_actions_from_source(self._kit_path)
        if not methods:
            return None
        _method_name, method = methods[0]
        self.body = method.body
        self.action_names = {"generate"}
        return ActionResolution(
            name=self._kit_name,
            source_dir=_REPO_ROOT / "actions" / self._kit_dir_name,
            calls=self._guidance_action_calls(),
        )

    @classmethod
    def live_owner(cls) -> object:
        """Load live ``AgentTool`` objects for every kit-owned lifecycle action name."""
        actions: dict[str, object] = {}
        for action_name, module_path, class_name in _LIFECYCLE_KIT_IMPORTS:
            if action_name in actions:
                continue
            module = importlib.import_module(module_path)
            instance = getattr(module, class_name)()
            discovered = instance.agent_tools
            if action_name in discovered:
                actions[action_name] = discovered[action_name]

        class _Owner:
            pass

        owner = _Owner()
        owner.agent_tools = actions
        return owner

    def write_catalog_page(self, catalog: Catalog) -> None:
        from catalog_generator.foundry_chrome import page_shell

        action = catalog._action_owner.agent_tools[self.name]
        catalog_action = catalog.catalog_action
        catalog_action.action = action
        catalog_action.owner = catalog._action_owner
        catalog_action.source_dir = self.source_dir
        body = catalog_action.generate_catalog()
        catalog._action_bodies.append(body)
        page = page_shell(
            title=f"{self.name} — lifecycle action",
            h1=self.name,
            tagline="Lifecycle action",
            body_inner=body,
            commons_prefix="../commons/",
            nav_prefix="../",
            nav_current="actions",
            show_hero=False,
            body_wrap_class="skill-detail-page",
            kanban_embed=catalog._kanban_embed(),
        )
        CatalogPage(catalog.out_root).write(f"actions/{self.name}.html", page)


_LIFECYCLE_KIT_IMPORTS: tuple[tuple[str, str, str], ...] = (
    ("partition", "actions.partition.partition", "Partition"),
    ("grill", "actions.grill_context.grill_context", "GrillContext"),
    ("sketch", "actions.sketch.sketch", "Sketch"),
    ("iterate", "actions.iterate.iterate", "Iterate"),
    ("generate", "actions.generate.generate", "Generate"),
    ("document", "actions.document.document", "Document"),
    ("validate", "actions.validate.validate", "Validate"),
    ("satisfy", "actions.satisfy.satisfy", "Satisfy"),
    ("repair", "actions.improvement.improvement", "Improvement"),
    ("createRule", "actions.validate.validate", "Validate"),
)

def resolve_lifecycle_actions() -> list[ActionResolution]:
    """Resolve lifecycle action source dirs and same-instance calls from action kits."""
    kit_by_name = {r.name: r for r in ActionResolution()._resolve_kit_lifecycle_actions()}
    order = (
        "partition",
        "grill",
        "sketch",
        "generate",
        "document",
        "iterate",
        "validate",
        "satisfy",
        "repair",
        "createRule",
    )
    return [kit_by_name[name] for name in order if name in kit_by_name]

_LIFECYCLE_KITS = {
    "generate": "generate.generate:Generate",
    "validate": "validate.validate:Validate",
    "satisfy": "satisfy.satisfy:Satisfy",
    "document": "document.document:Document",
}

def build_run_request(
    cls: type,
    *,
    action: str,
    fidelity: str | None = None,
) -> dict:
    """Build a spec run-request dict from the live toolset manifest.

    Constructor parameters become ``context``; the named action's parameters
    become ``arguments``. ``fidelity`` (when the constructor accepts it) is
    filled with the given fidelity key.

    Context tools do not own generate / validate / satisfy / document — those
    live on the kits. A request for one of those actions on a context tool
    is rewritten to the kit with ``arguments.guidance`` carrying that Guidance.
    """
    examples = ActionResolution()
    if action in _LIFECYCLE_KITS and getattr(cls, "_is_context", False):
        signature = cls.manifest.signature
        ctor_params = (signature.get("new") or {}).get("parameters") or {}
        guidance_context: dict[str, object] = {}
        for name, type_str in ctor_params.items():
            if name == "fidelity" and fidelity is not None:
                guidance_context[name] = fidelity
            else:
                guidance_context[name] = examples._example_value(name, str(type_str))
        return {
            "toolset": _LIFECYCLE_KITS[action],
            "action": action,
            "arguments": {
                "guidance": [
                    {"toolset": f"{cls.__module__}:{cls.__name__}", "context": guidance_context},
                ]
            },
        }

    signature = cls.manifest.signature
    ctor_params = (signature.get("new") or {}).get("parameters") or {}
    action_entry = signature.get(action) or {}
    action_params = action_entry.get("parameters") or {}

    context: dict[str, object] = {}
    for name, type_str in ctor_params.items():
        if name == "fidelity" and fidelity is not None:
            context[name] = fidelity
        else:
            context[name] = examples._example_value(name, str(type_str))

    request: dict[str, object] = {
        "toolset": f"{cls.__module__}:{cls.__name__}",
        "context": context,
        "action": action,
    }
    if action_params:
        request["arguments"] = {
            name: examples._example_value(name, str(type_str))
            for name, type_str in action_params.items()
        }
    return request

def dump_run_request_yaml(
    cls: type,
    *,
    action: str,
    fidelity: str | None = None,
) -> str:
    """Serialize :func:`build_run_request` as plain YAML (no fences)."""
    try:
        import yaml
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("PyYAML is required to dump catalog request manifests") from exc
    return yaml.safe_dump(
        build_run_request(cls, action=action, fidelity=fidelity),
        sort_keys=False,
        default_flow_style=False,
    )

# -- Illustrated examples -----------------------------------------------------

@dataclass(frozen=True)
class IllustratedExampleRow:
    """One parsed row of a tool's ``## Illustrated examples`` config table."""

    fidelity: str
    source: str
    anchor: str

    @classmethod
    def parse(cls, markdown: str) -> list[IllustratedExampleRow]:
        section = HeadingSection(markdown).extract("Illustrated examples")
        if not section:
            return []
        rows: list[IllustratedExampleRow] = []
        lines = [line for line in section.splitlines() if _TABLE_ROW_RE.match(line)]
        for line in lines[2:]:
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if len(cells) < 3:
                continue
            fidelity, source, anchor = cells[0], cells[1], cells[2]
            rows.append(cls(fidelity=fidelity, source=source, anchor=anchor))
        return rows

    @classmethod
    def whole_file(cls, source_path: Path) -> str:
        return source_path.read_text(encoding="utf-8")

    @classmethod
    def comment_tag(cls, text: str, tag: str) -> str:
        return "\n".join(line for line in text.splitlines() if tag in line)

    def resolve(self, tool_dir: Path) -> str:
        source_path = tool_dir / self.source
        if self.anchor == "whole-file":
            return self.whole_file(source_path)
        text = source_path.read_text(encoding="utf-8")
        if self.anchor.startswith("<!--"):
            return self.comment_tag(text, self.anchor)
        level = 3 if self.anchor.startswith("###") else 2
        heading = self.anchor.lstrip("#").strip()
        section = HeadingSection(text, level=level).extract(heading)
        return section if section is not None else text

_TABLE_ROW_RE = re.compile(r"^\|(.+)\|\s*$")

# -- Render model (Clean Engineering pass) ------------------------------------
#
# Each class below wraps one real primitive one-for-one and exposes exactly
# one operation, generate_catalog, that renders that node and composes its
# children's generate_catalog calls against the live objects - no separate
# scraped schema. See catalog/cdd-catalog-sketch.md's Clean Engineering pass
# for the model these classes implement.
#
# Two small, necessary elaborations on the sketch's one-page model (documented
# here rather than left implicit): CatalogAction additionally takes an
# ``action_page_hrefs`` map so it can tell a hyperlinkable lifecycle-action
# name apart from a plain @agent_tool name when rendering "Tools/actions called"
# bullets; CatalogFidelity additionally takes the ordered list of
# ``ActionResolution`` (from ``resolve_lifecycle_actions``) so it knows the
# 9 actions and their href map without re-deriving them per fidelity page.

class CatalogTool:
    """The one-line, hyperlinked rendering of a single real ``@agent_tool`` call
    site - a git-blob source citation, since no catalog page exists for a
    plain tool."""

    def __init__(self, repo_url: str, ref: str) -> None:
        self.repo_url = repo_url
        self.ref = ref

    def generate_catalog(self, tool: object, owner: object) -> str:
        """Render one "Tools/actions called" bullet for a plain @agent_tool name.
        ``tool`` is the tool's name (str) or a ``_Tool``; ``owner`` is the
        toolset instance/class it was called on - never mutated."""
        name = tool if isinstance(tool, str) else getattr(tool, "name", str(tool))
        func = getattr(owner, name, None)
        if func is not None and callable(func):
            try:
                href = GitCitation(self.repo_url, self.ref).blob_url_for_callable(func)
                return f'<li><a href="{href}">{name}</a> <span class="tag">(tool, no page)</span></li>'
            except (TypeError, OSError) as error:
                logging.debug("Skipping source citation for %s: %s", name, error)
        return f'<li>{name} <span class="tag">(tool, no page)</span></li>'

class CatalogAction:
    """The four-fixed-section rendering of one real ``Action`` - Tools/actions
    called, Markdown instructions, Module overview, Code - used for every
    lifecycle-action detail page and reused unchanged for a utility's own
    actions."""

    def __init__(
        self,
        repo_url: str,
        ref: str,
        catalog_tool: CatalogTool,
        action_page_hrefs: dict[str, str] | None = None,
    ) -> None:
        self.repo_url = repo_url
        self.ref = ref
        self.catalog_tool = catalog_tool
        self.action_page_hrefs = action_page_hrefs or {}
        self.action: object | None = None
        self.owner: object | None = None
        self.source_dir = Path()

    def _calls_section(self, action: object, owner: object) -> str:
        tools = list(getattr(action, "signature_entry", {}).get("tools", []))
        if not tools:
            return "<p>Calls nothing else directly.</p>"
        items = []
        for name in tools:
            href = self.action_page_hrefs.get(name)
            if href:
                items.append(f'<li><a href="{href}">{name}</a></li>')
            else:
                items.append(self.catalog_tool.generate_catalog(name, owner))
        return "<ul>" + "".join(items) + "</ul>"

    def _guide_section(self, source_dir: Path, action_name: str | None = None) -> str:
        from catalog_generator.foundry_chrome import markdown_to_html

        # Prefer ``{action}.md`` when two lifecycle actions share a kit dir
        # (repair + improve both live under tools/repair/).
        candidates: list[Path] = []
        if action_name:
            candidates.append(source_dir / f"{action_name}.md")
        candidates.append(source_dir / f"{source_dir.name}.md")
        for guide_path in candidates:
            if guide_path.is_file():
                return markdown_to_html(guide_path.read_text(encoding="utf-8"))
        return "<p>No dedicated guide - see module overview below.</p>"

    def _overview_section(self, source_dir: Path) -> str:
        from catalog_generator.foundry_chrome import markdown_to_html

        overview_path = source_dir / ".context" / "module-context.md"
        if not overview_path.is_file():
            return "<p>No module-context.md yet.</p>"
        return markdown_to_html(overview_path.read_text(encoding="utf-8"))

    def generate_catalog(self) -> str:
        """Render one action detail body — fidelity-style dark callouts.

        Guide and ``.context/module-context.md`` render as HTML (same as fidelity
        guidance). No source-code dump.
        Page shell (board + skill-detail wrap) is applied by ``Catalog``.
        """
        import html as html_mod

        action = self.action
        owner = self.owner
        source_dir = self.source_dir
        name = getattr(action, "name", str(action))
        return (
            f'<header class="page-hero--detail fidelity-detail-header">'
            f'<p class="s-name">Lifecycle action</p>'
            f'<h1 class="page-headline">{html_mod.escape(name)}</h1>'
            f"</header>\n"
            f'<section class="install-block action-invoke" aria-labelledby="action-invoke-heading">'
            f'<h2 id="action-invoke-heading">Request</h2>'
            f'<p class="install-hint">used as action: <code>{html_mod.escape(name)}</code> in the request</p>'
            f"</section>\n"
            f'<section class="install-block action-section" aria-label="Tools / actions called">'
            f"<h2>Tools / actions called</h2>"
            f"{self._calls_section(action, owner)}"
            f"</section>\n"
            f'<section class="install-block fidelity-guidance action-section" '
            f'aria-label="Markdown instructions">'
            f"<h2>Markdown instructions</h2>"
            f"{self._guide_section(source_dir, name)}"
            f"</section>\n"
            f'<section class="install-block fidelity-guidance action-section" '
            f'aria-label="Module overview">'
            f"<h2>Module overview</h2>"
            f"{self._overview_section(source_dir)}"
            f"</section>\n"
        )

class CatalogFidelity:
    """The Section-0-quick-invoke-plus-guidance rendering of one fidelity name
    on one ``BaseContextTool`` instance."""

    def __init__(
        self,
        repo_url: str,
        ref: str,
        catalog_action: CatalogAction,
        lifecycle_actions: list[ActionResolution],
    ) -> None:
        self.repo_url = repo_url
        self.ref = ref
        self.catalog_action = catalog_action
        self.lifecycle_actions = lifecycle_actions
        self.skill_name = ""
        self.fidelity_name = ""
        self.toolset_name = ""
        self.owner: object | None = None
        self.guidance = ""
        self.example_body: str | None = None
        self.overview = ""
        self.tool_display_name = ""
        self.default_format: str | None = None

    def _quick_invoke(self) -> str:
        """Invoke block — Foundry install-block chrome, sits under the board."""
        skill_name = self.skill_name
        fidelity_name = self.fidelity_name
        action_links = ", ".join(
            f'<a href="../actions/{r.name}.html">{r.name}</a>' for r in self.lifecycle_actions
        )
        return (
            f'<section class="install-block fidelity-invoke" aria-labelledby="fidelity-invoke-heading">'
            f'<h2 id="fidelity-invoke-heading">Chat invoke</h2>'
            f'<pre class="install-snippet"><code>/{skill_name} &lt;action&gt; {fidelity_name}'
            f" — e.g. /{skill_name} generate {fidelity_name}</code></pre>"
            f'<p class="install-hint">&lt;action&gt; is one of: {action_links}</p>'
            f"</section>"
        )

    def _illustrated_example_panel(self) -> str:
        from catalog_generator.foundry_chrome import fence

        if self.example_body is None:
            return (
                '<section class="skill-cr-single illustrated-example">'
                "<h2>Illustrated example</h2>"
                "<p>No illustrated example configured yet.</p></section>"
            )
        return (
            f'<section class="skill-cr-single illustrated-example">'
            f"<h2>Illustrated example</h2>"
            f'{fence("text", self.example_body)}</section>'
        )

    def _default_template_panel(self) -> str:
        """Default-format template callout — sits above the illustrated example."""
        import html as html_mod

        from catalog_generator.foundry_chrome import fence

        default_format = self.default_format
        module_dir = self._module_dir()
        path = self.default_template_path()
        if path is None or not path.is_file():
            fmt = html_mod.escape(default_format or "unknown")
            return (
                '<section class="install-block fidelity-template" aria-label="Default template">'
                "<h2>Default template</h2>"
                f"<p>No template file for default format <code>{fmt}</code>.</p>"
                "</section>"
            )
        body = self._read_template_body(path)
        rel = self._template_relpath(path, module_dir)
        lang = self._template_lang(path)
        blob = GitCitation(self.repo_url, self.ref).blob_url(path)
        return (
            f'<section class="install-block fidelity-template" aria-label="Default template">'
            f"<h2>Default template</h2>"
            f'<p class="install-hint">Default format: <code>{html_mod.escape(default_format or "")}</code>'
            f' — <a href="{html_mod.escape(blob)}">{html_mod.escape(rel)}</a></p>'
            f"{fence(lang, body)}"
            f"</section>"
        )

    def _module_dir(self) -> Path:
        return Path(getattr(self.owner, "module_dir", Path("."))).resolve()

    def _domain_slug(self) -> str:
        return getattr(self.owner, "toolset_name", self._module_dir().name)

    def _format_aliases(self) -> tuple[str, ...]:
        fmt = (self.default_format or "").lower()
        return _FORMAT_DIR_ALIASES.get(fmt, (fmt,))

    def default_template_path(self) -> Path | None:
        if not self.default_format:
            return None
        named = self._named_template_file()
        if named is not None:
            return named
        templates_root = self._module_dir() / "templates"
        if not templates_root.is_dir():
            return None
        scored = self._scored_templates(templates_root)
        if scored:
            scored.sort(key=lambda pair: (-pair[0], len(pair[1].parts), pair[1].as_posix()))
            return scored[0][1].resolve()
        return self._fallback_root_template(templates_root)

    def _named_template_file(self) -> Path | None:
        shared = self._module_dir() / "templates"
        if not shared.is_dir():
            return None
        ext = _FORMAT_FILE_EXT.get(self.default_format.lower(), "")
        for slug in _slug_variants(self._domain_slug()):
            for stem in (f"{slug}-templates", f"{slug}-template"):
                found = self._named_stem_path(shared, stem, ext)
                if found is not None:
                    return found
        return None

    def _named_stem_path(self, shared: Path, stem: str, ext: str) -> Path | None:
        if ext:
            preferred = shared / f"{stem}{ext}"
            if preferred.is_file():
                return preferred.resolve()
        for path in sorted(shared.glob(f"{stem}.*")):
            return path.resolve()
        return None

    def _search_roots(self, templates_root: Path) -> list[Path]:
        aliases = self._format_aliases()
        roots = [templates_root / alias for alias in aliases if (templates_root / alias).is_dir()]
        return roots or [templates_root]

    def _candidate_template_paths(self, templates_root: Path) -> list[Path]:
        paths: list[Path] = []
        for root in self._search_roots(templates_root):
            for path in root.rglob("*"):
                if self._is_template_candidate(path):
                    paths.append(path)
        return paths

    def _is_template_candidate(self, path: Path) -> bool:
        if not path.is_file():
            return False
        if "sketch" in path.name.lower() or "components" in path.parts:
            return False
        return True

    def _scored_templates(self, templates_root: Path) -> list[tuple[int, Path]]:
        scored: list[tuple[int, Path]] = []
        for path in self._candidate_template_paths(templates_root):
            score = self._template_score(path)
            if score > 0:
                scored.append((score, path))
        return scored

    def _template_score(self, path: Path) -> int:
        fidelity = self.fidelity_name
        fidelity_kebab = fidelity.replace("_", "-")
        name_l = path.name.lower()
        stem_kebab = path.stem.replace("_", "-").lower()
        score = 0
        if stem_kebab == fidelity_kebab or path.stem.lower() == fidelity.lower():
            score += 100
        elif fidelity_kebab in stem_kebab or fidelity.lower() in path.stem.lower():
            score += 40
        tokens = self._path_frontmatter_tokens(path)
        if fidelity.lower() in tokens or fidelity_kebab in tokens:
            score += 50
        if self._stage_tokens() & tokens:
            score += 30
        if any(alias == path.parent.name.lower() for alias in self._format_aliases()):
            score += 5
        if "production" in name_l:
            score -= 20
        if path.suffix == ".tpl" or name_l.endswith(".py.tpl"):
            score += 10
        if fidelity == "scenarios" and "main-flow" in stem_kebab:
            score += 25
        return score

    def _path_frontmatter_tokens(self, path: Path) -> set[str]:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            return set()
        if not text:
            return set()
        return TemplateFrontmatter().tokens(text)

    def _stage_tokens(self) -> set[str]:
        fidelities = getattr(type(self.owner), "fidelities", None)
        if not isinstance(fidelities, dict):
            return set()
        stage_key = next(
            (stage for stage, name in fidelities.items() if name == self.fidelity_name),
            "",
        )
        return set(_STAGE_FRONTMATTER_TOKENS.get(stage_key, ()))

    def _fallback_root_template(self, templates_root: Path) -> Path | None:
        ext = _FORMAT_FILE_EXT.get((self.default_format or "").lower(), "")
        aliases = self._format_aliases()
        root_files = [
            path for path in templates_root.iterdir()
            if path.is_file() and "sketch" not in path.name.lower()
            and (not ext or path.suffix == ext or path.suffix.lstrip(".") in aliases)
        ]
        if len(root_files) == 1:
            return root_files[0].resolve()
        fidelity_kebab = self.fidelity_name.replace("_", "-")
        named = [
            path for path in root_files
            if fidelity_kebab in path.stem.replace("_", "-").lower()
            or self.fidelity_name.lower() in path.stem.lower()
        ]
        if named:
            return sorted(named)[0].resolve()
        return None

    def _read_template_body(self, path: Path) -> str:
        try:
            return path.read_text(encoding="utf-8")
        except OSError as error:
            logging.debug("Could not read template %s: %s", path, error)
            return ""

    def _template_relpath(self, path: Path, module_dir: Path) -> str:
        try:
            return path.relative_to(module_dir).as_posix()
        except ValueError as error:
            logging.debug("Template %s is outside %s: %s", path, module_dir, error)
            return path.name

    def _template_lang(self, path: Path) -> str:
        lang = path.suffix.lstrip(".") or "text"
        if path.name.endswith(".py.tpl"):
            return "python"
        if lang == "md":
            return "markdown"
        if lang == "tpl":
            return "text"
        return lang

    def _ensure_default_format(self) -> None:
        if self.default_format is not None:
            return
        defaults = getattr(type(self.owner), "_fidelity_format_defaults", {})
        self.default_format = defaults.get(self.fidelity_name)

    def _guidance_preview(self, label: str) -> str:
        from catalog_generator.foundry_chrome import markdown_to_html

        overview_html = markdown_to_html(self.overview) if self.overview.strip() else ""
        fid_md = f"## {label}\n\n{self.guidance}" if self.guidance else self.guidance
        bits = []
        if overview_html:
            bits.append(f"<h2>Overview</h2>\n{overview_html}")
        bits.append(markdown_to_html(fid_md))
        return "\n".join(bits)

    def generate_catalog(self) -> str:
        """Render everything under the board: title, invoke, guidance, template, example.

        Uses Foundry install-block chrome for invoke + guidance + default template
        (dark callout, orange links) — not the white skill-md-preview card.
        """
        import html as html_mod

        from catalog_generator.foundry_chrome import display_label

        self._ensure_default_format()
        label = display_label(self.fidelity_name)
        tool_label = self.tool_display_name or getattr(self.owner, "toolset_name", "")
        preview = self._guidance_preview(label)
        return (
            f'<header class="page-hero--detail fidelity-detail-header">'
            f'<p class="s-name">{html_mod.escape(tool_label)} · fidelity</p>'
            f'<h1 class="page-headline">{html_mod.escape(label)}</h1>'
            f"</header>\n"
            f"{self._quick_invoke()}\n"
            f'<section class="install-block fidelity-guidance" '
            f'data-fidelity="{html_mod.escape(self.fidelity_name)}" '
            f'aria-label="Fidelity guidance">'
            f"{preview}</section>\n"
            f"{self._default_template_panel()}\n"
            f"{self._illustrated_example_panel()}\n"
        )

    def section_0_html(self) -> str:
        return self._quick_invoke()

class CatalogContextTool:
    """The context-tool page for one ``BaseContextTool`` instance - Stories,
    DDD, UX, Clean Engineering, BDD, or CDD's own header-row page."""

    def __init__(self, repo_url: str, ref: str, catalog_fidelity: CatalogFidelity) -> None:
        self.repo_url = repo_url
        self.ref = ref
        self.catalog_fidelity = catalog_fidelity
        self.owner: object | None = None
        self.display_name = ""
        self.skill_name = ""
        self.guidances: list[CatalogFidelityGuidance] = []

    def generate_catalog(self) -> str:
        """Render one context-tool page body - badge, Purpose, fidelity cards
        (links only — never nest full fidelity pages)."""
        import html as html_mod

        from catalog_generator.foundry_chrome import display_label, markdown_to_html

        owner = self.owner
        display_name = self.display_name
        guidances = self.guidances
        purpose = (getattr(owner, "__doc__", "") or "").strip()
        overview = guidances[0].overview if guidances else ""
        purpose_html = markdown_to_html(overview) if overview else f"<p>{html_mod.escape(purpose)}</p>"
        slug = self._owner_slug()
        fidelities_section = self._fidelity_cards()
        return (
            f'<article class="context-tool-page" data-tool="{html_mod.escape(display_name)}">\n'
            f'  <header><span class="badge">{html_mod.escape(display_name)}</span></header>\n'
            f'  <div class="purpose-html">{purpose_html}</div>\n'
            f"{fidelities_section}"
            f"</article>"
        )

    def _owner_slug(self) -> str:
        return RegistryEntry("", "", "", type(self.owner)).toolset_name()

    def _fidelity_cards(self) -> str:
        import html as html_mod

        from catalog_generator.foundry_chrome import display_label

        owner = self.owner
        slug = self._owner_slug()
        if slug == "cdd":
            return ""
        fidelity_names = list(getattr(type(owner), "fidelities", {}).values())
        cards = "".join(
            f'<a class="cap-card fidelity-card" href="../fidelities/{slug}-{name}.html">'
            f'<p class="cap-card__title">{html_mod.escape(display_label(name))}</p>'
            f'<p class="cap-card__label">Fidelity</p>'
            f'<p class="cap-card__more">Open →</p></a>'
            for name in fidelity_names
        )
        return f'  <section class="fidelities cap-grid">{cards}</section>\n'

class CatalogUtility:
    """The utility-row detail page for one plain-utility ``Toolset`` instance."""

    def __init__(self, repo_url: str, ref: str, catalog_tool: CatalogTool, catalog_action: CatalogAction) -> None:
        self.repo_url = repo_url
        self.ref = ref
        self.catalog_tool = catalog_tool
        self.catalog_action = catalog_action
        self.owner: object | None = None
        self.display_name = ""

    def generate_catalog(self) -> str:
        """Render one utility page body — fidelity-style dark callouts."""
        import html as html_mod

        from catalog_generator.foundry_chrome import markdown_to_html

        owner = self.owner
        display_name = self.display_name
        target_cls = owner if isinstance(owner, type) else type(owner)
        module_dir = Path(inspect.getfile(target_cls)).resolve().parent
        purpose = (
            (getattr(owner, "__doc__", None) if not isinstance(owner, type) else None)
            or target_cls.__doc__
            or ""
        ).strip()
        guide_path = module_dir / f"{module_dir.name}.md"
        overview_path = module_dir / ".context" / "module-context.md"
        guide_html = (
            markdown_to_html(guide_path.read_text(encoding="utf-8"))
            if guide_path.is_file()
            else "<p>No dedicated guide.</p>"
        )
        overview_html = (
            markdown_to_html(overview_path.read_text(encoding="utf-8"))
            if overview_path.is_file()
            else f"<p>{html_mod.escape(purpose)}</p>"
        )
        return (
            f'<header class="page-hero--detail fidelity-detail-header">'
            f'<p class="s-name">Utility</p>'
            f'<h1 class="page-headline">{html_mod.escape(display_name)}</h1>'
            f"</header>\n"
            f'<section class="install-block fidelity-guidance action-section" '
            f'aria-label="Module overview">'
            f"<h2>Module overview</h2>"
            f"{overview_html}"
            f"</section>\n"
            f'<section class="install-block fidelity-guidance action-section" aria-label="Guide">'
            f"<h2>Guide</h2>"
            f"{guide_html}"
            f"</section>\n"
        )


@agent_toolset
class Catalog:
    """The top-level entry point - the only class ``generate_cdd_catalog.py``
    calls. Owns the shared portability config and the fixed roster of live
    instances to render. Always copies Foundry commons into ``out_root``."""

    def __init__(
        self,
        repo_url: str = "",
        ref: str = "",
        out_root: str = "catalog",
        brands_root: str | Path | None = None,
        catalog_context_tool: CatalogContextTool | None = None,
        catalog_action: CatalogAction | None = None,
        catalog_utility: CatalogUtility | None = None,
    ) -> None:
        citation = GitCitation.from_checkout()
        self.repo_url = repo_url or citation.repo_url
        self.ref = ref or citation.ref
        self.out_root = Path(out_root)
        self.brand = None
        from catalog_generator.foundry_chrome import Brand

        self.brands_root = Path(brands_root) if brands_root is not None else Brand().collection
        if catalog_context_tool is None or catalog_action is None or catalog_utility is None:
            wired = self._wire_catalog_renderers()
            self.catalog_context_tool = catalog_context_tool or wired[0]
            self.catalog_action = catalog_action or wired[1]
            self.catalog_utility = catalog_utility or wired[2]
        else:
            self.catalog_context_tool = catalog_context_tool
            self.catalog_action = catalog_action
            self.catalog_utility = catalog_utility
        self._context_tool_entries: list[RegistryEntry] = []
        self._utility_entries: list[RegistryEntry] = []
        self._lifecycle_actions: list[ActionResolution] = []
        self._action_owner: object | None = None
        self._board_tools: list[dict] = []
        self._action_dicts: list[dict] = []
        self._utility_dicts: list[dict] = []
        self._tool_bodies: list[str] = []
        self._action_bodies: list[str] = []
        self._utility_bodies: list[str] = []
        self._current_entry: RegistryEntry | None = None
        self._current_owner: object | None = None
        self._current_skill_name = ""
        self._kanban_path_prefix = "../"
        self._kanban_highlight_tool = None
        self._kanban_highlight_fidelity = None
        self._kanban_initial_family = None
        self.pages: dict[str, str] = {}

    def _wire_catalog_renderers(self) -> tuple[CatalogContextTool, CatalogAction, CatalogUtility]:
        lifecycle_actions = resolve_lifecycle_actions()
        catalog_tool = CatalogTool(self.repo_url, self.ref)
        hrefs = {r.name: f"actions/{r.name}.html" for r in lifecycle_actions}
        catalog_action = CatalogAction(self.repo_url, self.ref, catalog_tool, hrefs)
        catalog_fidelity = CatalogFidelity(
            self.repo_url, self.ref, catalog_action, lifecycle_actions
        )
        catalog_context_tool = CatalogContextTool(self.repo_url, self.ref, catalog_fidelity)
        catalog_utility = CatalogUtility(self.repo_url, self.ref, catalog_tool, catalog_action)
        return catalog_context_tool, catalog_action, catalog_utility

    def _board_tool_entries(self) -> list[dict]:
        from catalog_generator.foundry_chrome import STAGES
        from practices.cdd.cdd import _CONTEXT_TOOLS_BY_STAGE

        tools_on_stage: dict[str, set[str]] = {
            stage: {RegistryEntry("", "", "", cls).toolset_name() for cls in classes}
            for stage, classes in _CONTEXT_TOOLS_BY_STAGE.items()
        }
        self._board_stages = STAGES
        self._tools_on_stage = tools_on_stage
        return [self._board_row_for_entry(entry) for entry in self._context_tool_entries]

    def _board_row_for_entry(self, entry: RegistryEntry) -> dict:
        self._board_fidelities = getattr(entry.cls, "fidelities", {}) or {}
        self._board_tool_name = entry.toolset_name()
        self._board_stage_map: dict[str, dict] = {}
        for stage_key, _label in self._board_stages:
            self._board_stage_key = stage_key
            self._fill_board_stage()
        return {
            "display_name": entry.display_name,
            "toolset_name": self._board_tool_name,
            "href": f"context-tools/{self._board_tool_name}.html",
            "fidelities": self._board_stage_map,
        }

    def _fill_board_stage(self) -> None:
        tool_name = self._board_tool_name
        stage_key = self._board_stage_key
        if tool_name != "cdd" and tool_name not in self._tools_on_stage.get(stage_key, set()):
            return
        fid_name = self._board_fidelities.get(stage_key)
        if fid_name:
            self._board_stage_map[stage_key] = {
                "key": fid_name,
                "href": f"fidelities/{tool_name}-{fid_name}.html",
            }

    @classmethod
    def from_registry(cls, guidance: Iterable[Any] | None = None) -> Catalog:
        catalog = cls()
        for item in list(guidance or ()):
            catalog.add_guidance(item)
        return catalog

    def add_guidance(self, guidance: Any) -> None:
        from harness.markdown import HTML, Markdown

        slug = getattr(guidance, "context_index_key", None) or type(guidance).__name__
        for label in ("context", "guidance", "examples"):
            try:
                md = Markdown.from_label(guidance, "overview" if label == "context" else label)
                page = md.html()
            except Exception as error:
                logging.debug("Skipping catalog page %s-%s: %s", slug, label, error)
                continue
            if str(page).strip():
                self.pages[f"{slug}-{label}"] = str(page)
        fidelities = getattr(guidance, "fidelities", None)
        entries = getattr(fidelities, "entries", {}) if fidelities is not None else {}
        for name, child in entries.items():
            html = HTML.from_markdown(getattr(child, "guidance", "") or "")
            self.pages[f"{slug}-{name}"] = str(html)

    def _write_guidance_html_pages(self, out_root: Path) -> None:
        root = Path(out_root)
        root.mkdir(parents=True, exist_ok=True)
        for name, body in self.pages.items():
            (root / f"{name}.html").write_text(body, encoding="utf-8")

    @mcp
    @skill
    @agent_tool
    def generate_catalog(self, brand: str | Path = "") -> str:
        """Render the whole catalog into ``out_root`` with Foundry chrome.
        No output is ever written outside ``out_root``.
        ``brand`` is a collection name under the brands folder, or a path to a
        brand folder; empty uses bundled abd-works."""
        from catalog_generator.foundry_chrome import Brand

        if self.pages:
            root = Path(brand) if brand else self.out_root
            self._write_guidance_html_pages(root)
            return f"Wrote {len(self.pages)} guidance pages into {root}"
        self.brand = Brand(collection=self.brands_root).resolve(str(brand)) if brand else None
        self._context_tool_entries, self._utility_entries = load_registry()
        self._lifecycle_actions = resolve_lifecycle_actions()
        self._action_owner = ActionResolution.live_owner()
        self._render_catalog()
        return f"Catalog regenerated into {self.out_root} using {self.repo_url}@{self.ref}"

    @property
    def brands(self) -> dict[str, Path]:
        from catalog_generator.foundry_chrome import Brand

        return Brand(collection=self.brands_root).folders()

    @mcp
    @skill
    @agent_tool
    def apply_brand(self, name: str) -> str:
        """Overlay a named brand from the catalog brands collection onto the
        generated catalog commons without regenerating pages. ``name`` is a
        folder name under the brands collection, or a path to a brand folder.
        Bundled ``abd-works`` is always available."""
        from catalog_generator.foundry_chrome import Brand

        if not name:
            return f"Known brands: {', '.join(sorted(self.brands))}"
        dest = Brand(collection=self.brands_root).apply_named(self.out_root, name)
        self.brand = dest
        return f"Applied brand {name} under {dest}"

    def write_page(self, relative_path: str, html: str) -> Path:
        return CatalogPage(self.out_root).write(relative_path, html)

    def write_raw_manifests(self) -> None:
        return None

    def _render_catalog(self) -> None:
        """Write every catalog page under ``self.out_root``."""
        from catalog_generator.foundry_chrome import Brand

        self.out_root.mkdir(parents=True, exist_ok=True)
        Brand(collection=self.brands_root, folder=self.brand).copy_commons(self.out_root)
        self._board_tools = self._board_tool_entries()
        self._action_dicts = [
            {"name": r.name, "href": f"actions/{r.name}.html"}
            for r in self._lifecycle_actions
        ]
        self._utility_dicts = [
            {"name": e.display_name, "href": f"tools/{e.display_name}.html"}
            for e in self._utility_entries
        ]
        self._tool_bodies = []
        self._action_bodies = []
        self._utility_bodies = []
        self._write_context_tool_pages()
        self._write_action_pages()
        self._write_utility_pages()
        self._write_hub()
        self._write_workflow()
        self._write_grid_pages()

    def _kanban_embed(self) -> str:
        from catalog_generator.foundry_chrome import render_hub_board

        return render_hub_board(
            self._board_tools,
            self._action_dicts,
            self._utility_dicts,
            path_prefix=self._kanban_path_prefix,
            highlight_tool=self._kanban_highlight_tool,
            highlight_fidelity=self._kanban_highlight_fidelity,
            initial_family=self._kanban_initial_family,
        )

    def _write_context_tool_pages(self) -> None:
        for entry in self._context_tool_entries:
            entry.write_context_tool_page(self)

    def _write_fidelity_pages(self, guidances: list[CatalogFidelityGuidance]) -> None:
        for guidance in guidances:
            guidance.write_catalog_page(self)

    def _write_action_pages(self) -> None:
        self._prepare_plain_kanban()
        for resolution in self._lifecycle_actions:
            resolution.write_catalog_page(self)

    def _write_utility_pages(self) -> None:
        self._prepare_plain_kanban()
        for entry in self._utility_entries:
            entry.write_utility_page(self)

    def _prepare_tool_kanban(self) -> None:
        tool_name = self._current_owner.toolset_name
        self._kanban_path_prefix = "../"
        self._kanban_highlight_tool = tool_name
        self._kanban_highlight_fidelity = None
        self._kanban_initial_family = tool_name

    def _prepare_plain_kanban(self) -> None:
        self._kanban_path_prefix = "../"
        self._kanban_highlight_tool = None
        self._kanban_highlight_fidelity = None
        self._kanban_initial_family = None

    def _prepare_fidelity_kanban(self, fidelity_key: str) -> None:
        tool_name = self._current_owner.toolset_name
        self._kanban_path_prefix = "../"
        self._kanban_highlight_tool = tool_name
        self._kanban_highlight_fidelity = fidelity_key
        self._kanban_initial_family = tool_name

    def _write_hub(self) -> None:
        from catalog_generator.foundry_chrome import page_shell, render_hub_board

        board = render_hub_board(self._board_tools, self._action_dicts, self._utility_dicts)
        hub = page_shell(
            title="The ABD Foundry — Context Driven Delivery",
            h1='The ABD <span class="accent">Foundry</span>',
            tagline=(
                "The ABD Foundry — thirty years of product engineering experience "
                "shared as agents, skills, and tools that anyone can use. Grab the repo "
                '<a href="https://github.com/abd-works/abd-context-driven-delivery" '
                'target="_blank" rel="noopener noreferrer">here</a>.'
            ),
            body_inner=self._hub_body(),
            commons_prefix="commons/",
            nav_prefix="",
            nav_current="hub",
            kanban_embed=board,
        )
        self.write_page("index.html", hub)

    def _hub_body(self) -> str:
        import html as html_mod

        harness_href = GitCitation(self.repo_url, self.ref).blob_url(
            _REPO_ROOT / "harness" / "harness" / "harness.py",
        )
        return (
            '<section class="catalog-workflow" aria-labelledby="catalog-workflow-heading">'
            '<h2 id="catalog-workflow-heading">'
            '<a href="workflow.html">CDD Workflow</a>'
            "</h2>"
            "<p>Scenario-based steps for partitioning docs, documenting existing systems, "
            "designing new work, and fixing artifacts — using context tools, actions, and fidelities.</p>"
            "</section>\n"
            '<section class="install-block catalog-install" aria-labelledby="catalog-install-heading">'
            '<h2 id="catalog-install-heading">Install</h2>'
            "<ol>"
            "<li>Get the repository: "
            f'<a href="{html_mod.escape(self.repo_url)}" target="_blank" rel="noopener noreferrer">'
            f"{html_mod.escape(self.repo_url)}</a>.</li>"
            "<li>Add it to your project (clone into the workspace or add it as a sibling "
            "checkout the agent can see).</li>"
            "<li>Drop "
            f'<a href="{html_mod.escape(harness_href)}" target="_blank" rel="noopener noreferrer">'
            "<code>installation/harness.py</code></a> "
            "into the chat and ask the agent to run "
            "<strong>generate</strong> "
            "(action <code>generate</code>). "
            "That deploys each context tool as an IDE skill shim.</li>"
            "</ol>"
            "</section>\n"
        )

    def _write_workflow(self) -> None:
        from catalog_generator.foundry_chrome import markdown_to_html, page_shell

        workflow_md_path = _REPO_ROOT / "catalog" / "workflow.md"
        if not workflow_md_path.is_file():
            return
        workflow_md = workflow_md_path.read_text(encoding="utf-8")
        workflow_body_md = re.sub(
            r"^#\s+.*\n+", "", workflow_md.lstrip(), count=1, flags=re.MULTILINE
        )
        workflow_html = page_shell(
            title="CDD Workflow — ABD Foundry",
            h1="CDD Workflow",
            tagline=(
                "Scenario-based steps for using context tools, actions, and fidelities. "
                '<a href="index.html">Back to catalog</a>.'
            ),
            body_inner=(
                '<article class="catalog-workflow-page">'
                + markdown_to_html(workflow_body_md, include_tables=True)
                + "</article>"
            ),
            commons_prefix="commons/",
            nav_prefix="",
            nav_current="hub",
        )
        self.write_page("workflow.html", workflow_html)

    def _write_grid_pages(self) -> None:
        self._write_context_tools_grid()
        self._write_actions_grid()
        self._write_utilities_grid()
        self._write_fidelities_grid()

    def _write_context_tools_grid(self) -> None:
        from catalog_generator.foundry_chrome import cap_card, page_shell

        self.write_page(
            "context-tools.html",
            page_shell(
                title="Context tools — CDD Catalog",
                h1="Context tools",
                tagline="Every context tool in the catalog",
                body_inner='<div class="cap-grid">' + "".join(
                    cap_card(e.display_name, f"context-tools/{e.toolset_name()}.html", e.display_name)
                    for e in self._context_tool_entries
                ) + "</div>"
                + f'<div hidden>{"".join(self._tool_bodies)}</div>',
                commons_prefix="commons/",
                nav_current="context-tools",
            ),
        )

    def _write_actions_grid(self) -> None:
        from catalog_generator.foundry_chrome import cap_card, page_shell

        self.write_page(
            "actions.html",
            page_shell(
                title="Actions — CDD Catalog",
                h1="Actions",
                tagline="Lifecycle actions",
                body_inner='<div class="cap-grid">' + "".join(
                    cap_card(r.name, f"actions/{r.name}.html", "Lifecycle action")
                    for r in self._lifecycle_actions
                ) + "</div>"
                + f'<div hidden>{"".join(self._action_bodies)}</div>',
                commons_prefix="commons/",
                nav_current="actions",
            ),
        )

    def _write_utilities_grid(self) -> None:
        from catalog_generator.foundry_chrome import cap_card, page_shell

        self.write_page(
            "tools.html",
            page_shell(
                title="Utilities — CDD Catalog",
                h1="Utilities",
                tagline="Foundational utilities",
                body_inner='<div class="cap-grid">' + "".join(
                    cap_card(e.display_name, f"tools/{e.display_name}.html", "Utility")
                    for e in self._utility_entries
                ) + "</div>"
                + f'<div hidden>{"".join(self._utility_bodies)}</div>',
                commons_prefix="commons/",
                nav_current="tools",
            ),
        )

    def _write_fidelities_grid(self) -> None:
        from catalog_generator.foundry_chrome import cap_card, page_shell

        fid_cards = []
        for entry in self._context_tool_entries:
            fid_cards.extend(entry.fidelity_cards())
        self.write_page(
            "fidelities.html",
            page_shell(
                title="Fidelities — CDD Catalog",
                h1="Fidelities",
                tagline="Every fidelity ticket",
                body_inner='<div class="cap-grid">' + "".join(fid_cards) + "</div>",
                commons_prefix="commons/",
                nav_current="fidelities",
            ),
        )

