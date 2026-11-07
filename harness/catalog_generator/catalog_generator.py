"""catalog_generator - discover-and-render primitives for the CDD HTML catalog.

Wraps the real object model directly (the practice catalogue's live
PracticeGuidance and FidelityGuidance, each action kit's AgentTools) - there is
no separate scraped schema. See ``catalog/cdd-catalog-plan.md`` and
``catalog/cdd-catalog-sketch.md`` for the full design; this module implements
the "Assemble Catalog Page Data" epic's four discover-step stories:

- ``catalog_practices`` / ``catalog_utilities`` - Load Context Tool And Utility Registry
- each practice's live ``FidelityGuidance`` gives the fidelity name, stage, default format, and ``section`` text
- ``resolve_lifecycle_actions`` - each lifecycle action's kit, its live tool, and its folder
- ``SkillSlashName`` - Collect Skill Slash-Command Map From SKILL Frontmatter

It also implements "Render Self-Contained Catalog Pages" (``CatalogTool`` /
``CatalogAction`` / ``CatalogFidelity`` / ``CatalogContextTool`` /
``CatalogUtility`` / ``Catalog``, each with one ``generate_catalog(...)``
operation - see the sketch's Clean Engineering pass), "Make Catalog Output
Portable" (``git_blob_url``, ``resolve_repo_remote``, ``write_page``, ``build_run_request``), and
"Configure Illustrated Examples" (``parse_illustrated_examples``,
``extract_whole_file``, ``extract_heading_section``, ``extract_comment_tag``).
"""
from __future__ import annotations

import importlib
import inspect
import logging
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from harness.agent_tools.name import Name
from harness.catalog_generator.foundry_chrome import STAGE_COLUMNS, StageColumn
from harness.guidance.guidance import FidelityGuidance, PracticeGuidance
from harness.guidance.practice_catalogue import PracticeCatalogue
from harness.markdown.format import Format
from harness.markdown.markdown import MarkdownText
from harness.agent_tools import agent_instructions, agent_tool, agent_toolset, tools
from harness.installation.destination import NoCatalog, noCatalog
from harness.installation.files import skill
from harness.mcp.mcp_server import mcp
from space.work_state import project_checkout

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SKILLS_ROOTS = (_REPO_ROOT / ".claude" / "skills", _REPO_ROOT / ".cursor" / "skills")
_SKILL_NAME_RE = re.compile(r"^name:\s*(.+?)\s*$", re.MULTILINE)

# -- Practices and utilities --------------------------------------------------
#
# The practices come from the practice catalogue: each live PracticeGuidance with
# at least one fidelity on the board, unless marked @noCatalog. Each practice
# describes itself for the catalog in its ``catalog_card``.


