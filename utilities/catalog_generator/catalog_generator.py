# @toolset-manifest python -m tools manifest catalog_generator.catalog_generator:Catalog
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# Do not author behavior from this Python source.
"""catalog_generator - discover-and-render primitives for the CDD HTML catalog.

Wraps the real object model directly (Toolset.tools, AgenticToolset.actions,
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
Portable" (``git_blob_url``, ``resolve_repo_remote``, ``write_page``,
``write_raw_manifests`` / ``build_run_request``), and
"Configure Illustrated Examples" (``parse_illustrated_examples``,
``extract_whole_file``, ``extract_heading_section``, ``extract_comment_tag``).
"""
from __future__ import annotations

import ast
import importlib
import inspect
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from harness.harness_tool import prompt
from tools.tool import toolset

_REPO_ROOT = Path(__file__).resolve().parents[2]
_BASE_CONTEXT_TOOL_PATH = _REPO_ROOT / "context_tools" / "base" / "base_context_tool.py"
_SKILLS_DIR = _REPO_ROOT / ".cursor" / "skills"

# -- Registry ---------------------------------------------------------------
#
# Hardcoded per the plan's "Registry (context tools + utilities)" section -
# verified against the real classes on disk. CDD is the header row; the
# other five are the board's context-tool rows.

CONTEXT_TOOL_REGISTRY: tuple[tuple[str, str, str], ...] = (
    ("Context-driven delivery", "context_tools.cdd.cdd", "Cdd"),
    ("Stories", "context_tools.stories.stories", "Stories"),
    ("Clean Engineering", "context_tools.clean_engineering.clean_engineering", "CleanEngineering"),
    ("User Experience", "context_tools.ux.ux", "Ux"),
    ("Behavior-Driven Development", "context_tools.bdd.bdd", "Bdd"),
    ("Domain-Driven Design", "context_tools.ddd.ddd", "Ddd"),
)

# Harness owns generate (replaces the old deploy_agent_skills utility).
UTILITY_REGISTRY: tuple[tuple[str, str, str], ...] = (
    ("harness", "harness.harness", "Harness"),
    ("diagnose", "diagnose.diagnose", "Diagnose"),
    ("echo", "echo.echo", "Echo"),
    ("handoff", "handoff.handoff", "Handoff"),
    ("workspace", "workspace.workspace", "WorkSession"),
    ("sub_agent", "sub_agent.sub_agent", "SubAgent"),
)


def _toolset_name_of(cls: type) -> str:
    """Match ``Toolset.toolset_name`` without needing an instance (that property
    is instance-only; accessing it on the class returns the property object)."""
    import re

    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", cls.__name__).lower()


@dataclass(frozen=True)
class RegistryEntry:
    """One resolved registry row - a real, importable class, not a stub."""

    display_name: str
    module_path: str
    class_name: str
    cls: type


def _load_class(module_path: str, class_name: str) -> type:
    module = importlib.import_module(module_path)
    return getattr(module, class_name)


def load_registry() -> tuple[list[RegistryEntry], list[RegistryEntry]]:
    """Resolve every context-tool and utility registry row to a real class.

    Returns ``(context_tools, utilities)``. Resolution failures raise
    (``ImportError`` / ``AttributeError``) immediately - "nothing missing"
    is a hard fail at discover time, not a silently dropped row.
    """
    context_tools = [
        RegistryEntry(name, module_path, class_name, _load_class(module_path, class_name))
        for name, module_path, class_name in CONTEXT_TOOL_REGISTRY
    ]
    utilities = [
        RegistryEntry(name, module_path, class_name, _load_class(module_path, class_name))
        for name, module_path, class_name in UTILITY_REGISTRY
    ]
    return context_tools, utilities


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

# CDD stage key → frontmatter fidelity tokens used in template YAML/headers.
_STAGE_FRONTMATTER_TOKENS: dict[str, tuple[str, ...]] = {
    "discovery": ("discovery",),
    "spec": ("exploration", "specification", "spec"),
    "engineer": ("engineering", "engineer"),
}


@dataclass(frozen=True)
class FidelityGuidance:
    """One fidelity's key, default format, ``## {fidelity}`` body, and tool overview."""

    key: str
    default_format: str | None
    guidance: str
    overview: str = ""


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


def _frontmatter_tokens(text: str) -> set[str]:
    blob = _template_frontmatter_blob(text).lower()
    tokens: set[str] = set()
    for key in ("fidelity", "artifact", "format"):
        m = re.search(rf"{key}\s*:\s*\[([^\]]*)\]", blob)
        if m:
            for part in m.group(1).split(","):
                tok = part.strip().strip("\"'").lower()
                if tok:
                    tokens.add(tok)
        else:
            m2 = re.search(rf"{key}\s*:\s*([^\n]+)", blob)
            if m2:
                tok = m2.group(1).strip().strip("\"'").lower()
                if tok:
                    tokens.add(tok)
    return tokens


def resolve_default_template(
    module_dir: Path,
    domain_slug: str,
    fidelity: str,
    default_format: str | None,
    fidelities: dict[str, str] | None = None,
) -> Path | None:
    """Locate the artifact template for ``fidelity``'s default format.

    Prefer the format-specific ``{slug}-templates.{ext}`` file when present
    (Clean Engineering / BDD). Otherwise pick the best match under
    ``templates/{format-alias}/`` by filename and template frontmatter.
    """
    if not default_format:
        return None
    from primitives.instructions import _path_for_templates

    relative = _path_for_templates(module_dir, domain_slug, default_format)
    candidate = (module_dir / relative).resolve()
    if candidate.is_file():
        return candidate

    templates_root = module_dir / "templates"
    if not templates_root.is_dir():
        return None

    aliases = _FORMAT_DIR_ALIASES.get(default_format.lower(), (default_format.lower(),))
    search_roots = [templates_root / a for a in aliases if (templates_root / a).is_dir()]
    if not search_roots:
        search_roots = [templates_root]

    fidelity_kebab = fidelity.replace("_", "-")
    stage_key = None
    if fidelities:
        for stage, name in fidelities.items():
            if name == fidelity:
                stage_key = stage
                break
    stage_tokens = set(_STAGE_FRONTMATTER_TOKENS.get(stage_key or "", ()))

    scored: list[tuple[int, Path]] = []
    for root in search_roots:
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            name_l = path.name.lower()
            if "sketch" in name_l or "components" in path.parts:
                continue
            stem_kebab = path.stem.replace("_", "-").lower()
            score = 0
            if stem_kebab == fidelity_kebab or path.stem.lower() == fidelity.lower():
                score += 100
            elif fidelity_kebab in stem_kebab or fidelity.lower() in path.stem.lower():
                score += 40
            try:
                text = path.read_text(encoding="utf-8")
            except OSError:
                text = ""
            tokens = _frontmatter_tokens(text) if text else set()
            if fidelity.lower() in tokens or fidelity_kebab in tokens:
                score += 50
            if stage_tokens & tokens:
                score += 30
            if any(a == path.parent.name.lower() for a in aliases):
                score += 5
            if "production" in name_l:
                score -= 20
            if path.suffix == ".tpl" or name_l.endswith(".py.tpl"):
                score += 10
            if fidelity == "scenarios" and "main-flow" in stem_kebab:
                score += 25
            if score > 0:
                scored.append((score, path))

    if not scored:
        # Single non-sketch file at templates root matching format ext (e.g. DDD).
        from primitives.instructions import _FORMAT_TEMPLATE_EXT

        ext = _FORMAT_TEMPLATE_EXT.get(default_format.lower(), "")
        root_files = [
            p for p in templates_root.iterdir()
            if p.is_file() and "sketch" not in p.name.lower()
            and (not ext or p.suffix == ext or p.suffix.lstrip(".") in aliases)
        ]
        if len(root_files) == 1:
            return root_files[0].resolve()
        # Prefer fidelity / bounded-context style names when several md files.
        named = [
            p for p in root_files
            if fidelity_kebab in p.stem.replace("_", "-").lower()
            or fidelity.lower() in p.stem.lower()
        ]
        if named:
            return sorted(named)[0].resolve()
        return None

    scored.sort(key=lambda pair: (-pair[0], len(pair[1].parts), pair[1].as_posix()))
    return scored[0][1].resolve()


