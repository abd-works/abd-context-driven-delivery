"""Deterministic checks for surface.md § Generate and § Satisfy.

Agent-only actions (Generate, Satisfy) must not appear in {surface}.py CLI.
Only actions with documented python entry points (Deploy, Clean) may have CLI.
"""
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

AGENT_ACTIONS = frozenset({"Generate", "Satisfy", "Deploy", "Clean"})
CLI_ACTIONS = frozenset({"deploy", "clean"})
AGENT_ONLY = frozenset({"Generate", "Satisfy"})
FORBIDDEN_CLI = frozenset(
    {"generate", "satisfy", "open", "extend", "identify", "discover", "list", "is-valid"}
)
CLI_METHODS = frozenset({"deploy", "clean"})


def api_class_name(folder_name: str) -> str:
    return "".join(part.capitalize() for part in folder_name.replace("_", "-").split("-"))


def api_cli_class_name(folder_name: str) -> str:
    return f"{api_class_name(folder_name)}Cli"


def md_sections(md_path: Path) -> set[str]:
    titles: set[str] = set()
    for line in md_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            titles.add(line[3:].strip())
    return titles


def md_cli_actions(md_path: Path, surface_name: str) -> set[str]:
    """CLI actions from ## Deploy / ## Clean fenced blocks only."""
    section_to_cli = {"Deploy": "deploy", "Clean": "clean"}
    actions: set[str] = set()
    current: str | None = None
    in_fence = False
    prefix = f"python -m {surface_name}"

    for line in md_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            in_fence = False
            continue
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence or current not in section_to_cli:
            continue
        if prefix not in line:
            continue
        rest = line.split(prefix, 1)[1].strip()
        token = rest.split()[0] if rest else ""
        if token:
            actions.add(token)

    return actions


def load_surface_module(surface_dir: Path):
    py_path = surface_dir / f"{surface_dir.name}.py"
    spec = importlib.util.spec_from_file_location(
        f"_surface_align_{surface_dir.name}", py_path
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {py_path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def cli_subcommands(surface_dir: Path) -> set[str]:
    mod = load_surface_module(surface_dir)
    cli_cls = getattr(mod, api_cli_class_name(surface_dir.name))
    surface = getattr(mod, api_class_name(surface_dir.name))(surface_dir)
    cli = cli_cls(surface)
    parser = cli._build_parser()
    sub = parser._subparsers._group_actions[0]  # type: ignore[attr-defined]
    return {action.dest for action in sub._choices_actions}


def paired_files_ok(surface_dir: Path) -> list[str]:
    name = surface_dir.name
    errors: list[str] = []
    if not (surface_dir / ".cdd-config.json").is_file():
        errors.append(f"missing .cdd-config.json in {surface_dir}")
    if not (surface_dir / f"{name}.md").is_file():
        errors.append(f"missing {name}.md")
    if not (surface_dir / f"{name}.py").is_file():
        errors.append(f"missing {name}.py")
    return errors


def extension_frontmatter_present(surface_dir: Path) -> bool:
    md_path = surface_dir / f"{surface_dir.name}.md"
    text = md_path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return False
    block = text.split("---", 2)
    if len(block) < 3:
        return False
    return any(
        key in block[1]
        for key in ("extends:", "overrides:", "open:", "mustOverride:")
    )


def api_class_errors(surface_dir: Path, mod) -> list[str]:
    """Main API class mirrors folder name; actions are methods not *Deployer classes."""
    errors: list[str] = []
    name = surface_dir.name
    py_path = surface_dir / f"{name}.py"
    expected_class = api_class_name(name)
    expected_cli = api_cli_class_name(name)
    source = py_path.read_text(encoding="utf-8")

    if re.search(r"class \w*Deployer\b", source):
        errors.append(
            f"{py_path.name} must not define *Deployer classes — "
            f"implement deploy/clean on {expected_class}"
        )

    if not hasattr(mod, expected_class):
        errors.append(f"{py_path.name} must define class {expected_class}")
        return errors

    api_cls = getattr(mod, expected_class)
    for method in CLI_METHODS:
        if not hasattr(api_cls, method) or not callable(getattr(api_cls, method)):
            errors.append(
                f"{expected_class} must implement {method}() matching §{method.title()}"
            )

    if not hasattr(mod, expected_cli):
        errors.append(
            f"{py_path.name} must define {expected_cli} to route CLI entry points"
        )

    return errors


def alignment_errors(surface_dir: Path) -> list[str]:
    surface_dir = surface_dir.resolve()
    errors = paired_files_ok(surface_dir)
    if errors:
        return errors

    md_path = surface_dir / f"{surface_dir.name}.md"
    py_path = surface_dir / f"{surface_dir.name}.py"

    sections = md_sections(md_path)
    if sections != AGENT_ACTIONS:
        missing = AGENT_ACTIONS - sections
        extra = sections - AGENT_ACTIONS
        if missing:
            errors.append(f"{md_path.name} missing agent actions: {sorted(missing)}")
        if extra:
            errors.append(f"{md_path.name} unexpected agent actions: {sorted(extra)}")

    if extension_frontmatter_present(surface_dir):
        errors.append(f"{md_path.name} has extension frontmatter — plain surface is closed")

    documented_cli = md_cli_actions(md_path, surface_dir.name)
    if documented_cli != CLI_ACTIONS:
        errors.append(
            f"{md_path.name} documented CLI {sorted(documented_cli)} "
            f"!= expected {sorted(CLI_ACTIONS)}"
        )

    try:
        mod = load_surface_module(surface_dir)
        cli_cmds = cli_subcommands(surface_dir)
    except Exception as exc:
        errors.append(f"cannot inspect CLI in {py_path.name}: {exc}")
        return errors

    errors.extend(api_class_errors(surface_dir, mod))

    if cli_cmds != CLI_ACTIONS:
        errors.append(
            f"{py_path.name} CLI subcommands {sorted(cli_cmds)} "
            f"!= expected {sorted(CLI_ACTIONS)}"
        )

    for action in AGENT_ONLY:
        if action.lower() in cli_cmds:
            errors.append(f"{py_path.name} must not expose CLI for agent-only §{action}")

    source = py_path.read_text(encoding="utf-8")
    for forbidden in FORBIDDEN_CLI:
        if f'add_parser("{forbidden}"' in source:
            errors.append(f'{py_path.name} must not add_parser("{forbidden}")')

    return errors


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    surface_dir = Path(args[0]).resolve() if args else Path(__file__).resolve().parent
    errors = alignment_errors(surface_dir)
    if errors:
        for err in errors:
            print(f"satisfy FAIL: {err}")
        return 1
    print(f"satisfy OK: agentic surface aligned — {surface_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