class CatalogPractice:
    """One practice as the catalog shows it: the live ``PracticeGuidance``, the catalog card it gives itself, and its
    fidelities placed in the board's stage columns. Every page, board row, and grid card for the practice reads it."""

    _CARD_DEFAULTS: dict[str, Any] = {
        "family": "aad-fam-other",
        "perspective": "other",
        "order": 100,
        "blurb": "",
        "spec_blurb": "",
    }

    def __init__(self, practice: PracticeGuidance, skills: SkillSlashName | None = None) -> None:
        self.practice = practice
        self._skills = skills or SkillSlashName()
        self._card = self._card_of(type(practice))

    def _card_of(self, practice_class: type) -> dict[str, Any]:
        card = {**self._CARD_DEFAULTS, **(getattr(practice_class, "catalog_card", None) or {})}
        card.setdefault("name", re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", practice_class.__name__))
        card.setdefault("label", card["name"].lower().replace(" ", "-"))
        return card

    @property
    def key(self) -> str:
        """The practice's key, such as ``clean_engineering``: its page names, board rows, and skill lookups use it."""
        return self.practice.key

    @property
    def display_name(self) -> str:
        return self._card["name"]

    @property
    def label(self) -> str:
        """The practice's kebab-case name on the board's practice rail and approach grids."""
        return self._card["label"]

    @property
    def family(self) -> str:
        """The practice's colour family class on the board."""
        return self._card["family"]

    @property
    def perspective(self) -> str:
        return self._card["perspective"]

    @property
    def order(self) -> int:
        return self._card["order"]

    @property
    def spec_blurb(self) -> str:
        return self._card["spec_blurb"]

    @property
    def href(self) -> str:
        return f"context-tools/{self.key}.html"

    @property
    def skill_name(self) -> str:
        """The slash command that runs the practice, from its deployed skill; its key when it has none deployed."""
        return self._skills.resolve(self.key) or self.key

    @property
    def fidelities(self) -> list[FidelityGuidance]:
        """The practice's fidelities in declared order, less those marked ``@noCatalog``."""
        return [fidelity for fidelity in self.practice.fidelities if not NoCatalog.marks(fidelity)]

    def column_of(self, fidelity: FidelityGuidance) -> StageColumn | None:
        return STAGE_COLUMNS.of(fidelity.stage)

    def fidelity_in(self, column: StageColumn) -> FidelityGuidance | None:
        """The practice's fidelity in ``column``; none when the practice has no fidelity at that stage."""
        return next((fidelity for fidelity in self.fidelities if self.column_of(fidelity) is column), None)

    @property
    def on_board(self) -> bool:
        """Whether any fidelity has a board column; a practice with none, such as a pattern, has no catalog page."""
        return any(self.column_of(fidelity) is not None for fidelity in self.fidelities)

    def fidelity_href(self, fidelity: FidelityGuidance) -> str:
        return f"fidelities/{self.key}-{fidelity.name}.html"

    @property
    def shared_markdown(self) -> str:
        """The practice-level ``##`` sections of the practice guide, each with its heading: everything but
        ``## Fidelities``, whose blocks each fidelity page shows. The guide is read with the same ``MarkdownText``
        that gives each ``FidelityGuidance`` its section."""
        guide = self.practice.domain_markdown_path()
        if not guide.is_file():
            return ""
        document = MarkdownText(guide.read_text(encoding="utf-8"))
        names = [name for _start, _end, level, name in document.headings() if level == 2]
        sections = (document.slice_heading(name) for name in names if name.casefold() != "fidelities")
        return "\n\n".join(section for section in sections if section)


def catalog_practices() -> list[CatalogPractice]:
    """Every practice in the practice catalogue with a fidelity on the board, unless marked ``@noCatalog``, in the
    order each practice's catalog card gives."""
    practices = [
        CatalogPractice(practice)
        for practice in PracticeCatalogue.practices()
        if not NoCatalog.marks(type(practice))
    ]
    shown = [practice for practice in practices if practice.on_board]
    return sorted(shown, key=lambda practice: (practice.order, practice.display_name))


# Installer owns install. Diagnose, echo, handoff, and workspace are live utilities.
UTILITY_REGISTRY: tuple[tuple[str, str, str], ...] = (
    ("installer", "harness.installation.installer", "Installer"),
    ("diagnose", "cdd_guidance.actions.diagnose.diagnose", "Diagnose"),
    ("echo", "tools.echo.echo", "Echo"),
    ("repo", "space.repo.repo", "Repo"),
)


@dataclass
class RegistryEntry:
    """One utility the catalog shows: a real, importable class, not a stub."""

    name: str
    module_path: str
    class_name: str
    cls: type = type

    @property
    def href(self) -> str:
        return f"tools/{self.name}.html"

    @property
    def owner(self) -> object:
        """An instance of the utility, or the class itself when it cannot be built without arguments."""
        try:
            return self.cls()
        except TypeError as error:
            logging.debug("Utility %s is not constructible: %s", self.name, error)
            return self.cls


def catalog_utilities() -> list[RegistryEntry]:
    """Every utility in ``UTILITY_REGISTRY``, less those marked ``@noCatalog``. A utility that cannot be imported
    raises (``ImportError`` / ``AttributeError``) rather than leaving a silent gap."""
    entries = [
        RegistryEntry(name, module_path, class_name, getattr(importlib.import_module(module_path), class_name))
        for name, module_path, class_name in UTILITY_REGISTRY
    ]
    return [entry for entry in entries if keep_in_catalog(entry)]


def keep_in_catalog(entry: RegistryEntry) -> bool:
    """Registry rows marked ``@noCatalog`` stay deployed and stay out of the catalog."""
    return not NoCatalog.marks(entry.cls)


# -- Fidelity templates -------------------------------------------------------


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

    def __init__(self, skills_roots: Iterable[Path] = _SKILLS_ROOTS) -> None:
        self._skills_roots = tuple(skills_roots)

    def resolve(self, module_dir_name: str) -> str | None:
        for candidate in (module_dir_name, module_dir_name.replace("_", "-")):
            for skill_md in self._skill_files(candidate):
                match = _SKILL_NAME_RE.search(skill_md.read_text(encoding="utf-8"))
                if match:
                    return match.group(1)
        return None

    def _skill_files(self, candidate: str) -> list[Path]:
        found: list[Path] = []
        for root in self._skills_roots:
            found.extend(self._skill_files_under(root, candidate))
        return [path for path in found if path.is_file()]

    def _skill_files_under(self, root: Path, candidate: str) -> list[Path]:
        """``{candidate}/SKILL.md`` at the skills root, the Cursor layout
        ``{category}/{candidate}/SKILL.md``, and the Claude layout, which joins the
        category into one folder name: ``{category}-{candidate}/SKILL.md``."""
        found = [root / candidate / "SKILL.md"]
        if not root.is_dir():
            return found
        flat_name = re.compile(rf"^[a-z0-9_]+-{re.escape(candidate)}$")
        for folder in sorted(root.iterdir()):
            if not folder.is_dir():
                continue
            found.append(folder / candidate / "SKILL.md")
            if flat_name.match(folder.name):
                found.append(folder / "SKILL.md")
        return found





def _insert_after_heading(html_text: str, heading: str, insertion: str) -> str:
    """Place ``insertion`` after the named heading's section, before the next heading."""
    match = re.search(rf"<h([1-4])>{re.escape(heading)}</h\1>", html_text)
    if not match:
        return html_text + insertion
    start = match.end()
    nxt = re.search(r"<h[1-4]>", html_text[start:])
    insert_at = start + nxt.start() if nxt else len(html_text)
    return html_text[:insert_at] + insertion + html_text[insert_at:]


def _first_prose_paragraph(text: str) -> str:
    lines: list[str] = []
    started = False
    in_fence = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            if started:
                break
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if not stripped or stripped.startswith("#"):
            if started:
                break
            continue
        started = True
        lines.append(line)
    return "\n".join(lines).strip()

# -- Lifecycle actions --------------------------------------------------------


class LifecycleAction:
    """One lifecycle action the catalog gives a page: its name, the action kit class that owns it, and that kit's
    live ``AgentTool``. The kit's folder holds the action's guide and module overview."""

    def __init__(self, name: str, module: str, class_name: str) -> None:
        self.name = name
        self.module = module
        self.class_name = class_name
        self._kit: object | None = None

    @property
    def kit(self) -> object:
        """The action kit, built once."""
        if self._kit is None:
            self._kit = getattr(importlib.import_module(self.module), self.class_name)()
        return self._kit

    @property
    def tool(self) -> object | None:
        """The kit's live tool for this action; none when the kit has no such tool or marks it ``@noCatalog``."""
        tools = self.kit.tools
        tool = tools[self.name] if self.name in tools else None
        if tool is None or NoCatalog.marks(getattr(tool, "callable", tool)):
            return None
        return tool

    @property
    def source_dir(self) -> Path:
        """The kit's folder under ``cdd_guidance/actions``."""
        return Path(inspect.getfile(type(self.kit))).resolve().parent

    @property
    def href(self) -> str:
        return f"actions/{self.name}.html"

    @property
    def request_toolset(self) -> str:
        """The kit as a run request names it, by the module's full name so the run loads it only once, such as
        ``cdd_guidance.actions.generate.generate:Generate``."""
        return f"{self.module}:{self.class_name}"


# Every lifecycle action, in the order the catalog lists them. createRule is an action of the Validate kit.
LIFECYCLE_ACTIONS: tuple[LifecycleAction, ...] = (
    LifecycleAction("partition", "cdd_guidance.actions.partition.partition", "Partition"),
    LifecycleAction("grill", "cdd_guidance.actions.grill_context.grill_context", "GrillContext"),
    LifecycleAction("sketch", "cdd_guidance.actions.sketch.sketch", "Sketch"),
    LifecycleAction("generate", "cdd_guidance.actions.generate.generate", "Generate"),
    LifecycleAction("document", "cdd_guidance.actions.document.document", "Document"),
    LifecycleAction("iterate", "cdd_guidance.actions.iterate.iterate", "Iterate"),
    LifecycleAction("validate", "cdd_guidance.actions.validate.validate", "Validate"),
    LifecycleAction("satisfy", "cdd_guidance.actions.satisfy.satisfy", "Satisfy"),
    LifecycleAction("repair", "cdd_guidance.actions.improvement.improvement", "Improvement"),
    LifecycleAction("createRule", "cdd_guidance.actions.validate.validate", "Validate"),
)

# The actions a run request routes through their kit, with the practice passed as the ``guidance`` argument.
_ACTIONS_TAKING_GUIDANCE = frozenset({"generate", "validate", "satisfy", "document"})


def resolve_lifecycle_actions() -> list[LifecycleAction]:
    """The lifecycle actions whose kit has a live tool for them that the catalog shows."""
    return [action for action in LIFECYCLE_ACTIONS if action.tool is not None]


def _declared_parameters(fn: object) -> dict[str, str]:
    """Named parameters (minus ``self`` and ``*args`` / ``**kwargs``) with their annotation text.

    The toolset manifest carries kind / instructions only, so parameters come
    from the live Python signature. A property or other non-callable declares none.
    """
    if not callable(fn):
        return {}
    try:
        params = inspect.signature(fn).parameters
    except (TypeError, ValueError):
        return {}
    declared: dict[str, str] = {}
    for name, param in params.items():
        if name == "self" or param.kind in (param.VAR_POSITIONAL, param.VAR_KEYWORD):
            continue
        annotation = param.annotation
        if annotation is inspect.Parameter.empty:
            declared[name] = ""
        elif isinstance(annotation, str):
            declared[name] = annotation
        else:
            declared[name] = getattr(annotation, "__name__", str(annotation))
    return declared


def _example_value(name: str, type_str: str) -> object:
    """A placeholder for one parameter in a run request: none for an optional one, an empty list for a list."""
    compact = type_str.replace(" ", "")
    if compact.endswith("|None") or compact == "None":
        return None
    if compact.startswith("list["):
        return []
    return f"<{name}>"


def _is_guidance_class(cls: type) -> bool:
    from harness.guidance.guidance import Guidance

    return isinstance(cls, type) and issubclass(cls, Guidance)


def _kit_taking_guidance(action: str) -> LifecycleAction | None:
    return next(
        (kit for kit in LIFECYCLE_ACTIONS if kit.name == action and action in _ACTIONS_TAKING_GUIDANCE),
        None,
    )


def build_run_request(
    cls: type,
    *,
    action: str,
    fidelity: str | None = None,
) -> dict:
    """Build a spec run-request dict from the live toolset.

    Constructor parameters become ``context``; the named action's parameters
    become ``arguments``. ``fidelity`` (when the constructor accepts it) is
    filled with the given fidelity key.

    Guidance (practices) do not own generate / validate / satisfy / document —
    those live on the action kits. A request for one of those actions on a
    Guidance class is rewritten to the kit with ``arguments.guidance`` carrying
    that Guidance.
    """

    def _context() -> dict[str, object]:
        context: dict[str, object] = {}
        for name, type_str in _declared_parameters(cls.__init__).items():
            if name == "fidelity" and fidelity is not None:
                context[name] = fidelity
            else:
                context[name] = _example_value(name, type_str)
        return context

    kit = _kit_taking_guidance(action)
    if kit is not None and _is_guidance_class(cls):
        return {
            "toolset": kit.request_toolset,
            "action": action,
            "arguments": {
                "guidance": [
                    {"toolset": f"{cls.__module__}:{cls.__name__}", "context": _context()},
                ]
            },
        }

    action_fn = inspect.getattr_static(cls, action, None)
    if isinstance(action_fn, (staticmethod, classmethod)):
        action_fn = action_fn.__func__
    action_params = _declared_parameters(action_fn)

    request: dict[str, object] = {
        "toolset": f"{cls.__module__}:{cls.__name__}",
        "context": _context(),
        "action": action,
    }
    if action_params:
        request["arguments"] = {
            name: _example_value(name, type_str)
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
# Each renderer below is built once with what every page shares (the repository
# citation, the action page links) and exposes one operation, generate_catalog,
# which renders the live object it is given: a LifecycleAction, a CatalogPractice
# and one of its fidelities, or a utility's RegistryEntry. Nothing is copied into
# the renderer between pages, so a page shows exactly what its object holds.
# See catalog/cdd-catalog-sketch.md's Clean Engineering pass for the model.

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
    """The four-fixed-section rendering of one lifecycle action - Tools/actions
    called, Markdown instructions, Module overview - used for every
    lifecycle-action detail page."""

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

    def _calls_section(self, action: LifecycleAction) -> str:
        tools = list(getattr(action.tool, "signature_entry", {}).get("tools", []))
        if not tools:
            return "<p>Calls nothing else directly.</p>"
        items = []
        for name in tools:
            href = self.action_page_hrefs.get(name)
            if href:
                items.append(f'<li><a href="{href}">{name}</a></li>')
            else:
                items.append(self.catalog_tool.generate_catalog(name, action.kit))
        return "<ul>" + "".join(items) + "</ul>"

    def _guide_section(self, action: LifecycleAction) -> str:
        from harness.catalog_generator.foundry_chrome import markdown_to_html

        # Prefer ``{action}.md`` when two lifecycle actions share a kit folder
        # (validate and createRule both live under actions/validate/).
        source_dir = action.source_dir
        for guide_path in (source_dir / f"{action.name}.md", source_dir / f"{source_dir.name}.md"):
            if guide_path.is_file():
                return markdown_to_html(guide_path.read_text(encoding="utf-8"))
        return "<p>No dedicated guide - see module overview below.</p>"

    def _overview_section(self, action: LifecycleAction) -> str:
        from harness.catalog_generator.foundry_chrome import markdown_to_html

        overview_path = action.source_dir / ".context" / "module-context.md"
        if not overview_path.is_file():
            return "<p>No module-context.md yet.</p>"
        return markdown_to_html(overview_path.read_text(encoding="utf-8"))

    def generate_catalog(self, action: LifecycleAction) -> str:
        """Render one action detail body — fidelity-style dark callouts.

        Guide and ``.context/module-context.md`` render as HTML (same as fidelity
        guidance). No source-code dump.
        Page shell (board + skill-detail wrap) is applied by ``Catalog``.
        """
        import html as html_mod

        name = action.name
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
            f"{self._calls_section(action)}"
            f"</section>\n"
            f'<section class="install-block fidelity-guidance action-section" '
            f'aria-label="Markdown instructions">'
            f"<h2>Markdown instructions</h2>"
            f"{self._guide_section(action)}"
            f"</section>\n"
            f'<section class="install-block fidelity-guidance action-section" '
            f'aria-label="Module overview">'
            f"<h2>Module overview</h2>"
            f"{self._overview_section(action)}"
            f"</section>\n"
        )


class FidelityTemplate:
    """The template file a fidelity page shows for the fidelity's default format: a template named for the practice,
    else the best match in the practice's ``templates`` folder by name, front matter, stage, and format folder."""

    _NOT_TEMPLATE_SUFFIXES = frozenset({".png", ".jpg", ".jpeg", ".gif", ".webp", ".pdf", ".trap"})

    def __init__(self, fidelity: FidelityGuidance) -> None:
        self.fidelity = fidelity
        self.module_dir = Path(fidelity.practice_guidance.module_dir).resolve()
        self.templates_root = self.module_dir / "templates"
        self._format = Format(fidelity.default_format)
        self._column = STAGE_COLUMNS.of(fidelity.stage)

    @property
    def path(self) -> Path | None:
        if not self.fidelity.default_format or not self.templates_root.is_dir():
            return None
        named = self._named_template_file()
        if named is not None:
            return named
        scored = self._scored_templates()
        if scored:
            scored.sort(key=lambda pair: (-pair[0], len(pair[1].parts), pair[1].as_posix()))
            return scored[0][1].resolve()
        return self._fallback_root_template()

    @property
    def relative_path(self) -> str:
        """The template's path inside its practice folder."""
        path = self.path
        try:
            return path.relative_to(self.module_dir).as_posix()
        except ValueError as error:
            logging.debug("Template %s is outside %s: %s", path, self.module_dir, error)
            return path.name

    @property
    def body(self) -> str:
        try:
            return self.path.read_text(encoding="utf-8")
        except OSError as error:
            logging.debug("Could not read template %s: %s", self.path, error)
            return ""

    @property
    def language(self) -> str:
        """The code-fence language the template's text is shown in."""
        path = self.path
        if path.name.endswith(".py.tpl"):
            return "python"
        lang = path.suffix.lstrip(".") or "text"
        return {"md": "markdown", "tpl": "text"}.get(lang, lang)

    def _format_aliases(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys((self._format.short, self._format.name)))

    def _named_template_file(self) -> Path | None:
        ext = self._format.template_extension
        for slug in Name(self.fidelity.practice_guidance.key).spellings:
            for stem in (f"{slug}-templates", f"{slug}-template"):
                found = self._named_stem_path(stem, ext)
                if found is not None:
                    return found
        return None

    def _named_stem_path(self, stem: str, ext: str) -> Path | None:
        if ext:
            preferred = self.templates_root / f"{stem}{ext}"
            if preferred.is_file():
                return preferred.resolve()
        for path in sorted(self.templates_root.glob(f"{stem}.*")):
            return path.resolve()
        return None

    def _search_roots(self) -> list[Path]:
        root = self.templates_root
        roots = [root / alias for alias in self._format_aliases() if (root / alias).is_dir()]
        return roots or [root]

    def _candidate_template_paths(self) -> list[Path]:
        return [path for root in self._search_roots() for path in root.rglob("*") if self._is_template_candidate(path)]

    def _is_template_candidate(self, path: Path) -> bool:
        if not path.is_file():
            return False
        if "sketch" in path.name.lower() or "components" in path.parts or ".codeql" in path.parts:
            return False
        return path.suffix.lower() not in self._NOT_TEMPLATE_SUFFIXES

    def _scored_templates(self) -> list[tuple[int, Path]]:
        scored = [(self._template_score(path), path) for path in self._candidate_template_paths()]
        return [(score, path) for score, path in scored if score > 0]

    def _template_score(self, path: Path) -> int:
        fidelity = self.fidelity.name
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
        except (OSError, UnicodeDecodeError):
            return set()
        if not text:
            return set()
        return TemplateFrontmatter().tokens(text)

    def _stage_tokens(self) -> set[str]:
        """The words a template's front matter uses for the fidelity's stage."""
        return set(self._column.template_tokens) if self._column is not None else set()

    def _fallback_root_template(self) -> Path | None:
        ext = self._format.template_extension
        aliases = self._format_aliases()
        root_files = [
            path for path in self.templates_root.iterdir()
            if path.is_file() and "sketch" not in path.name.lower()
            and (not ext or path.suffix == ext or path.suffix.lstrip(".") in aliases)
        ]
        if len(root_files) == 1:
            return root_files[0].resolve()
        fidelity_kebab = self.fidelity.name.replace("_", "-")
        named = [
            path for path in root_files
            if fidelity_kebab in path.stem.replace("_", "-").lower()
            or self.fidelity.name.lower() in path.stem.lower()
        ]
        if named:
            return sorted(named)[0].resolve()
        return None


class CatalogFidelity:
    """The page body for one fidelity of one practice: the chat invoke line, the fidelity's guidance, its default
    template, and its illustrated example."""

    def __init__(
        self,
        repo_url: str,
        ref: str,
        catalog_action: CatalogAction,
        lifecycle_actions: list[LifecycleAction],
    ) -> None:
        self.repo_url = repo_url
        self.ref = ref
        self.catalog_action = catalog_action
        self.lifecycle_actions = lifecycle_actions

    def _quick_invoke(self, practice: CatalogPractice, fidelity: FidelityGuidance) -> str:
        """Invoke block — Foundry install-block chrome, sits under the board."""
        skill_name = practice.skill_name
        action_links = ", ".join(
            f'<a href="../{action.href}">{action.name}</a>' for action in self.lifecycle_actions
        )
        return (
            f'<section class="install-block fidelity-invoke" aria-labelledby="fidelity-invoke-heading">'
            f'<h2 id="fidelity-invoke-heading">Chat invoke</h2>'
            f'<pre class="install-snippet"><code>/{skill_name} &lt;action&gt; {fidelity.name}'
            f" — e.g. /{skill_name} generate {fidelity.name}</code></pre>"
            f'<p class="install-hint">&lt;action&gt; is one of: {action_links}</p>'
            f"</section>"
        )

    def _illustrated_example_panel(self) -> str:
        return (
            '<section class="skill-cr-single illustrated-example">'
            "<h2>Illustrated example</h2>"
            "<p>No illustrated example configured yet.</p></section>"
        )

    def _default_template_panel(self, fidelity: FidelityGuidance) -> str:
        """Default-format template callout — sits above the illustrated example."""
        import html as html_mod

        from harness.catalog_generator.foundry_chrome import fence

        default_format = fidelity.default_format
        template = FidelityTemplate(fidelity)
        path = template.path
        if path is None or not path.is_file():
            fmt = html_mod.escape(default_format or "unknown")
            return (
                '<section class="install-block fidelity-template" aria-label="Default template">'
                "<h2>Default template</h2>"
                f"<p>No template file for default format <code>{fmt}</code>.</p>"
                "</section>"
            )
        blob = GitCitation(self.repo_url, self.ref).blob_url(path)
        return (
            f'<section class="install-block fidelity-template" aria-label="Default template">'
            f"<h2>Default template</h2>"
            f'<p class="install-hint">Default format: <code>{html_mod.escape(default_format or "")}</code>'
            f' — <a href="{html_mod.escape(blob)}">{html_mod.escape(template.relative_path)}</a></p>'
            f"{fence(template.language, template.body)}"
            f"</section>"
        )

    def _guidance_preview(self, fidelity: FidelityGuidance, label: str) -> str:
        from harness.catalog_generator.foundry_chrome import (
            catalog_examples_html,
            markdown_to_html,
            wrap_guidance_body,
        )

        section = fidelity.section
        fid_md = f"## {label}\n\n{section}" if section else section
        examples = catalog_examples_html(fidelity)
        preview = wrap_guidance_body(markdown_to_html(fid_md))
        if examples:
            preview = _insert_after_heading(preview, "Overview", examples)
        return preview

    def generate_catalog(self, practice: CatalogPractice, fidelity: FidelityGuidance) -> str:
        """Render everything under the board: title, invoke, guidance, template, example.

        Uses Foundry install-block chrome for invoke + guidance + default template
        (dark callout, orange links) — not the white skill-md-preview card.
        """
        import html as html_mod

        from harness.catalog_generator.foundry_chrome import display_label

        label = display_label(fidelity.name)
        return (
            f'<header class="page-hero--detail fidelity-detail-header">'
            f'<p class="s-name">{html_mod.escape(practice.display_name)} · fidelity</p>'
            f'<h1 class="page-headline">{html_mod.escape(label)}</h1>'
            f"</header>\n"
            f"{self._quick_invoke(practice, fidelity)}\n"
            f'<section class="install-block fidelity-guidance" '
            f'data-fidelity="{html_mod.escape(fidelity.name)}" '
            f'aria-label="Fidelity guidance">'
            f"{self._guidance_preview(fidelity, label)}</section>\n"
            f"{self._default_template_panel(fidelity)}\n"
            f"{self._illustrated_example_panel()}\n"
        )


class CatalogContextTool:
    """The practice page for one catalog practice: its shared sections and a link to each fidelity page."""

    def __init__(self, repo_url: str, ref: str, catalog_fidelity: CatalogFidelity) -> None:
        self.repo_url = repo_url
        self.ref = ref
        self.catalog_fidelity = catalog_fidelity

    def generate_catalog(self, practice: CatalogPractice) -> str:
        """Render one practice page the way a fidelity page is rendered.

        Shared practice sections (overview, guidance, shared rules, and any
        other practice-level heading) sit in the guidance block. Fidelity
        pages are linked, not inlined.
        """
        import html as html_mod

        from harness.catalog_generator.foundry_chrome import markdown_to_html, wrap_guidance_body

        shared_html = wrap_guidance_body(markdown_to_html(practice.shared_markdown))
        guidance = (
            f'<section class="install-block fidelity-guidance" aria-label="Practice guidance">'
            f"{shared_html}</section>\n"
            if shared_html.strip()
            else ""
        )
        return (
            f'<header class="page-hero--detail fidelity-detail-header">'
            f'<p class="s-name">Practice</p>'
            f'<h1 class="page-headline">{html_mod.escape(practice.display_name)}</h1>'
            f"</header>\n"
            f"{guidance}"
            f"{self._fidelity_section(practice)}"
        )

    def _fidelity_section(self, practice: CatalogPractice) -> str:
        rows = [self._fidelity_row(practice, fidelity) for fidelity in practice.fidelities]
        if not rows:
            return ""
        return (
            '<section class="install-block" aria-label="Fidelities">'
            "<h2>Fidelities</h2>"
            f'<div class="practice-fidelities">{"".join(rows)}</div>'
            "</section>\n"
        )

    def _fidelity_row(self, practice: CatalogPractice, fidelity: FidelityGuidance) -> str:
        import html as html_mod

        from harness.catalog_generator.foundry_chrome import catalog_examples_html, display_label, markdown_to_html

        opening = _first_prose_paragraph(fidelity.overview or fidelity.section)
        opening_html = markdown_to_html(opening) if opening else ""
        return (
            '<div class="practice-fidelity">'
            f'<h3 class="practice-fidelity__title">'
            f'<a href="../{html_mod.escape(practice.fidelity_href(fidelity))}">'
            f"{html_mod.escape(display_label(fidelity.name))}</a></h3>"
            f'<div class="practice-fidelity__opening">{opening_html}</div>'
            f"{catalog_examples_html(fidelity)}"
            "</div>"
        )


class CatalogUtility:
    """The utility-row detail page for one plain-utility ``Toolset``."""

    def __init__(self, repo_url: str, ref: str, catalog_tool: CatalogTool, catalog_action: CatalogAction) -> None:
        self.repo_url = repo_url
        self.ref = ref
        self.catalog_tool = catalog_tool
        self.catalog_action = catalog_action

    def generate_catalog(self, utility: RegistryEntry) -> str:
        """Render one utility page body — fidelity-style dark callouts."""
        import html as html_mod

        from harness.catalog_generator.foundry_chrome import markdown_to_html

        owner = utility.owner
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
            f'<h1 class="page-headline">{html_mod.escape(utility.name)}</h1>'
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


class CatalogPageNotRendered(Exception):
    """A catalog page could not be rendered from its guidance; the message names the page."""


class CatalogNotGenerated(Exception):
    """A project's own catalog generator failed; the message names the project and what the generator reported."""


# A whole catalog renders in seconds; a run this long has hung, and it would hold an MCP thread until it is stopped.
CATALOG_GENERATION_TIMEOUT_SECONDS = 600
_CATALOG_GENERATOR_MODULE = "harness.catalog_generator.generate_cdd_catalog"
_CATALOG_GENERATOR_FILE = Path("harness", "catalog_generator", "generate_cdd_catalog.py")
# The folders a CDD checkout imports its guidance from, as its specs and its own catalog generator put them on the path.
_CDD_IMPORT_FOLDERS = (
    ".", "tools", "cdd_guidance", "cdd_guidance/practices", "cdd_guidance/actions",
    "cdd_guidance/builders", "cdd_guidance/patterns",
)


class CatalogProject:
    """The project a catalog is generated for: the folder its pages go into and the checkout whose guidance they show.

    A CDD checkout, such as a branch worktree, shows its own guidance in its own ``cdd_guidance/catalog``, so a branch's
    catalog shows that branch's practices and actions. Any other project shows the guidance the CDD tools serving it
    give its agents, written into the project's ``catalog`` folder beside the project's own approach slide."""

    def __init__(self, root: Path | str) -> None:
        self.root = Path(root).resolve()

    @property
    def is_cdd_checkout(self) -> bool:
        return (self.root / _CATALOG_GENERATOR_FILE).is_file()

    @property
    def is_serving_checkout(self) -> bool:
        """Whether this project is the checkout this code was imported from, whose guidance is already loaded."""
        return os.path.normcase(self.root) == os.path.normcase(_REPO_ROOT)

    @property
    def shows_own_guidance(self) -> bool:
        """Whether the catalog must be generated by the project's own code, because it is a CDD checkout whose
        guidance can differ from the guidance loaded here."""
        return self.is_cdd_checkout and not self.is_serving_checkout

    @property
    def catalog_folder(self) -> Path:
        if self.is_cdd_checkout:
            return self.root / "cdd_guidance" / "catalog"
        return self.root / "catalog"

    def generate_with_own_guidance(self, out_root: Path, brand: str) -> str:
        """Run the project's own catalog generator, so every page is read from the project's guidance and code."""
        try:
            finished = subprocess.run(
                self._generator_command(out_root, brand),
                cwd=self.root,
                env=self._generator_environment(),
                capture_output=True,
                text=True,
                encoding="utf-8",
                timeout=CATALOG_GENERATION_TIMEOUT_SECONDS,
                check=True,
            )
        except subprocess.CalledProcessError as failure:
            raise CatalogNotGenerated(
                f"The catalog generator in {self.root} failed: {failure.stderr.strip() or failure.stdout.strip()}"
            ) from failure
        except subprocess.TimeoutExpired as failure:
            raise CatalogNotGenerated(
                f"The catalog generator in {self.root} did not finish in {CATALOG_GENERATION_TIMEOUT_SECONDS} seconds"
            ) from failure
        return finished.stdout.strip()

    def _generator_command(self, out_root: Path, brand: str) -> list[str]:
        command = [sys.executable, "-m", _CATALOG_GENERATOR_MODULE, "--out", str(out_root)]
        return command + ["--brand", brand] if brand else command

    def _generator_environment(self) -> dict[str, str]:
        """Import path and project for the generator: only the project's folders, so no module is read from the
        checkout serving these tools."""
        environment = dict(os.environ)
        environment["PYTHONPATH"] = os.pathsep.join(str(self.root / folder) for folder in _CDD_IMPORT_FOLDERS)
        environment["PYTHONIOENCODING"] = "utf-8"
        environment["CDD_PROJECT"] = str(self.root)
        return environment


@agent_toolset
class Catalog:
    """The top-level entry point - the only class ``generate_cdd_catalog.py``
    calls. Owns the shared portability config and the practices, lifecycle
    actions, and utilities it renders. Always copies Foundry commons into ``out_root``."""

    def __init__(
        self,
        repo_url: str = "",
        ref: str = "",
        out_root: str = "",
        brands_root: str | Path | None = None,
        catalog_context_tool: CatalogContextTool | None = None,
        catalog_action: CatalogAction | None = None,
        catalog_utility: CatalogUtility | None = None,
        approach_md_path: str | Path | None = None,
    ) -> None:
        citation = GitCitation.from_checkout()
        self.repo_url = repo_url or citation.repo_url
        self.ref = ref or citation.ref
        self._named_out_root = Path(out_root) if out_root else None
        from harness.catalog_generator.approach_copy import APPROACH_MARKDOWN

        self.approach_md_path = (
            Path(approach_md_path) if approach_md_path is not None else APPROACH_MARKDOWN
        )
        self.brand = None
        from harness.catalog_generator.foundry_chrome import Brand

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
        self._practices: list[CatalogPractice] | None = None
        self._utilities: list[RegistryEntry] | None = None
        self._lifecycle_actions: list[LifecycleAction] | None = None
        self._loaded_approach_copy = None
        self._tool_bodies: list[str] = []
        self._action_bodies: list[str] = []
        self._utility_bodies: list[str] = []
        self.pages: dict[str, str] = {}

    def _wire_catalog_renderers(self) -> tuple[CatalogContextTool, CatalogAction, CatalogUtility]:
        lifecycle_actions = resolve_lifecycle_actions()
        catalog_tool = CatalogTool(self.repo_url, self.ref)
        hrefs = {action.name: action.href for action in lifecycle_actions}
        catalog_action = CatalogAction(self.repo_url, self.ref, catalog_tool, hrefs)
        catalog_fidelity = CatalogFidelity(
            self.repo_url, self.ref, catalog_action, lifecycle_actions
        )
        catalog_context_tool = CatalogContextTool(self.repo_url, self.ref, catalog_fidelity)
        catalog_utility = CatalogUtility(self.repo_url, self.ref, catalog_tool, catalog_action)
        return catalog_context_tool, catalog_action, catalog_utility

    @property
    def project(self) -> CatalogProject:
        """The project the running call acts on; one server answers every chat, so it is read for each call."""
        return CatalogProject(project_checkout())

    @property
    def out_root(self) -> Path:
        """The folder every page is written under: the one the caller named, else the project's catalog folder."""
        return self._named_out_root or self.project.catalog_folder

    @property
    def practices(self) -> list[CatalogPractice]:
        """The practices the catalog renders, loaded on first use."""
        if self._practices is None:
            self._practices = catalog_practices()
        return self._practices

    @property
    def utilities(self) -> list[RegistryEntry]:
        if self._utilities is None:
            self._utilities = catalog_utilities()
        return self._utilities

    @property
    def lifecycle_actions(self) -> list[LifecycleAction]:
        if self._lifecycle_actions is None:
            self._lifecycle_actions = resolve_lifecycle_actions()
        return self._lifecycle_actions

    @classmethod
    def from_registry(cls, guidance: Iterable[Any] | None = None) -> Catalog:
        catalog = cls()
        for item in list(guidance or ()):
            catalog.add_guidance(item)
        return catalog

    def add_guidance(self, guidance: Any) -> None:
        from harness.markdown import HTML, Markdown

        if NoCatalog.marks(guidance):
            return
        slug = getattr(guidance, "context_index_key", None) or type(guidance).__name__
        for label in ("context", "guidance", "examples"):
            try:
                page = Markdown.from_label(guidance, "overview" if label == "context" else label).html()
            except Exception as error:
                raise CatalogPageNotRendered(f"Catalog page {slug}-{label} could not be rendered: {error}") from error
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
        """Render the whole catalog for the project being worked on, with Foundry chrome.
        Pages go into ``out_root``: the project's ``cdd_guidance/catalog`` when
        the project is a CDD checkout, else its ``catalog`` folder. A CDD
        checkout's catalog shows that checkout's own guidance; any other
        project's shows the guidance these tools give it. No output is ever
        written outside ``out_root``.
        ``brand`` is a collection name under the brands folder, or a path to a
        brand folder; empty uses bundled abd-works."""
        from harness.catalog_generator.foundry_chrome import Brand

        if self.pages:
            root = Path(brand) if brand else self.out_root
            self._write_guidance_html_pages(root)
            return f"Wrote {len(self.pages)} guidance pages into {root}"
        project = self.project
        if project.shows_own_guidance:
            return project.generate_with_own_guidance(self.out_root, str(brand))
        self.brand = Brand(collection=self.brands_root).resolve(str(brand)) if brand else None
        self._render_catalog()
        return f"Catalog regenerated into {self.out_root} using {self.repo_url}@{self.ref}"

    @property
    def brands(self) -> dict[str, Path]:
        from harness.catalog_generator.foundry_chrome import Brand

        return Brand(collection=self.brands_root).folders()

    @mcp
    @skill
    @agent_tool
    def apply_brand(self, name: str) -> str:
        """Overlay a named brand from the catalog brands collection onto the
        generated catalog commons without regenerating pages. ``name`` is a
        folder name under the brands collection, or a path to a brand folder.
        Bundled ``abd-works`` is always available."""
        from harness.catalog_generator.foundry_chrome import Brand

        if not name:
            return f"Known brands: {', '.join(sorted(self.brands))}"
        dest = Brand(collection=self.brands_root).apply_named(self.out_root, name)
        self.brand = dest
        return f"Applied brand {name} under {dest}"

    @mcp
    @skill
    @agent_tool
    def generate_project_approach(
        self,
        project_root: str,
        out_root: str = "",
        project_title: str = "",
        repo_url: str = "",
        examples_json: str = "",
    ) -> str:
        """Render ``cdd-approach.html`` for a project using mapped example artifacts.

        ``project_root`` is the project checkout. ``out_root`` defaults to
        ``{project_root}/catalog``. ``examples_json`` is optional JSON mapping
        practice → stage → relative path; when blank, use
        ``.context/project-approach-examples.json`` and auto-discovery."""
        from harness.catalog_generator.project_approach import (
            ProjectApproach,
            merge_example_sources,
            save_examples_manifest,
        )

        root = Path(project_root).resolve()
        destination = Path(out_root).resolve() if out_root else root / "catalog"
        merged = merge_example_sources(root)
        if examples_json.strip():
            payload = __import__("json").loads(examples_json)
            for practice, stages in (payload.get("examples") or payload).items():
                if not isinstance(stages, dict):
                    continue
                for stage, relative in stages.items():
                    merged[(practice, stage)] = (root / str(relative)).resolve()
        save_examples_manifest(
            root,
            merged,
            project_title=project_title,
            repo_url=repo_url,
        )
        approach = ProjectApproach(
            project_root=root,
            project_title=project_title or root.name.replace("-", " ").title(),
            repo_url=repo_url or self.repo_url,
            examples=merged,
        )
        return approach.generate(destination, brands_root=self.brands_root)

    @mcp
    @skill
    @agent_instructions
    def configure_project_approach(
        self,
        project_root: str,
        example_paths: list[str] | None = None,
        out_root: str = "",
    ) -> str:
        """Build a project-specific ``cdd-approach.html`` slide from example artifacts.

        project_root={project_root}
        out_root={out_root or '{project_root}/catalog'}
        example_paths={example_paths or 'discover from project tree'}

        Each example lands under one practice and one stage on the approach page.
        Use the same layout as ``catalog/cdd-approach.html``.

        **Where each example goes**

        | Practice | Discovery | Specification | Implementation |
        | --- | --- | --- | --- |
        | stories | story map | scenarios | acceptance tests |
        | ddd | bounded context map | domain model | tactics code |
        | ux | information architecture | mockup | front-end code |
        | clean_engineering | modules | model | code |
        | bdd | behavior specs | realization | development tests |

        **Step 1 — Collect examples**

        Read every path in ``example_paths``. When the list is empty,
        ``generate_project_approach`` walks the project tree itself.

        **Step 2 — Classify each file**

        A file belongs to the fidelity whose declared outputs name it: the
        same file names and patterns the session uses to find a fidelity's
        files, such as ``.context/story-map.drawio`` for the story map or
        ``{{bounded_context}}/{{aggregate}}/{{aggregate}}.ts`` for the domain
        model. ``generate_project_approach`` classifies discovered files this
        way, so classify the listed files the same way. A file no fidelity
        declares has no place until the user names one; ask rather than
        guess from its name.

        **Step 3 — Confirm the mapping**

        Show a short table: practice, stage, relative path. Edit it until
        every practice and stage the user cares about has a file.

        **Step 4 — Generate**

        Build ``examples_json`` from the confirmed mapping:

        ```json
        {{"examples": {{"stories": {{"discovery": "stories/story-map.drawio", ...}}}}}}
        ```

        Call ``generate_project_approach`` with ``project_root``, ``out_root``,
        ``project_title``, ``repo_url``, and ``examples_json``."""
        tools(self.generate_project_approach)
        return "Project approach slide generated."

    def write_page(self, relative_path: str, html: str) -> Path:
        return CatalogPage(self.out_root).write(relative_path, html)

    def write_raw_manifests(self) -> None:
        return None

    def _render_catalog(self) -> None:
        """Write every catalog page under ``self.out_root``."""
        from harness.catalog_generator.foundry_chrome import Brand

        self.out_root.mkdir(parents=True, exist_ok=True)
        Brand(collection=self.brands_root, folder=self.brand).copy_commons(self.out_root)
        self._tool_bodies = []
        self._action_bodies = []
        self._utility_bodies = []
        for practice in self.practices:
            self._write_practice_page(practice)
        for action in self.lifecycle_actions:
            self._write_action_page(action)
        for utility in self.utilities:
            self._write_utility_page(utility)
        self._write_hub()
        self._write_source_docs()
        self._write_workflow()
        self._write_grid_pages()

    def _kanban_embed(
        self,
        highlight_practice: CatalogPractice | None = None,
        highlight_fidelity: FidelityGuidance | None = None,
    ) -> str:
        """The board shown on a detail page one folder below the hub, highlighting the page's practice and fidelity."""
        from harness.catalog_generator.foundry_chrome import render_hub_board

        return render_hub_board(
            self.practices,
            self.lifecycle_actions,
            self.utilities,
            path_prefix="../",
            highlight_practice=highlight_practice,
            highlight_fidelity=highlight_fidelity,
        )

    def _detail_page(self, title: str, body: str, nav_current: str, kanban_embed: str) -> str:
        from harness.catalog_generator.foundry_chrome import page_shell

        return page_shell(
            title=title,
            h1=self._harness_headline(),
            tagline=self._harness_tagline(),
            body_inner=body,
            commons_prefix="../commons/",
            nav_prefix="../",
            nav_current=nav_current,
            show_hero=True,
            body_wrap_class="skill-detail-page",
            kanban_embed=kanban_embed,
        )

    def _write_practice_page(self, practice: CatalogPractice) -> None:
        body = self.catalog_context_tool.generate_catalog(practice)
        self._tool_bodies.append(body)
        page = self._detail_page(
            f"{practice.display_name} — CDD Catalog", body, "context-tools", self._kanban_embed(practice)
        )
        self.write_page(practice.href, page)
        for fidelity in practice.fidelities:
            self._write_fidelity_page(practice, fidelity)

    def _write_fidelity_page(self, practice: CatalogPractice, fidelity: FidelityGuidance) -> None:
        from harness.catalog_generator.foundry_chrome import display_label

        body = self.catalog_context_tool.catalog_fidelity.generate_catalog(practice, fidelity)
        page = self._detail_page(
            f"{display_label(fidelity.name)} — {practice.display_name}",
            body,
            "fidelities",
            self._kanban_embed(practice, fidelity),
        )
        self.write_page(practice.fidelity_href(fidelity), page)

    def _write_action_page(self, action: LifecycleAction) -> None:
        body = self.catalog_action.generate_catalog(action)
        self._action_bodies.append(body)
        page = self._detail_page(f"{action.name} — lifecycle action", body, "actions", self._kanban_embed())
        self.write_page(action.href, page)

    def _write_utility_page(self, utility: RegistryEntry) -> None:
        body = self.catalog_utility.generate_catalog(utility)
        self._utility_bodies.append(body)
        page = self._detail_page(f"{utility.name} — utility", body, "tools", self._kanban_embed())
        self.write_page(utility.href, page)
    def _harness_headline(self) -> str:
        return 'ABD <span class="accent">Context Driven Delivery</span> Harness'

    def _harness_tagline(self) -> str:
        return (
            "Agentic tools that bring the best of agile product, delivery, and engineering practices into the age of AI. "
            f'Get the repo <a href="{self.repo_url}" '
            'target="_blank" rel="noopener noreferrer">here</a>.'
        )

    def _write_hub(self) -> None:
        from harness.catalog_generator.foundry_chrome import page_shell, render_hub_board

        board = render_hub_board(self.practices, self.lifecycle_actions, self.utilities)
        hub = page_shell(
            title="ABD Context Driven Delivery Harness",
            h1=self._harness_headline(),
            tagline=self._harness_tagline(),
            after_tagline=self._hub_doc_links(),
            body_inner=self._hub_body(),
            commons_prefix="commons/",
            nav_prefix="",
            nav_current="hub",
            kanban_embed=board,
        )
        self.write_page("index.html", hub)

    def _hub_doc_links(self) -> str:
        return (
            '<a class="page-hero__approach-btn" href="cdd-approach.html">The approach</a>'
        )

    def _write_source_docs(self) -> None:
        self._write_approach_page()
        self._write_approach_practice_pages()
        self._write_coming_soon_pages()
        self._write_readme_page()

    @property
    def approach_copy(self):
        """The approach page's copy, read from ``approach_md_path`` on first use."""
        from harness.catalog_generator.approach_copy import load_approach_copy

        if self._loaded_approach_copy is None:
            self._loaded_approach_copy = load_approach_copy(self.approach_md_path)
        return self._loaded_approach_copy

    def _write_approach_page(self) -> None:
        from harness.catalog_generator.foundry_chrome import (
            copy_practice_examples,
            page_shell,
            write_stage_example_pages,
        )

        copy_practice_examples(self.out_root)
        example_hrefs = write_stage_example_pages(self.out_root, self.approach_copy.stages)
        page = page_shell(
            title="ABD Context Driven Delivery Harness",
            h1=self._harness_headline(),
            tagline="",
            subhead=self.approach_copy.subhead,
            after_subhead=(
                f'Get the repo <a href="{self.repo_url}" '
                'target="_blank" rel="noopener noreferrer">here</a>.'
            ),
            body_inner=self.approach_page_body(example_hrefs),
            commons_prefix="commons/",
            nav_prefix="",
            nav_current="",
            body_wrap_class="approach-wrap",
        )
        self.write_page("cdd-approach.html", page)

    def _write_coming_soon_pages(self) -> None:
        import html as html_mod

        from harness.catalog_generator.foundry_chrome import page_shell

        for slug, title in (
            ("customer-discovery", "Customer Discovery"),
            ("devops", "DevOps"),
        ):
            body = (
                '<article class="approach-practice">'
                '<p class="approach-practice__back"><a href="cdd-approach.html">← Back to the approach</a></p>'
                f'<h2 class="approach-practice__title">{html_mod.escape(title)}</h2>'
                '<p class="approach-practice__para">Coming soon.</p>'
                "</article>"
            )
            page = page_shell(
                title=f"{title} — ABD Context Driven Delivery",
                h1=f'<span class="accent">{html_mod.escape(title)}</span>',
                tagline="",
                body_inner=body,
                commons_prefix="commons/",
                nav_prefix="",
                nav_current="",
                body_wrap_class="approach-wrap",
            )
            self.write_page(f"{slug}.html", page)

    def _write_approach_practice_pages(self) -> None:
        import html as html_mod

        from harness.catalog_generator.foundry_chrome import page_shell

        from harness.catalog_generator.approach_copy import format_principle_bullet

        for practice in self.approach_copy.practices:
            paras = "".join(
                f'<p class="approach-practice__para">{format_principle_bullet(item)}</p>'
                for item in practice.get("bullets", ())
            )
            caption = practice.get("caption", "")
            if caption:
                paras += f'<p class="approach-practice__para">{caption}</p>'
            body = (
                '<article class="approach-practice">'
                f'<p class="approach-practice__back"><a href="cdd-approach.html">← Back to the approach</a></p>'
                f'<h2 class="approach-practice__title">{html_mod.escape(practice["title"])}</h2>'
                f'<div class="approach-practice__body">{paras}</div>'
                "</article>"
            )
            page = page_shell(
                title=f'{practice["title"]} — ABD Context Driven Delivery',
                h1=f'<span class="accent">{html_mod.escape(practice["title"])}</span>',
                tagline="",
                body_inner=body,
                commons_prefix="commons/",
                nav_prefix="",
                nav_current="",
                body_wrap_class="approach-wrap",
            )
            self.write_page(f'cdd-{practice["slug"]}.html', page)

    def approach_page_body(
        self,
        example_hrefs: dict[str, str] | None = None,
        *,
        example_sources=None,
        catalog_root: str | Path | None = None,
    ) -> str:
        import html as html_mod

        from harness.catalog_generator.approach_copy import (
            format_principle_bullet,
            product_engineering_layout,
            so_what_row,
        )

        copy = self.approach_copy
        resolved_catalog_root = Path(catalog_root) if catalog_root is not None else self.out_root
        stages = copy.stages
        principles = copy.practices
        example_hrefs = example_hrefs or {}

        stage_buttons: list[str] = []
        for index, stage in enumerate(stages):
            items = "".join(
                f'<li class="approach-stage__item kb-ticket aad-skill aad-fam-{html_mod.escape(fam)}">'
                f"{html_mod.escape(item)}</li>"
                for item, fam in zip(stage["items"], stage["item_fams"])
            )
            shape = (
                '<span class="kb-col-scope-shape-wrap approach-stage__scope">'
                f'<span class="kb-col-scope-shape kb-col-scope-shape--{html_mod.escape(stage["shape"])}" '
                f'aria-label="{html_mod.escape(stage["scope_name"])}. {html_mod.escape(stage["scope_width"])}"></span>'
                '<span class="kb-col-shape-tooltip" role="tooltip">'
                f'<span class="kb-col-shape-tooltip__name">{html_mod.escape(stage["scope_name"])}</span>'
                f'<span class="kb-col-shape-tooltip__width">{html_mod.escape(stage["scope_width"])}</span>'
                "</span></span>"
            )
            active = " is-active" if index == 0 else ""
            label_html = (
                f'<span class="approach-stage__label">{html_mod.escape(stage["label"])}</span>'
            )
            stage_buttons.append(
                f'<div class="approach-stage{active}" role="button" tabindex="0" '
                f'data-stage-index="{index}" data-stage-id="{html_mod.escape(stage["id"])}" '
                f'aria-pressed="{"true" if index == 0 else "false"}">'
                f'<span class="approach-stage__head">'
                f'{shape}'
                f"{label_html}"
                f"</span>"
                f'<ul class="approach-stage__items">{items}</ul>'
                "</div>"
            )

        first = stages[0]
        bullets = "".join(
            f"<li>{html_mod.escape(para)}</li>" for para in first["paras"]
        )
        stage_json = html_mod.escape(
            __import__("json").dumps(
                [
                    {
                        "id": s["id"],
                        "label": s["label"],
                        "detail_title": s["detail_title"],
                        "items": list(s["items"]),
                        "paras": list(s["paras"]),
                        "example_href": example_hrefs.get(s["id"], ""),
                    }
                    for s in stages
                ]
            ),
            quote=True,
        )

        from harness.catalog_generator.foundry_chrome import approach_principle_grid

        principle_kinds = {
            "product-engineering": "descriptions",
            "iterate-and-learn": "windows",
            "code-is-context": "spec",
        }
        principle_cards: list[str] = []
        for number, practice in enumerate(principles, start=1):
            kind = practice.get("kind") or principle_kinds.get(practice["slug"], "tickets")
            grid = approach_principle_grid(
                self.practices,
                kind,
                stages=stages if practice["slug"] == "iterate-and-learn" else None,
                example_sources=example_sources,
                catalog_root=resolved_catalog_root,
            )
            caption = practice.get("caption", "")
            caption_html = (
                f'<aside class="approach-principle__caption"><p class="approach-principle__caption-body">{caption}</p></aside>'
                if caption
                else ""
            )
            bullet_list = list(practice.get("bullets", ()))
            if practice["slug"] == "iterate-and-learn" and bullet_list:
                bullets_html = (
                    '<div class="approach-refine__layout approach-refine__layout--bullets">'
                    '<div class="approach-refine__context" aria-hidden="true"></div>'
                    + so_what_row(bullet_list, modifier="approach-so--stages")
                    + "</div>"
                )
            elif practice["slug"] == "product-engineering" and bullet_list:
                bullets_html = product_engineering_layout(bullet_list)
            else:
                bullet_items = "".join(
                    f"<li>{format_principle_bullet(item)}</li>" for item in bullet_list
                )
                bullets_html = (
                    f'<ul class="approach-principle__bullets">{bullet_items}</ul>' if bullet_items else ""
                )
            principle_cards.append(
                f'<section class="approach-principle" data-principle="{html_mod.escape(practice["slug"])}">'
                f'<button type="button" class="approach-principle__toggle" aria-expanded="false">'
                f'<span class="approach-principle__num" aria-hidden="true">{number}</span>'
                f'<span class="approach-principle__copy">'
                f'<h3 class="approach-principle__title">{html_mod.escape(practice["title"])}</h3>'
                f"</span></button>"
                f'<div class="approach-principle__panel"><div class="approach-principle__panel-inner">{bullets_html}{grid}{caption_html}</div></div>'
                "</section>"
            )

        return (
            '<div class="approach-page" id="approach-page" tabindex="0" '
            f'data-stages="{stage_json}">'
            '<div class="approach-main" id="approach-main">'
            f'<div class="approach-stage-row" role="list">{"".join(stage_buttons)}</div>'
            '<section class="approach-detail" id="approach-detail" aria-live="polite">'
            f'<h2 class="approach-detail__title" id="approach-detail-title">'
            f'{html_mod.escape(first["detail_title"])}</h2>'
            f'<ul class="approach-detail__body" id="approach-detail-body">{bullets}</ul>'
            "</section>"
            "</div>"
            '<aside class="approach-principles" id="approach-principles" aria-labelledby="approach-principles-heading">'
            '<h2 class="approach-principles__title" id="approach-principles-heading">'
            f"{html_mod.escape(copy.principles_heading)}"
            "</h2>"
            f'<div class="approach-principles__list">{"".join(principle_cards)}</div>'
            "</aside>"
            '<section class="approach-library" aria-labelledby="approach-library-heading">'
            '<h2 class="approach-library__title" id="approach-library-heading">'
            f"{html_mod.escape(copy.library_heading)}"
            "</h2>"
            f"{approach_principle_grid(self.practices, 'tickets', example_sources=example_sources, catalog_root=resolved_catalog_root)}"
            "</section>"
            "</div>"
            "<script>(function(){"
            "var root=document.getElementById('approach-page');"
            "if(!root)return;"
            "var stages=[];"
            "try{stages=JSON.parse(root.getAttribute('data-stages')||'[]');}catch(e){return;}"
            "var buttons=[].slice.call(root.querySelectorAll('.approach-stage'));"
            "var titleEl=document.getElementById('approach-detail-title');"
            "var bodyEl=document.getElementById('approach-detail-body');"
            "var principlesEl=document.getElementById('approach-principles');"
            "var principles=[].slice.call(root.querySelectorAll('.approach-principle'));"
            "var principleIndex=-1;"
            "var index=0;"
            "var ready=false;"
            "var started=false;"
            "var onPrinciples=false;"
            "function scrollRefineToTop(){"
            "window.scrollTo({top:0,behavior:'smooth'});"
            "}"
            "function scrollPrinciple(el){"
            "var nav=document.querySelector('.site-nav');"
            "var navH=nav?nav.getBoundingClientRect().height:0;"
            "var pad=navH+16;"
            "var top=el.getBoundingClientRect().top+window.pageYOffset;"
            "var height=el.offsetHeight;"
            "var room=window.innerHeight-pad;"
            "var y=top-pad;"
            "if(height<room)y=top-pad-Math.min(24,room-height);"
            "window.scrollTo({top:Math.max(0,y),behavior:'smooth'});"
            "}"
            "function showPrinciple(i,scroll){"
            "principleIndex=i;"
            "onPrinciples=i>=0;"
            "principles.forEach(function(el,n){"
            "var open=n===i;"
            "el.classList.toggle('is-open',open);"
            "var toggle=el.querySelector('.approach-principle__toggle');"
            "if(toggle)toggle.setAttribute('aria-expanded',open?'true':'false');"
            "});"
            "if(scroll&&i>=0&&principles[i]){"
            "var target=principles[i];"
            "window.setTimeout(function(){scrollPrinciple(target);},440);"
            "}"
            "}"
            "function paint(scroll){"
            "buttons.forEach(function(btn,i){"
            "var on=!onPrinciples&&i===index;"
            "btn.classList.toggle('is-active',on);"
            "btn.classList.remove('is-done');"
            "btn.setAttribute('aria-pressed',on?'true':'false');"
            "if(on){"
            "btn.classList.remove('is-flash');"
            "void btn.offsetWidth;"
            "btn.classList.add('is-flash');"
            "}"
            "});"
            "var stage=stages[index];"
            "if(!stage)return;"
            "titleEl.textContent=stage.detail_title;"
            "showStageExample(stage,scroll&&started);"
            "bodyEl.classList.remove('is-enter');"
            "void bodyEl.offsetWidth;"
            "bodyEl.innerHTML=stage.paras.map(function(para){"
            "return '<li>'+para.replace(/</g,'&lt;')+'</li>';"
            "}).join('');"
            "bodyEl.classList.add('is-enter');"
            "if(scroll&&!onPrinciples&&started&&!(stage.example_href))scrollRefineToTop();"
            "}"
            "function showStageExample(){}"
            "function openNextColumn(){"
            "var host=document.getElementById('approach-stage-examples');"
            "return !!(window.catalogRefineOpenNext&&window.catalogRefineOpenNext(host));"
            "}"
            "function closeLastColumn(){"
            "var host=document.getElementById('approach-stage-examples');"
            "return !!(window.catalogRefineCloseLast&&window.catalogRefineCloseLast(host));"
            "}"
            "function principleSlug(i){"
            "return principles[i]?principles[i].getAttribute('data-principle'):'';"
            "}"
            "var peStep=-1;"
            "function peSteps(){"
            "var steps=[];"
            "document.querySelectorAll('#pe-engineering .approach-refine-row').forEach(function(host){"
            "['discovery','specification','implementation'].forEach(function(id){"
            "if(host.querySelector('.approach-stage-column[data-stage-id=\"'+id+'\"]')){"
            "steps.push({host:host,id:id});"
            "}"
            "});"
            "});"
            "return steps;"
            "}"
            "function walkPe(delta){"
            "if(!window.catalogRefineSetStage)return false;"
            "var steps=peSteps();"
            "if(!steps.length)return false;"
            "if(delta>0){"
            "if(peStep>=steps.length-1)return false;"
            "peStep+=1;"
            "return window.catalogRefineSetStage(steps[peStep].host,steps[peStep].id,true);"
            "}"
            "if(peStep<0)return false;"
            "window.catalogRefineSetStage(steps[peStep].host,steps[peStep].id,false);"
            "peStep-=1;"
            "return true;"
            "}"
            "function move(delta){"
            "started=true;"
            "if(phase==='stages'){"
            "if(delta>0&&index>=stages.length-1){"
            "phase='principles';"
            "closePrinciples();"
            "if(principlesEl){"
            "var nav=document.querySelector('.site-nav');"
            "var navH=nav?nav.getBoundingClientRect().height:0;"
            "var top=principlesEl.getBoundingClientRect().top+window.pageYOffset-(navH+16);"
            "window.scrollTo(0,Math.max(0,top));"
            "}"
            "return;"
            "}"
            "if(delta<0&&index<=0)return;"
            "index+=delta;"
            "closePrinciples();"
            "paint(false);"
            "return;"
            "}"
            "if(phase==='travel'||phase==='library')phase='principles';"
            "if(delta>0){"
            "if(principleIndex<0){showPrinciple(0,false);paint(false);return;}"
            "if(principleSlug(principleIndex)==='iterate-and-learn'&&openNextColumn())return;"
            "if(principleSlug(principleIndex)==='product-engineering'&&walkPe(1))return;"
            "if(principleIndex>=principles.length-1)return;"
            "showPrinciple(principleIndex+1,false);"
            "if(principleSlug(principleIndex)==='product-engineering')peStep=-1;"
            "paint(false);"
            "return;"
            "}"
            "if(principleSlug(principleIndex)==='product-engineering'&&walkPe(-1))return;"
            "if(principleSlug(principleIndex)==='iterate-and-learn'&&closeLastColumn())return;"
            "if(principleIndex>0){showPrinciple(principleIndex-1,false);paint(false);return;}"
            "if(principleIndex===0){closePrinciples();paint(false);return;}"
            "phase='stages';"
            "index=stages.length-1;"
            "paint(false);"
            "}"
            "buttons.forEach(function(btn,i){"
            "btn.addEventListener('click',function(e){"
            "if(e.target.closest&&e.target.closest('a'))return;"
            "started=true;"
            "phase='stages';"
            "index=i;"
            "if(!stages[i]||!stages[i].example_href)showPrinciple(-1,false);"
            "paint(ready);"
            "});"
            "btn.addEventListener('keydown',function(e){"
            "if(e.target!==btn)return;"
            "if(e.key==='Enter'||e.key===' '){e.preventDefault();btn.click();}"
            "});"
            "});"
            "principles.forEach(function(el,i){"
            "var toggle=el.querySelector('.approach-principle__toggle');"
            "if(!toggle)return;"
            "toggle.addEventListener('click',function(){"
            "started=true;"
            "phase='principles';"
            "if(principleIndex===i){showPrinciple(-1,false);paint(false);return;}"
            "showPrinciple(i,false);"
            "if(principleSlug(i)==='product-engineering')peStep=-1;"
            "paint(false);"
            "});"
            "});"
            "document.addEventListener('keydown',function(e){"
            "if(e.target.closest('input,textarea,select,a'))return;"
            "if(e.key==='ArrowRight'||e.key==='ArrowDown'){e.preventDefault();move(1);}"
            "else if(e.key==='ArrowLeft'||e.key==='ArrowUp'){e.preventDefault();move(-1);}"
            "});"
            "var phase='stages';"
            "var dragClip=null,dragX=0,dragLeft=0;"
            "document.addEventListener('pointerdown',function(e){"
            "var clip=e.target.closest&&e.target.closest('.approach-stage-examples__clip');"
            "if(!clip||e.button!==0)return;"
            "if(e.target.closest('button,a,input,textarea,select,.catalog-monaco,.mxgraph,.skill-drawio-wrap'))return;"
            "dragClip=clip;dragX=e.clientX;dragLeft=clip.scrollLeft;"
            "clip.classList.add('is-dragging');"
            "try{clip.setPointerCapture(e.pointerId);}catch(err){}"
            "});"
            "document.addEventListener('pointermove',function(e){"
            "if(!dragClip)return;"
            "dragClip.scrollLeft=dragLeft-(e.clientX-dragX);"
            "});"
            "document.addEventListener('pointerup',function(){"
            "if(!dragClip)return;"
            "dragClip.classList.remove('is-dragging');"
            "dragClip=null;"
            "});"
            "function closePrinciples(){"
            "showPrinciple(-1,false);"
            "}"
            "paint(false);"
            "ready=true;"
            "})();</script>"
        )

    def _write_readme_page(self) -> None:
        from harness.catalog_generator.foundry_chrome import markdown_to_html, page_shell

        source = _REPO_ROOT / "README.md"
        if not source.is_file():
            return
        raw = source.read_text(encoding="utf-8")
        body_md = re.sub(r"^#\s+.*\n+", "", raw.lstrip(), count=1, flags=re.MULTILINE)
        page = page_shell(
            title="README — ABD Context Driven Delivery Harness",
            h1="README",
            tagline=(
                "Agentic tools that bring the best of agile product, delivery, and engineering practices into the age of AI. "
                '<a href="index.html">Back to catalog</a>.'
            ),
            body_inner=f'<article class="catalog-source-doc">{markdown_to_html(body_md)}</article>',
            commons_prefix="commons/",
            nav_prefix="",
            nav_current="",
        )
        self.write_page("readme.html", page)

    def _hub_body(self) -> str:
        import html as html_mod

        harness_href = GitCitation(self.repo_url, self.ref).blob_url(
            _REPO_ROOT / "harness" / "harness" / "harness.py",
        )
        return (
            '<section class="install-block catalog-install">'
            '<details>'
            '<summary id="catalog-install-heading">Install</summary>'
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
            "</details>"
            "</section>\n"
        )

    def _write_workflow(self) -> None:
        from harness.catalog_generator.foundry_chrome import markdown_to_html, page_shell

        workflow_md_path = _REPO_ROOT / "catalog" / "workflow.md"
        if not workflow_md_path.is_file():
            return
        workflow_md = workflow_md_path.read_text(encoding="utf-8")
        workflow_body_md = re.sub(
            r"^#\s+.*\n+", "", workflow_md.lstrip(), count=1, flags=re.MULTILINE
        )
        workflow_html = page_shell(
            title="CDD Workflow — ABD Context Driven Delivery Harness",
            h1="CDD Workflow",
            tagline=(
                "Agentic tools that bring the best of agile product, delivery, and engineering practices into the age of AI. "
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
        from harness.catalog_generator.foundry_chrome import cap_card, page_shell

        self.write_page(
            "context-tools.html",
            page_shell(
                title="Context tools — CDD Catalog",
                h1="Context tools",
                tagline="Every context tool in the catalog",
                body_inner='<div class="cap-grid">' + "".join(
                    cap_card(practice.display_name, practice.href, practice.display_name)
                    for practice in self.practices
                ) + "</div>"
                + f'<div hidden>{"".join(self._tool_bodies)}</div>',
                commons_prefix="commons/",
                nav_current="context-tools",
            ),
        )

    def _write_actions_grid(self) -> None:
        from harness.catalog_generator.foundry_chrome import cap_card, page_shell

        self.write_page(
            "actions.html",
            page_shell(
                title="Actions — CDD Catalog",
                h1="Actions",
                tagline="Lifecycle actions",
                body_inner='<div class="cap-grid">' + "".join(
                    cap_card(action.name, action.href, "Lifecycle action")
                    for action in self.lifecycle_actions
                ) + "</div>"
                + f'<div hidden>{"".join(self._action_bodies)}</div>',
                commons_prefix="commons/",
                nav_current="actions",
            ),
        )

    def _write_utilities_grid(self) -> None:
        from harness.catalog_generator.foundry_chrome import cap_card, page_shell

        self.write_page(
            "tools.html",
            page_shell(
                title="Utilities — CDD Catalog",
                h1="Utilities",
                tagline="Foundational utilities",
                body_inner='<div class="cap-grid">' + "".join(
                    cap_card(utility.name, utility.href, "Utility")
                    for utility in self.utilities
                ) + "</div>"
                + f'<div hidden>{"".join(self._utility_bodies)}</div>',
                commons_prefix="commons/",
                nav_current="tools",
            ),
        )

    def _write_fidelities_grid(self) -> None:
        from harness.catalog_generator.foundry_chrome import cap_card, page_shell

        fid_cards = [
            cap_card(
                fidelity.name,
                practice.fidelity_href(fidelity),
                f"{practice.display_name} · {practice.column_of(fidelity).key}",
                label="Fidelity",
            )
            for practice in self.practices
            for fidelity in practice.fidelities
            if practice.column_of(fidelity) is not None
        ]
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