def extract_heading_section(markdown: str, heading: str, level: int = 2) -> str | None:
    """Return the body under ``'#' * level + ' ' + heading`` up to the next
    heading of the same or higher level, or ``None`` if the heading is absent.

    Shared by fidelity-guidance scraping here and, later, by the
    heading-anchored illustrated-example extractor - same algorithm, same
    story rule (``branch-on-mechanical-uniqueness`` keeps whole-file /
    heading / comment-tag as three distinct extractors, but heading-anchored
    extraction itself is one algorithm reused wherever a heading anchors a
    section).
    """
    marker = "#" * level + " "
    lines = markdown.splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.strip().lower() == (marker + heading).lower():
            start = i + 1
            break
    if start is None:
        return None
    end = len(lines)
    heading_re = re.compile(r"^#{1," + str(level) + r"}\s")
    for i in range(start, len(lines)):
        if heading_re.match(lines[i]):
            end = i
            break
    return "\n".join(lines[start:end]).strip()


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


def scrape_fidelities(cls: type) -> list[FidelityGuidance]:
    """For every fidelity in ``cls.fidelities`` (declared stage order), resolve
    its key, default format, and ``## {fidelity}`` guidance body from
    ``{module_dir}/{module_dir.name}.md``.

    A fidelity with no matching heading resolves to a "Guidance missing"
    stub instead of failing the whole scrape.
    """
    fidelities: dict[str, str] | None = getattr(cls, "fidelities", None)
    if not fidelities:
        return []
    format_defaults: dict[str, str] = getattr(cls, "_fidelity_format_defaults", {})
    module_dir = Path(importlib_module_file(cls.__module__)).resolve().parent
    guide_path = module_dir / f"{module_dir.name}.md"
    guide_text = guide_path.read_text(encoding="utf-8") if guide_path.is_file() else ""
    overview = extract_tool_overview(guide_text) if guide_text else ""

    results: list[FidelityGuidance] = []
    for fidelity_key in fidelities.values():
        section = extract_heading_section(guide_text, fidelity_key) if guide_text else None
        results.append(
            FidelityGuidance(
                key=fidelity_key,
                default_format=format_defaults.get(fidelity_key),
                guidance=section if section is not None else _GUIDANCE_MISSING,
                overview=overview,
            )
        )
    return results


def importlib_module_file(module_path: str) -> str:
    """Thin wrapper so ``scrape_fidelities`` needs only one import surface."""
    module = importlib.import_module(module_path)
    return module.__file__  # type: ignore[return-value]


# -- Lifecycle action resolution (AST walk) ----------------------------------

_ACTION_DECORATOR_NAME = "action"


@dataclass(frozen=True)
class ActionResolution:
    """One public lifecycle ``@agent_instructions``'s resolved delegate dir and same-instance calls."""

    name: str
    source_dir: Path
    calls: list[str] = field(default_factory=list)


def _decorator_names(node: ast.FunctionDef) -> set[str]:
    names: set[str] = set()
    for dec in node.decorator_list:
        target = dec.func if isinstance(dec, ast.Call) else dec
        if isinstance(target, ast.Name):
            names.add(target.id)
        elif isinstance(target, ast.Attribute):
            names.add(target.attr)
    return names


# Plan: emit top-level lifecycle actions; skip override hooks.
# ``generate_fixes_from_validate`` is a satisfy helper, not its own catalog action.
# ``improve`` sits after ``repair`` — same peer kit (``utilities/repair/``),
# distinct guide (``improve.md``); the improve loop is catalogued as its own
# action, not folded into repair.
_LIFECYCLE_ACTION_SKIP = frozenset({
    "generate_output",
    "add_generate_header_to_generated",
    "generate_fixes_from_validate",
})


def _public_action_methods(tree: ast.Module) -> list[ast.FunctionDef]:
    methods: list[ast.FunctionDef] = []
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        for item in node.body:
            if not isinstance(item, ast.FunctionDef):
                continue
            if item.name.startswith("_"):
                continue
            if item.name in _LIFECYCLE_ACTION_SKIP:
                continue
            if _ACTION_DECORATOR_NAME in _decorator_names(item):
                methods.append(item)
    return methods


def _init_peer_kit_attrs(tree: ast.Module) -> dict[str, str]:
    """Map ``self.<attr> = <ClassName>(...)`` assignments in ``__init__`` to
    the class name assigned, for every peer-kit attribute."""
    attr_to_class: dict[str, str] = {}
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        for item in node.body:
            if not (isinstance(item, ast.FunctionDef) and item.name == "__init__"):
                continue
            for stmt in ast.walk(item):
                if not isinstance(stmt, ast.Assign):
                    continue
                if len(stmt.targets) != 1:
                    continue
                target = stmt.targets[0]
                if not (
                    isinstance(target, ast.Attribute)
                    and isinstance(target.value, ast.Name)
                    and target.value.id == "self"
                ):
                    continue
                value = stmt.value
                call_func = value.func if isinstance(value, ast.Call) else None
                if isinstance(call_func, ast.Name):
                    attr_to_class[target.attr] = call_func.id
    return attr_to_class


def _import_module_for_class(tree: ast.Module, class_name: str) -> str | None:
    """Find ``from <module> import <class_name>`` at module top level."""
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module:
            for alias in node.names:
                if alias.name == class_name:
                    return node.module
    return None


def _double_attr_calls(body: list[ast.stmt]) -> list[tuple[str, str]]:
    """Every ``self.<attr>.<method>(...)`` call's ``(<attr>, <method>)`` pair,
    in source order.

    The pair - not the bare attribute - is the uniqueness unit: two actions
    can each own a genuine, distinct delegate call on the *same* peer kit
    (``repair`` -> ``self.repairer.repair(...)``, ``improve`` ->
    ``self.repairer.improve()``) without either stealing the other's
    delegate dir. What marks a call as shared infrastructure instead of a
    delegate is two actions calling the exact same method on the exact same
    attribute (``document`` and ``validate`` both calling
    ``self.scanner.scan(...)``).
    """
    pairs: list[tuple[str, str]] = []
    for stmt in body:
        for node in ast.walk(stmt):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            if not isinstance(func, ast.Attribute):
                continue
            owner = func.value
            if (
                isinstance(owner, ast.Attribute)
                and isinstance(owner.value, ast.Name)
                and owner.value.id == "self"
            ):
                pairs.append((owner.attr, func.attr))
    return pairs


def _same_instance_action_calls(body: list[ast.stmt], action_names: set[str]) -> list[str]:
    """Every ``self.<method>()`` call where ``<method>`` is another public
    action name, in source order, de-duplicated."""
    calls: list[str] = []
    for stmt in body:
        for node in ast.walk(stmt):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            if (
                isinstance(func, ast.Attribute)
                and isinstance(func.value, ast.Name)
                and func.value.id == "self"
                and func.attr in action_names
                and func.attr not in calls
            ):
                calls.append(func.attr)
    return calls


def _host_action_calls(body: list[ast.stmt], action_names: set[str]) -> list[str]:
    """``host.<method>()`` or ``Generate().generate(tools=[host])`` kit dispatch."""
    calls: list[str] = []
    for stmt in body:
        for node in ast.walk(stmt):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            if not isinstance(func, ast.Attribute):
                continue
            if func.attr not in action_names or func.attr in calls:
                continue
            value = func.value
            if isinstance(value, ast.Name) and value.id == "host":
                calls.append(func.attr)
            elif func.attr == "generate":
                calls.append(func.attr)
    return calls


_HOST_LIFECYCLE_ACTIONS = frozenset({
    "generate",
    "document",
    "validate",
    "satisfy",
    "createRule",
})


def _resolve_actions_from_source(
    path: Path,
    *,
    action_names: frozenset[str] | None = None,
) -> list[tuple[str, ast.FunctionDef]]:
    """Return ``(name, method)`` for public ``@agent_instructions`` methods in ``path``."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    methods = _public_action_methods(tree)
    if action_names is not None:
        methods = [m for m in methods if m.name in action_names]
    return [(m.name, m) for m in methods]


def _resolve_kit_lifecycle_actions() -> list[ActionResolution]:
    """AST-walk kit-owned lifecycle actions (partition, grill, sketch, iterate,
    generate, document, validate, satisfy, repair, createRule)."""
    kit_specs: tuple[tuple[str, Path, str], ...] = (
        ("partition", _REPO_ROOT / "context_tools" / "actions" / "partition" / "partition.py", "partition"),
        ("grill", _REPO_ROOT / "context_tools" / "actions" / "grill_context" / "grill_context.py", "grill_context"),
        ("sketch", _REPO_ROOT / "context_tools" / "actions" / "sketch" / "sketch.py", "sketch"),
        ("iterate", _REPO_ROOT / "context_tools" / "actions" / "iterate" / "iterate.py", "iterate"),
        ("generate", _REPO_ROOT / "context_tools" / "actions" / "generate" / "generate.py", "generate"),
        ("document", _REPO_ROOT / "context_tools" / "actions" / "document" / "document.py", "document"),
        ("validate", _REPO_ROOT / "context_tools" / "actions" / "validate" / "validate.py", "validate"),
        ("satisfy", _REPO_ROOT / "context_tools" / "actions" / "satisfy" / "satisfy.py", "satisfy"),
        ("repair", _REPO_ROOT / "context_tools" / "actions" / "improvement" / "improvement.py", "improvement"),
        ("createRule", _REPO_ROOT / "context_tools" / "actions" / "validate" / "validate.py", "validate"),
    )
    results: list[ActionResolution] = []
    for name, path, dir_name in kit_specs:
        methods = _resolve_actions_from_source(path, action_names=frozenset({name}))
        if not methods:
            continue
        _method_name, method = methods[0]
        source_dir = _REPO_ROOT / "context_tools" / "actions" / dir_name
        calls = _host_action_calls(method.body, {"generate"})
        results.append(ActionResolution(name=name, source_dir=source_dir, calls=calls))
    return results


def resolve_lifecycle_actions(
    base_context_tool_path: Path | None = None,
) -> list[ActionResolution]:
    """AST-walk ``BaseContextTool``'s public ``@agent_instructions`` methods, in source
    order, and resolve each one's delegate kit dir and same-instance calls.

    Kit-owned lifecycle actions (``partition``, ``grill``, ``sketch``,
    ``iterate``) are resolved from their action kits under
    ``context_tools/actions/`` — not from the host composer.

    Delegate resolution has no hand-maintained per-action lookup table: a
    peer-kit ``(attr, method)`` call pair is that action's unique delegate
    signal only when no *other* public action calls that exact same pair.
    Two actions may each own a distinct call on the *same* peer kit
    (``repair`` -> ``self.repairer.repair(...)``, ``improve`` ->
    ``self.repairer.improve()``) without colliding - each pair is unique to
    its own action. Shared infrastructure is marked by the opposite case:
    two actions calling the *identical* pair (``document`` and ``validate``
    both calling ``self.scanner.scan(...)``), which is excluded from
    delegate resolution. An action with no unique peer-kit pair falls back
    to ``context_tools/base/``.
    """
    path = base_context_tool_path or _BASE_CONTEXT_TOOL_PATH
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)

    methods = _public_action_methods(tree)
    action_names = {m.name for m in methods}
    peer_kit_attrs = _init_peer_kit_attrs(tree)

    # (attr, method) -> set of action names that call self.<attr>.<method>(...)
    pair_actions: dict[tuple[str, str], set[str]] = {}
    for method in methods:
        for pair in set(_double_attr_calls(method.body)):
            pair_actions.setdefault(pair, set()).add(method.name)

    host_results: list[ActionResolution] = []
    for method in methods:
        called_pairs = set(_double_attr_calls(method.body))
        delegate_attr = next(
            (
                attr
                for attr, _method_name in called_pairs
                if attr in peer_kit_attrs
                and len(pair_actions.get((attr, _method_name), set())) == 1
            ),
            None,
        )
        if method.name in _HOST_LIFECYCLE_ACTIONS:
            source_dir = _REPO_ROOT / "context_tools" / "base"
        elif delegate_attr is not None:
            class_name = peer_kit_attrs[delegate_attr]
            module_path = _import_module_for_class(tree, class_name)
            package_name = module_path.split(".")[0] if module_path else delegate_attr
            actions_dir = _REPO_ROOT / "context_tools" / "actions" / package_name
            utilities_dir = _REPO_ROOT / "utilities" / package_name
            source_dir = actions_dir if actions_dir.is_dir() else utilities_dir
        else:
            source_dir = _REPO_ROOT / "context_tools" / "base"

        calls = _same_instance_action_calls(method.body, action_names - {method.name})
        host_results.append(ActionResolution(name=method.name, source_dir=source_dir, calls=calls))

    kit_by_name = {r.name: r for r in _resolve_kit_lifecycle_actions()}
    host_by_name = {r.name: r for r in host_results}
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
    return [kit_by_name.get(name) or host_by_name[name] for name in order]


# -- Skill slash-command map --------------------------------------------------

_SKILL_NAME_RE = re.compile(r"^name:\s*(.+?)\s*$", re.MULTILINE)


def skill_slash_name(module_dir_name: str) -> str | None:
    """Resolve a context tool's slash-invocable skill name from its deployed
    ``.cursor/skills/*/SKILL.md`` frontmatter ``name:`` field.

    Tries the module dir name first (``stories``), then its hyphenated form
    (``clean_engineering`` -> ``clean-engineering``) since that folder is the
    one real exception to the snake_case convention.
    """
    for candidate in (module_dir_name, module_dir_name.replace("_", "-")):
        skill_md = _SKILLS_DIR / candidate / "SKILL.md"
        if not skill_md.is_file():
            continue
        match = _SKILL_NAME_RE.search(skill_md.read_text(encoding="utf-8"))
        if match:
            return match.group(1)
    return None
\

# -- Portability: git-URL source citations + CLI defaults --------------------


def resolve_repo_remote(repo_root: Path | None = None) -> tuple[str, str]:
    """Resolve ``(repo_url, ref)`` from the local git checkout - the CLI's
    zero-flag defaults (``git remote get-url origin`` + current ``HEAD``)."""
    root = repo_root or _REPO_ROOT
    repo_url = subprocess.run(
        ["git", "remote", "get-url", "origin"],
        cwd=root, capture_output=True, text=True, check=True,
    ).stdout.strip()
    ref = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root, capture_output=True, text=True, check=True,
    ).stdout.strip()
    return normalize_repo_url(repo_url), ref


def normalize_repo_url(repo_url: str) -> str:
    """Strip a trailing ``.git`` and turn an SSH remote (``git@host:org/repo``)
    into the ``https://host/org/repo`` form ``git_blob_url`` builds on."""
    url = repo_url.strip()
    if url.startswith("git@"):
        host_and_path = url[len("git@"):]
        host, _, path = host_and_path.partition(":")
        url = f"https://{host}/{path}"
    if url.endswith(".git"):
        url = url[: -len(".git")]
    return url


def git_blob_url(repo_url: str, ref: str, path: Path, lines: tuple[int, int] | None = None) -> str:
    """Build ``{repo_url}/blob/{ref}/{relative_path}`` - the only source
    citation shape any generated page ever emits. ``path`` may be absolute
    (resolved relative to ``_REPO_ROOT``) or already-relative.

    Never a local filesystem path: this is the single seam every render
    class must go through to cite a file, so there is exactly one place a
    ``c:\\...`` / ``file://`` path could leak from, and this function is it.
    """
    try:
        relative = path.resolve().relative_to(_REPO_ROOT)
    except ValueError:
        relative = path
    posix_path = relative.as_posix()
    url = f"{repo_url.rstrip('/')}/blob/{ref}/{posix_path}"
    if lines:
        start, end = lines
        url += f"#L{start}-L{end}" if end != start else f"#L{start}"
    return url


def git_blob_url_for_callable(repo_url: str, ref: str, func: object) -> str:
    """Cite a Python callable's own definition - file + line range."""
    source_file = Path(inspect.getsourcefile(func))  # type: ignore[arg-type]
    _, start_line = inspect.getsourcelines(func)  # type: ignore[arg-type]
    end_line = start_line + len(inspect.getsource(func).splitlines()) - 1  # type: ignore[arg-type]
    return git_blob_url(repo_url, ref, source_file, (start_line, end_line))


def write_page(out_root: Path, relative_path: str, html: str) -> Path:
    """Write one generated page's literal HTML under ``out_root``.

    Every panel's content (markdown guide bodies, ``.context/module-context.md``
    prose, main-file code, illustrated-example bodies) is embedded as literal
    text into ``html`` *before* this is called - there is no runtime fetch
    back into ``context_tools/`` or ``utilities/`` from the written page.
    """
    target = out_root / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(html, encoding="utf-8")
    return target


# -- Raw run-request YAML (from live toolset manifests) -----------------------


def _example_value(name: str, type_str: str) -> object:
    """Placeholder value for a manifest parameter type in a sample request."""
    compact = type_str.replace(" ", "")
    if compact.endswith("|None") or compact == "None":
        return None
    if compact.startswith("list["):
        return []
    return f"<{name}>"


def build_run_request(
    cls: type,
    *,
    action: str,
    fidelity: str | None = None,
) -> dict:
    """Build a ``python -m tools run`` request dict from the live toolset manifest.

    Constructor parameters become ``context``; the named action's parameters
    become ``arguments``. ``fidelity`` (when the constructor accepts it) is
    filled with the given fidelity key.
    """
    signature = cls.manifest.signature
    ctor_params = (signature.get("new") or {}).get("parameters") or {}
    action_entry = signature.get(action) or {}
    action_params = action_entry.get("parameters") or {}

    context: dict[str, object] = {}
    for name, type_str in ctor_params.items():
        if name == "fidelity" and fidelity is not None:
            context[name] = fidelity
        else:
            context[name] = _example_value(name, str(type_str))

    request: dict[str, object] = {
        "toolset": cls.manifest_path,
        "context": context,
        "action": action,
    }
    if action_params:
        request["arguments"] = {
            name: _example_value(name, str(type_str))
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


def write_raw_manifests(
    out_root: Path,
    context_tool_entries: list[RegistryEntry],
    lifecycle_action_names: list[str],
) -> None:
    """Write request YAML (and full toolset manifests) under ``out_root/manifests/``.

    Per context tool:
    - ``manifests/{tool}/manifest.yaml`` — live ``front_matter`` from the toolset
    - ``manifests/{tool}/{fidelity}.yaml`` — run request with ``action: generate``
    - ``manifests/{tool}/{action}.yaml`` — run request for each lifecycle action

    Per lifecycle action:
    - ``manifests/actions/{action}.html`` — all tools' request YAML for that action
    """
    import html as html_mod

    manifests_root = out_root / "manifests"
    manifests_root.mkdir(parents=True, exist_ok=True)

    per_action_blocks: dict[str, list[tuple[str, str, str]]] = {
        name: [] for name in lifecycle_action_names
    }

    for entry in context_tool_entries:
        cls = entry.cls
        tool = _toolset_name_of(cls)
        tool_dir = manifests_root / tool
        tool_dir.mkdir(parents=True, exist_ok=True)

        (tool_dir / "manifest.yaml").write_text(cls.manifest.front_matter, encoding="utf-8")

        fidelities = list((getattr(cls, "fidelities", {}) or {}).values())
        for fidelity in fidelities:
            (tool_dir / f"{fidelity}.yaml").write_text(
                dump_run_request_yaml(cls, action="generate", fidelity=fidelity),
                encoding="utf-8",
            )

        for action_name in lifecycle_action_names:
            body = dump_run_request_yaml(cls, action=action_name)
            (tool_dir / f"{action_name}.yaml").write_text(body, encoding="utf-8")
            per_action_blocks[action_name].append((entry.display_name, tool, body))

    for action_name, blocks in per_action_blocks.items():
        sections = []
        for display_name, tool, body in blocks:
            rel = f"../{tool}/{action_name}.yaml"
            sections.append(
                f"<section>\n"
                f"<h2>{html_mod.escape(display_name)}</h2>\n"
                f'<p class="install-source"><a href="{html_mod.escape(rel)}">'
                f"{html_mod.escape(tool)}/{action_name}.yaml</a></p>\n"
                f"<pre><code>{html_mod.escape(body)}</code></pre>\n"
                f"</section>"
            )
        page = (
            "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n"
            '<meta charset="utf-8">\n'
            f"<title>{html_mod.escape(action_name)} — raw request format</title>\n"
            "<style>\n"
            "body{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;"
            "background:#0f1115;color:#e8eaed;padding:2rem;line-height:1.45;}\n"
            "h1{color:#f97316;font-size:1.25rem;}\n"
            "h2{margin-top:2rem;font-size:1rem;color:#fb923c;}\n"
            "pre{background:#1a1d24;padding:1rem;overflow:auto;border-radius:6px;}\n"
            "a{color:#fb923c;}\n"
            "p{color:#9aa0a6;}\n"
            "</style>\n</head>\n<body>\n"
            f"<h1>action: {html_mod.escape(action_name)}</h1>\n"
            "<p>Request YAML for <code>python -m tools run</code>, built from each "
            "context tool&rsquo;s live manifest signature "
            "(<code>Cls.manifest</code> / <code>python -m tools manifest</code>).</p>\n"
            + "\n".join(sections)
            + "\n</body>\n</html>\n"
        )
        write_page(out_root, f"manifests/actions/{action_name}.html", page)


# -- Illustrated examples -----------------------------------------------------


@dataclass(frozen=True)
class IllustratedExampleRow:
    """One parsed row of a tool's ``## Illustrated examples`` config table."""

    fidelity: str
    source: str
    anchor: str


_TABLE_ROW_RE = re.compile(r"^\|(.+)\|\s*$")


def parse_illustrated_examples(markdown: str) -> list[IllustratedExampleRow]:
    """Parse the ``## Illustrated examples`` table (``Fidelity | Source | Anchor``)
    out of a tool's ``examples.md`` / ``README.md`` index.

    Which file illustrates a fidelity is a decision the maintainer names
    explicitly here - this function only reads that decision, it never
    guesses a Source path from a fidelity name.
    """
    section = extract_heading_section(markdown, "Illustrated examples")
    if not section:
        return []
    rows: list[IllustratedExampleRow] = []
    lines = [line for line in section.splitlines() if _TABLE_ROW_RE.match(line)]
    # First row is the header, second is the `---` separator - both skipped.
    for line in lines[2:]:
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 3:
            continue
        fidelity, source, anchor = cells[0], cells[1], cells[2]
        rows.append(IllustratedExampleRow(fidelity=fidelity, source=source, anchor=anchor))
    return rows


def extract_whole_file(source_path: Path) -> str:
    """Whole-file illustrated example: the entire source file's content."""
    return source_path.read_text(encoding="utf-8")


def extract_comment_tag(text: str, tag: str) -> str:
    """Comment-tag-anchored illustrated example: only the lines carrying the
    given HTML comment tag (e.g. ``<!-- Mu -->``), matched literally."""
    return "\n".join(line for line in text.splitlines() if tag in line)


def resolve_illustrated_example(tool_dir: Path, row: IllustratedExampleRow) -> str:
    """Resolve one :class:`IllustratedExampleRow` to its example body, using
    the extractor its ``anchor`` mechanically implies:

    - ``anchor == "whole-file"`` -> :func:`extract_whole_file`
    - ``anchor`` starts with ``<!--`` -> :func:`extract_comment_tag`
    - anything else -> :func:`extract_heading_section` (``##``/``###``)
    """
    source_path = tool_dir / row.source
    if row.anchor == "whole-file":
        return extract_whole_file(source_path)
    text = source_path.read_text(encoding="utf-8")
    if row.anchor.startswith("<!--"):
        return extract_comment_tag(text, row.anchor)
    level = 3 if row.anchor.startswith("###") else 2
    heading = row.anchor.lstrip("#").strip()
    section = extract_heading_section(text, heading, level=level)
    return section if section is not None else text


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
                href = git_blob_url_for_callable(self.repo_url, self.ref, func)
                return f'<li><a href="{href}">{name}</a> <span class="tag">(tool, no page)</span></li>'
            except (TypeError, OSError):
                pass
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
        # (repair + improve both live under utilities/repair/).
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

    def generate_catalog(self, action: object, owner: object, source_dir: Path) -> str:
        """Render one action detail body — fidelity-style dark callouts.

        Guide and ``.context/module-context.md`` render as HTML (same as fidelity
        guidance). No source-code dump.
        Page shell (board + skill-detail wrap) is applied by ``Catalog``.
        """
        import html as html_mod

        name = getattr(action, "name", str(action))
        request_href = f"../manifests/actions/{name}.html"
        return (
            f'<header class="page-hero--detail fidelity-detail-header">'
            f'<p class="s-name">Lifecycle action</p>'
            f'<h1 class="page-headline">{html_mod.escape(name)}</h1>'
            f"</header>\n"
            f'<section class="install-block action-invoke" aria-labelledby="action-invoke-heading">'
            f'<h2 id="action-invoke-heading">Request</h2>'
            f'<p class="install-hint">used as action: <code>{html_mod.escape(name)}</code> in the request</p>'
            f'<p class="install-source">'
            f'<a href="{html_mod.escape(request_href)}" id="raw-manifest">Raw manifest format →</a></p>'
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

    def _quick_invoke(self, skill_name: str, fidelity_name: str, toolset_name: str) -> str:
        """Invoke block — Foundry install-block chrome, sits under the board."""
        action_links = ", ".join(
            f'<a href="../actions/{r.name}.html">{r.name}</a>' for r in self.lifecycle_actions
        )
        request_href = f"../manifests/{toolset_name}/{fidelity_name}.yaml"
        return (
            f'<section class="install-block fidelity-invoke" aria-labelledby="fidelity-invoke-heading">'
            f'<h2 id="fidelity-invoke-heading">Chat invoke</h2>'
            f'<pre class="install-snippet"><code>/{skill_name} &lt;action&gt; {fidelity_name}'
            f" — e.g. /{skill_name} generate {fidelity_name}</code></pre>"
            f'<p class="install-hint">&lt;action&gt; is one of: {action_links}</p>'
            f'<p class="install-source">'
            f'<a href="{request_href}" id="raw-manifest">Raw manifest format →</a></p>'
            f"</section>"
        )

    def _illustrated_example_panel(self, example_body: str | None) -> str:
        from catalog_generator.foundry_chrome import fence

        if example_body is None:
            return (
                '<section class="skill-cr-single illustrated-example">'
                "<h2>Illustrated example</h2>"
                "<p>No illustrated example configured yet.</p></section>"
            )
        return (
            f'<section class="skill-cr-single illustrated-example">'
            f"<h2>Illustrated example</h2>"
            f'{fence("text", example_body)}</section>'
        )

    def _default_template_panel(
        self,
        owner: object,
        fidelity_name: str,
        default_format: str | None,
    ) -> str:
        """Default-format template callout — sits above the illustrated example."""
        import html as html_mod

        from catalog_generator.foundry_chrome import fence

        module_dir = Path(getattr(owner, "module_dir", Path("."))).resolve()
        domain_slug = getattr(owner, "toolset_name", module_dir.name)
        fidelities = getattr(type(owner), "fidelities", None)
        path = resolve_default_template(
            module_dir, domain_slug, fidelity_name, default_format, fidelities
        )
        if path is None or not path.is_file():
            fmt = html_mod.escape(default_format or "unknown")
            return (
                '<section class="install-block fidelity-template" aria-label="Default template">'
                "<h2>Default template</h2>"
                f"<p>No template file for default format <code>{fmt}</code>.</p>"
                "</section>"
            )
        try:
            body = path.read_text(encoding="utf-8")
        except OSError:
            body = ""
        try:
            rel = path.relative_to(module_dir).as_posix()
        except ValueError:
            rel = path.name
        lang = path.suffix.lstrip(".") or "text"
        if path.name.endswith(".py.tpl"):
            lang = "python"
        elif lang == "md":
            lang = "markdown"
        elif lang == "tpl":
            lang = "text"
        blob = git_blob_url(self.repo_url, self.ref, path)
        return (
            f'<section class="install-block fidelity-template" aria-label="Default template">'
            f"<h2>Default template</h2>"
            f'<p class="install-hint">Default format: <code>{html_mod.escape(default_format or "")}</code>'
            f' — <a href="{html_mod.escape(blob)}">{html_mod.escape(rel)}</a></p>'
            f"{fence(lang, body)}"
            f"</section>"
        )

    def generate_catalog(
        self,
        fidelity_name: str,
        owner: object,
        skill_name: str,
        guidance: str,
        example_body: str | None = None,
        actions_action_owner: object | None = None,
        overview: str = "",
        tool_display_name: str = "",
        default_format: str | None = None,
    ) -> str:
        """Render everything under the board: title, invoke, guidance, template, example.

        Uses Foundry install-block chrome for invoke + guidance + default template
        (dark callout, orange links) — not the white skill-md-preview card.
        """
        import html as html_mod

        from catalog_generator.foundry_chrome import display_label, markdown_to_html

        label = display_label(fidelity_name)
        tool_label = tool_display_name or getattr(owner, "toolset_name", "")
        if default_format is None:
            defaults = getattr(type(owner), "_fidelity_format_defaults", {})
            default_format = defaults.get(fidelity_name)
        overview_html = markdown_to_html(overview) if overview.strip() else ""
        fid_md = f"## {label}\n\n{guidance}" if guidance else guidance
        guidance_html = markdown_to_html(fid_md)
        preview_bits = []
        if overview_html:
            preview_bits.append(f"<h2>Overview</h2>\n{overview_html}")
        preview_bits.append(guidance_html)
        preview = "\n".join(preview_bits)
        toolset_name = _toolset_name_of(type(owner))
        invoke = self._quick_invoke(skill_name, fidelity_name, toolset_name)
        return (
            f'<header class="page-hero--detail fidelity-detail-header">'
            f'<p class="s-name">{html_mod.escape(tool_label)} · fidelity</p>'
            f'<h1 class="page-headline">{html_mod.escape(label)}</h1>'
            f"</header>\n"
            f"{invoke}\n"
            f'<section class="install-block fidelity-guidance" '
            f'data-fidelity="{html_mod.escape(fidelity_name)}" '
            f'aria-label="Fidelity guidance">'
            f"{preview}</section>\n"
            f"{self._default_template_panel(owner, fidelity_name, default_format)}\n"
            f"{self._illustrated_example_panel(example_body)}\n"
        )

    def section_0_html(self, skill_name: str, fidelity_name: str, toolset_name: str | None = None) -> str:
        return self._quick_invoke(skill_name, fidelity_name, toolset_name or skill_name)


class CatalogContextTool:
    """The context-tool page for one ``BaseContextTool`` instance - Stories,
    DDD, UX, Clean Engineering, BDD, or CDD's own header-row page."""

    def __init__(self, repo_url: str, ref: str, catalog_fidelity: CatalogFidelity) -> None:
        self.repo_url = repo_url
        self.ref = ref
        self.catalog_fidelity = catalog_fidelity

    def generate_catalog(
        self,
        owner: object,
        display_name: str,
        skill_name: str,
        guidances: list[FidelityGuidance],
        example_bodies: dict[str, str | None] | None = None,
    ) -> str:
        """Render one context-tool page body - badge, Purpose, fidelity cards
        (links only — never nest full fidelity pages)."""
        import html as html_mod

        purpose = (getattr(owner, "__doc__", "") or "").strip()
        from catalog_generator.foundry_chrome import markdown_to_html

        # Prefer tool guide overview over class docstring when available.
        overview = ""
        if guidances:
            overview = guidances[0].overview
        purpose_html = markdown_to_html(overview) if overview else f"<p>{html_mod.escape(purpose)}</p>"
        fidelity_names = list(getattr(type(owner), "fidelities", {}).values())
        from catalog_generator.foundry_chrome import display_label

        slug = _toolset_name_of(type(owner))
        # CDD's "fidelities" are the three stage columns already on the board —
        # do not re-list them as empty Foundry skill cards (discovery/spec/engineer).
        fidelities_section = ""
        if slug != "cdd":
            cards = "".join(
                f'<a class="cap-card fidelity-card" href="../fidelities/{slug}-{name}.html">'
                f'<p class="cap-card__title">{html_mod.escape(display_label(name))}</p>'
                f'<p class="cap-card__label">Fidelity</p>'
                f'<p class="cap-card__more">Open →</p></a>'
                for name in fidelity_names
            )
            fidelities_section = f'  <section class="fidelities cap-grid">{cards}</section>\n'
        return (
            f'<article class="context-tool-page" data-tool="{html_mod.escape(display_name)}">\n'
            f'  <header><span class="badge">{html_mod.escape(display_name)}</span></header>\n'
            f'  <div class="purpose-html">{purpose_html}</div>\n'
            f"{fidelities_section}"
            f"</article>"
        )


class CatalogUtility:
    """The utility-row detail page for one plain-utility ``Toolset`` instance."""

    def __init__(self, repo_url: str, ref: str, catalog_tool: CatalogTool, catalog_action: CatalogAction) -> None:
        self.repo_url = repo_url
        self.ref = ref
        self.catalog_tool = catalog_tool
        self.catalog_action = catalog_action

    def generate_catalog(self, owner: object, display_name: str) -> str:
        """Render one utility page body — fidelity-style dark callouts."""
        import html as html_mod

        from catalog_generator.foundry_chrome import markdown_to_html

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


@toolset
class Catalog:
    """The top-level entry point - the only class ``generate_cdd_catalog.py``
    calls. Owns the shared portability config and the fixed roster of live
    instances to render. Always copies Foundry commons into ``out_root``."""

    def __init__(
        self,
        repo_url: str,
        ref: str,
        out_root: str,
        catalog_context_tool: CatalogContextTool,
        catalog_action: CatalogAction,
        catalog_utility: CatalogUtility,
    ) -> None:
        self.repo_url = repo_url
        self.ref = ref
        self.out_root = Path(out_root)
        self.catalog_context_tool = catalog_context_tool
        self.catalog_action = catalog_action
        self.catalog_utility = catalog_utility

    def _board_tool_entries(
        self,
        context_tool_entries: list[RegistryEntry],
    ) -> list[dict]:
        from catalog_generator.foundry_chrome import STAGES
        from context_tools.cdd.cdd import _CONTEXT_TOOLS_BY_STAGE

        tools_on_stage: dict[str, set[str]] = {
            stage: {_toolset_name_of(cls) for cls in classes}
            for stage, classes in _CONTEXT_TOOLS_BY_STAGE.items()
        }

        tools: list[dict] = []
        for entry in context_tool_entries:
            fidelities_by_stage = getattr(entry.cls, "fidelities", {}) or {}
            tool_name = _toolset_name_of(entry.cls)
            stage_map: dict[str, dict] = {}
            for stage_key, _label in STAGES:
                # CDD header row: cells from Cdd.fidelities (always on the board).
                # Other tools: only when listed in Cdd._CONTEXT_TOOLS_BY_STAGE
                # for that stage (plan: BDD discovery cell stays empty).
                if tool_name != "cdd" and tool_name not in tools_on_stage.get(stage_key, set()):
                    continue
                fid_name = fidelities_by_stage.get(stage_key)
                if fid_name:
                    stage_map[stage_key] = {
                        "key": fid_name,
                        "href": f"fidelities/{tool_name}-{fid_name}.html",
                    }
            tools.append(
                {
                    "display_name": entry.display_name,
                    "toolset_name": tool_name,
                    "href": f"context-tools/{tool_name}.html",
                    "fidelities": stage_map,
                }
            )
        return tools

    @prompt(name="generate-catalog")
    def generate_catalog(
        self,
        context_tool_entries: list[RegistryEntry],
        utility_entries: list[RegistryEntry],
        lifecycle_actions: list[ActionResolution],
        action_owner: object,
    ) -> None:
        """Render the whole catalog into ``self.out_root`` with Foundry chrome.
        No output is ever written outside ``out_root``."""
        from catalog_generator.foundry_chrome import (
            cap_card,
            copy_commons,
            display_label,
            page_shell,
            render_hub_board,
        )

        self.out_root.mkdir(parents=True, exist_ok=True)
        copy_commons(self.out_root)

        write_raw_manifests(
            self.out_root,
            context_tool_entries,
            [r.name for r in lifecycle_actions],
        )

        board_tools = self._board_tool_entries(context_tool_entries)
        action_dicts = [{"name": r.name, "href": f"actions/{r.name}.html"} for r in lifecycle_actions]
        utility_dicts = [
            {"name": e.display_name, "href": f"utilities/{e.display_name}.html"}
            for e in utility_entries
        ]

        # -- context-tool pages --
        tool_bodies: list[str] = []
        for entry in context_tool_entries:
            owner = entry.cls()
            skill_name = skill_slash_name(owner.toolset_name) or owner.toolset_name
            guidances = scrape_fidelities(entry.cls)
            body = self.catalog_context_tool.generate_catalog(
                owner, entry.display_name, skill_name, guidances,
            )
            tool_bodies.append(body)
            page = page_shell(
                title=f"{entry.display_name} — CDD Catalog",
                h1=entry.display_name,
                tagline="Context tool",
                body_inner=body,
                commons_prefix="../commons/",
                nav_prefix="../",
                nav_current="context-tools",
                kanban_embed=render_hub_board(
                    board_tools, action_dicts, utility_dicts,
                    highlight_tool=owner.toolset_name,
                    path_prefix="../",
                    initial_family=owner.toolset_name,
                ),
            )
            write_page(self.out_root, f"context-tools/{owner.toolset_name}.html", page)

            # fidelity pages for this tool
            for g in guidances:
                fid_body = self.catalog_context_tool.catalog_fidelity.generate_catalog(
                    g.key,
                    owner,
                    skill_name,
                    g.guidance,
                    overview=g.overview,
                    tool_display_name=entry.display_name,
                    default_format=g.default_format,
                )
                fid_page = page_shell(
                    title=f"{display_label(g.key)} — {entry.display_name}",
                    h1=display_label(g.key),
                    tagline=f"{entry.display_name} · fidelity",
                    body_inner=fid_body,
                    commons_prefix="../commons/",
                    nav_prefix="../",
                    nav_current="fidelities",
                    show_hero=False,
                    body_wrap_class="skill-detail-page",
                    kanban_embed=render_hub_board(
                        board_tools, action_dicts, utility_dicts,
                        highlight_tool=owner.toolset_name,
                        highlight_fidelity=g.key,
                        path_prefix="../",
                        initial_family=owner.toolset_name,
                    ),
                )
                write_page(
                    self.out_root,
                    f"fidelities/{owner.toolset_name}-{g.key}.html",
                    fid_page,
                )

        # -- action pages --
        action_bodies: list[str] = []
        for resolution in lifecycle_actions:
            action = action_owner.actions[resolution.name]
            body = self.catalog_action.generate_catalog(action, action_owner, resolution.source_dir)
            action_bodies.append(body)
            page = page_shell(
                title=f"{resolution.name} — lifecycle action",
                h1=resolution.name,
                tagline="Lifecycle action",
                body_inner=body,
                commons_prefix="../commons/",
                nav_prefix="../",
                nav_current="actions",
                show_hero=False,
                body_wrap_class="skill-detail-page",
                kanban_embed=render_hub_board(
                    board_tools, action_dicts, utility_dicts,
                    path_prefix="../",
                ),
            )
            write_page(self.out_root, f"actions/{resolution.name}.html", page)

        # -- utility pages --
        utility_bodies: list[str] = []
        for entry in utility_entries:
            try:
                owner_u: object = entry.cls()
            except TypeError:
                owner_u = entry.cls
            body = self.catalog_utility.generate_catalog(owner_u, entry.display_name)
            utility_bodies.append(body)
            page = page_shell(
                title=f"{entry.display_name} — utility",
                h1=entry.display_name,
                tagline="Utility",
                body_inner=body,
                commons_prefix="../commons/",
                nav_prefix="../",
                nav_current="utilities",
                show_hero=False,
                body_wrap_class="skill-detail-page",
                kanban_embed=render_hub_board(
                    board_tools, action_dicts, utility_dicts,
                    path_prefix="../",
                ),
            )
            write_page(self.out_root, f"utilities/{entry.display_name}.html", page)

        # -- hub --
        import html as html_mod

        board = render_hub_board(board_tools, action_dicts, utility_dicts)
        harness_href = git_blob_url(
            self.repo_url,
            self.ref,
            _REPO_ROOT / "primitives" / "harness" / "harness.py",
        )
        hub_body = (
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
            "<code>primitives/harness/harness.py</code></a> "
            "into the chat and ask the agent to run "
            "<strong>generate</strong> "
            "(action <code>generate</code>). "
            "That deploys each context tool as an IDE skill shim.</li>"
            "</ol>"
            "</section>\n"
        )
        hub = page_shell(
            title="The ABD Foundry — Context Driven Delivery",
            h1='The ABD <span class="accent">Foundry</span>',
            tagline=(
                "The ABD Foundry — thirty years of product engineering experience "
                "shared as agents, skills, and tools that anyone can use. Grab the repo "
                '<a href="https://github.com/abd-works/abd-context-driven-delivery" '
                'target="_blank" rel="noopener noreferrer">here</a>.'
            ),
            body_inner=hub_body,
            commons_prefix="commons/",
            nav_prefix="",
            nav_current="hub",
            kanban_embed=board,
        )
        write_page(self.out_root, "index.html", hub)

        # -- workflow manual (from catalog/workflow.md) --
        from catalog_generator.foundry_chrome import markdown_to_html

        workflow_md_path = _REPO_ROOT / "catalog" / "workflow.md"
        if workflow_md_path.is_file():
            workflow_md = workflow_md_path.read_text(encoding="utf-8")
            # Drop the leading H1 — page_shell already provides the title.
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
            write_page(self.out_root, "workflow.html", workflow_html)

        # -- flat grids --
        write_page(
            self.out_root,
            "context-tools.html",
            page_shell(
                title="Context tools — CDD Catalog",
                h1="Context tools",
                tagline="Every context tool in the catalog",
                body_inner='<div class="cap-grid">' + "".join(
                    cap_card(e.display_name, f"context-tools/{_toolset_name_of(e.cls)}.html", e.display_name)
                    for e in context_tool_entries
                ) + "</div>"
                # keep CDD string findable for tests that scan the grid page
                + f'<div hidden>{"".join(tool_bodies)}</div>',
                commons_prefix="commons/",
                nav_current="context-tools",
            ),
        )
        write_page(
            self.out_root,
            "actions.html",
            page_shell(
                title="Actions — CDD Catalog",
                h1="Actions",
                tagline="Lifecycle actions",
                body_inner='<div class="cap-grid">' + "".join(
                    cap_card(r.name, f"actions/{r.name}.html", "Lifecycle action")
                    for r in lifecycle_actions
                ) + "</div>"
                + f'<div hidden>{"".join(action_bodies)}</div>',
                commons_prefix="commons/",
                nav_current="actions",
            ),
        )
        write_page(
            self.out_root,
            "utilities.html",
            page_shell(
                title="Utilities — CDD Catalog",
                h1="Utilities",
                tagline="Foundational utilities",
                body_inner='<div class="cap-grid">' + "".join(
                    cap_card(e.display_name, f"utilities/{e.display_name}.html", "Utility")
                    for e in utility_entries
                ) + "</div>"
                + f'<div hidden>{"".join(utility_bodies)}</div>',
                commons_prefix="commons/",
                nav_current="utilities",
            ),
        )
        # fidelities grid
        fid_cards = []
        for entry in context_tool_entries:
            for stage, fid_name in (getattr(entry.cls, "fidelities", {}) or {}).items():
                fid_cards.append(
                    cap_card(
                        fid_name,
                        f"fidelities/{_toolset_name_of(entry.cls)}-{fid_name}.html",
                        f"{entry.display_name} · {stage}",
                        label="Fidelity",
                    )
                )
        write_page(
            self.out_root,
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
