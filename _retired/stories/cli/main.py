"""Thin CLI wrapper over the deterministic code-path generators.

This is the **code path** described in `stories/behavior/code-scaffolding-vs-ai-editing.md`.
Use it for:

- The first render of a spec-file tree in a code backend, or a diagram tree in
  drawio.
- The first scaffold of tier files (write-once — never overwrites existing).
- Translating a whole story subtree into a new backend, including drawio views.
- Bulk re-render after the AI has done fine-grained edits to the underlying
  model files (e.g. hand-edited scenarios, added stories, changed thin-slice).

Do NOT use it for fine-grained edits (single scenario tweak, single body fill).
Those are AI edits — the CLI intentionally has no `edit` subcommand.

Invocation
----------

    python stories/cli/main.py <command> [options]

Commands
--------

- ``create``         — render-tree + scaffold-tiers in one pass. The canonical
                       "bring a story subtree into a new backend" command; use
                       this for almost every code-path invocation. For drawio
                       the scaffold phase is a no-op.
- ``render-tree``    — render only the spec-file tree for a code backend, or
                       the requested views for a diagram backend. Idempotent.
- ``scaffold-tiers`` — emit only the write-once <slug>-<tier>.test.<ext> files
                       per story-tier. Skips any file that already exists.
                       Only meaningful for code backends.

Formats
-------

- ``ts``, ``tsx``, ``py``, ``js`` — code backends (spec-file + tier scaffold).
- ``java``                        — code backend now wired. Uses Java records/
                                    interfaces from `templates/java/`.
- ``md``                          — document backend. Renders `story-map.md`.
                                    `--tests-root` defaults to `""` (workspace
                                    root). No tiers.
- ``drawio``                      — diagram backend. Views: ``story-map`` (Epic
                                    → SubEpic → Story grid), ``thin-slice``
                                    (increments with stories), ``scenario``
                                    (Story → Scenarios → one cell per clause;
                                    no Examples tables).

Every command is idempotent-safe: spec files and diagram views re-render
deterministically; tier files are guarded by an existence check that never
overwrites.
"""

from __future__ import annotations

import argparse
import io
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Dict, List, Sequence


# Import from the stories package. This file lives at stories/cli/stories.py so
# the repository root is two parents up — put it on sys.path before importing
# from `stories.src.stories.*`.
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
_CLI_DIR = Path(__file__).resolve().parent
if str(_CLI_DIR) not in sys.path:
    sys.path.insert(0, str(_CLI_DIR))

from stories.src.stories.workspace import Workspace  # noqa: E402


# ---------------------------------------------------------------------------
# Backend registry — one row per code backend the CLI knows about.
# ---------------------------------------------------------------------------


def _import_backend(format_key: str) -> Dict[str, Callable]:
    """Return the callables for a backend, imported lazily so unused backends
    don't drag their transitive imports into every CLI run.

    Every backend descriptor carries a `kind`: `"code"` for backends that emit
    spec-file trees plus tier scaffolds, or `"diagram"` for renderers that emit
    view files (e.g. drawio) and have no tier concept.
    """
    if format_key in ("ts", "tsx"):
        from stories.src.stories.code.typescript.tree import render_ts_tree
        from stories.src.stories.code.typescript.tier_scaffold import scaffold_ts_tier_tree
        default_tier_ext = {"client": "tsx"} if format_key == "tsx" else None
        return {
            "kind": "code",
            "render_tree": render_ts_tree,
            "scaffold_tiers": scaffold_ts_tier_tree,
            "default_tier_extensions": default_tier_ext,
            "supports_tier_extensions": True,
        }
    if format_key == "py":
        from stories.src.stories.code.python.tree import render_py_tree
        from stories.src.stories.code.python.tier_scaffold import scaffold_py_tier_tree
        return {
            "kind": "code",
            "render_tree": render_py_tree,
            "scaffold_tiers": scaffold_py_tier_tree,
            "default_tier_extensions": None,
            "supports_tier_extensions": False,
        }
    if format_key == "js":
        from stories.src.stories.code.javascript.tree import render_js_tree
        from stories.src.stories.code.javascript.tier_scaffold import scaffold_js_tier_tree
        return {
            "kind": "code",
            "render_tree": render_js_tree,
            "scaffold_tiers": scaffold_js_tier_tree,
            "default_tier_extensions": None,
            "supports_tier_extensions": True,
        }
    if format_key == "java":
        from stories.src.stories.code.java.tree import render_java_tree
        from stories.src.stories.code.java.tier_scaffold import scaffold_java_tier_tree
        return {
            "kind": "code",
            "render_tree": render_java_tree,
            "scaffold_tiers": scaffold_java_tier_tree,
            "default_tier_extensions": None,
            "supports_tier_extensions": False,
        }
    if format_key == "drawio":
        from stories.src.stories.diagram.drawio.nodes import DrawIOStoryMap

        _DRAWIO_VIEWS = ("story-map", "thin-slice", "scenario")
        _DRAWIO_FILENAMES = {
            "story-map": "story-map.drawio",
            "thin-slice": "thin-slicing.drawio",
            "scenario":   "acceptance-criteria.drawio",
        }

        def _render_drawio_tree(workspace, views=_DRAWIO_VIEWS, tests_root="diagrams"):
            sm = workspace.story_map
            d = DrawIOStoryMap()
            root = tests_root.strip("/") or "diagrams"
            out = {}
            for view in views:
                if view == "story-map" and sm.epics:
                    out[f"{root}/{_DRAWIO_FILENAMES[view]}"] = d.render(sm)
                elif view == "thin-slice" and sm.increments:
                    out[f"{root}/{_DRAWIO_FILENAMES[view]}"] = d.render_thin_slice(sm)
                elif view == "scenario" and sm.epics and any(
                    getattr(s, "scenarios", None) for s in sm.all_stories()
                ):
                    out[f"{root}/{_DRAWIO_FILENAMES[view]}"] = d.render_scenario(sm)
            return out

        return {
            "kind": "diagram",
            "render_tree": _render_drawio_tree,
            "all_views": _DRAWIO_VIEWS,
        }
    if format_key == "md":
        from stories.src.stories.document.markdown.tree import render_md_tree
        return {
            "kind": "document",
            "render_tree": render_md_tree,
            "supports_tier_extensions": False,
            "default_tier_extensions": None,
        }
    raise ValueError(
        f"unknown --format {format_key!r} (choose from ts, tsx, py, js, java, md, drawio)"
    )


SUPPORTED_FORMATS = ("ts", "tsx", "py", "js", "java", "md", "drawio")


# ---------------------------------------------------------------------------
# Subcommand implementations
# ---------------------------------------------------------------------------


def cmd_render_tree(args: argparse.Namespace) -> int:
    backend = _import_backend(args.format)
    workspace = Workspace.load(Path(args.workspace).resolve())

    if backend["kind"] == "diagram":
        views = _resolve_views_arg(args, backend)
        tree = backend["render_tree"](
            workspace,
            views=views,
            tests_root=args.tests_root,
        )
        return _emit(tree, output=Path(args.output).resolve(), dry_run=args.dry_run, kind="diagram")

    # code and document backends both call render_tree(story_map, ...)
    tree = backend["render_tree"](
        workspace.story_map,
        tests_root=args.tests_root,
        include_shared=not args.no_shared,
    )
    return _emit(tree, output=Path(args.output).resolve(), dry_run=args.dry_run, kind="spec")


def cmd_scaffold_tiers(args: argparse.Namespace) -> int:
    backend = _import_backend(args.format)

    if backend["kind"] in ("diagram", "document"):
        # Diagrams and document backends have no tier concept.
        sys.stderr.write(
            f"[tier] --format {args.format} has no tier files; skipping scaffold phase.\n"
        )
        return 0

    workspace = Workspace.load(Path(args.workspace).resolve())
    tiers = _parse_tiers(args.tiers)
    if not tiers:
        _emit_error("no --tiers given (comma-separated, e.g. server,client,e2e,domain)")
        return 2

    existing = _read_existing_tree(Path(args.output).resolve(), args.tests_root)

    kwargs: Dict = {
        "tests_root": args.tests_root,
        "existing_tree": existing,
    }
    if backend["supports_tier_extensions"]:
        ext_override = _parse_tier_extensions(args.tier_ext)
        merged = dict(backend["default_tier_extensions"] or {})
        merged.update(ext_override)
        if merged:
            kwargs["tier_extensions"] = merged

    tree = backend["scaffold_tiers"](workspace.story_map, tiers, **kwargs)
    return _emit(tree, output=Path(args.output).resolve(), dry_run=args.dry_run, kind="tier")


def cmd_create(args: argparse.Namespace) -> int:
    """Full first-pass: render-tree + scaffold-tiers back-to-back.

    For code backends the scaffolder consults `existing_tree`, so running
    `create` on a project that already has tier files leaves them alone — the
    write-once contract is preserved end-to-end. For diagram backends the
    scaffold phase is a no-op and only the tree is rendered.
    """
    rc = cmd_render_tree(args)
    if rc != 0:
        return rc
    return cmd_scaffold_tiers(args)


def _resolve_views_arg(args: argparse.Namespace, backend: Dict) -> Sequence[str]:
    """Turn the `--view` flag into a concrete list of drawio views.

    Empty / missing / `all` all resolve to every supported view. Explicit
    comma-separated names win. Unknown names are rejected by the underlying
    renderer, not here.
    """
    raw = (getattr(args, "view", None) or "").strip().lower()
    if not raw or raw == "all":
        return backend["all_views"]
    return tuple(entry.strip() for entry in raw.split(",") if entry.strip())


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _emit(tree: Dict[str, str], *, output: Path, dry_run: bool, kind: str) -> int:
    if not tree:
        sys.stderr.write(f"[{kind}] no files produced (empty story map or all tier files already exist)\n")
        return 0

    written: List[str] = []
    skipped: List[str] = []
    for rel_path, contents in sorted(tree.items()):
        target = output / rel_path
        if target.exists() and kind == "tier":
            # Second-line defense in case the caller passed a stale existing_tree.
            skipped.append(rel_path)
            continue
        if dry_run:
            written.append(rel_path)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(contents, encoding="utf-8")
        written.append(rel_path)

    payload = {
        "kind": kind,
        "output": str(output),
        "written": written,
        "skipped_existing": skipped,
        "dry_run": dry_run,
    }
    json.dump(payload, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


def _read_existing_tree(output_root: Path, tests_root: str) -> Dict[str, str]:
    """Snapshot the current output tree so the scaffolder can honor its
    write-once contract. Only files under `<output>/<tests_root>/` are
    surveyed — that matches the paths the scaffolder will consider."""
    scan_root = output_root / tests_root.strip("/")
    if not scan_root.exists():
        return {}
    existing: Dict[str, str] = {}
    for path in scan_root.rglob("*"):
        if path.is_file():
            rel = path.relative_to(output_root).as_posix()
            existing[rel] = ""  # value unused by the scaffolder, only key membership
    return existing


def _parse_tiers(raw: str | None) -> Sequence[str]:
    if not raw:
        return ()
    parts = [entry.strip() for entry in raw.split(",")]
    return tuple(entry for entry in parts if entry)


def _parse_tier_extensions(pairs: List[str] | None) -> Dict[str, str]:
    """Accept `--tier-ext client=tsx` (repeatable) and return `{tier: ext}`."""
    result: Dict[str, str] = {}
    for pair in pairs or []:
        if "=" not in pair:
            raise ValueError(f"--tier-ext expects <tier>=<ext>, got {pair!r}")
        tier, ext = pair.split("=", 1)
        result[tier.strip()] = ext.strip().lstrip(".")
    return result


def _emit_error(message: str) -> None:
    sys.stderr.write(f"error: {message}\n")


# ---------------------------------------------------------------------------
# Argparse plumbing
# ---------------------------------------------------------------------------


def _add_common_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--workspace",
        required=True,
        help="Path to the workspace root that holds the story map / scenarios. "
             "The CLI loads a Workspace from here via workspace.loader.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Where to write generated files. Defaults to --workspace.",
    )
    parser.add_argument(
        "--format",
        required=True,
        choices=SUPPORTED_FORMATS,
        help="Backend to render into.",
    )
    parser.add_argument(
        "--tests-root",
        default="tests",
        help=(
            "Top-level folder under --output for the emitted tree. "
            "Default: 'tests' for code backends, 'diagrams' for --format drawio."
        ),
    )
    parser.add_argument(
        "--view",
        default=None,
        help=(
            "Drawio-only. Comma-separated views to render "
            "(story-map, thin-slice, scenario) or 'all'. Default: all."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report the files that would be written without touching disk.",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="stories",
        description=(
            "Deterministic code-path CLI for the stories skill. "
            "Renders spec-file trees and scaffolds write-once tier files. "
            "For fine-grained edits, use AI — see "
            "stories/behavior/code-scaffolding-vs-ai-editing.md."
        ),
    )
    sub = parser.add_subparsers(dest="command", required=True, metavar="<command>")

    p_render = sub.add_parser(
        "render-tree",
        help="Render shared story-types + story-runner + one <slug>-stories.<ext> per story with scenarios.",
    )
    _add_common_args(p_render)
    p_render.add_argument(
        "--no-shared",
        action="store_true",
        help="Skip story-types / story-runner. Useful when only spec files should re-render.",
    )
    p_render.set_defaults(func=cmd_render_tree)

    p_scaffold = sub.add_parser(
        "scaffold-tiers",
        help="Emit one write-once <slug>-<tier>.test.<ext> per story-tier. Never overwrites existing files.",
    )
    _add_common_args(p_scaffold)
    p_scaffold.add_argument(
        "--tiers",
        required=False,
        help=(
            "Comma-separated tier names, e.g. server,client,e2e,domain. "
            "Required for code backends; ignored for --format drawio."
        ),
    )
    p_scaffold.add_argument(
        "--tier-ext",
        action="append",
        metavar="<tier>=<ext>",
        help="Override the file extension for a tier. Repeatable. Example: --tier-ext client=tsx.",
    )
    p_scaffold.set_defaults(func=cmd_scaffold_tiers)

    p_create = sub.add_parser(
        "create",
        help="Canonical code-path command: render-tree + scaffold-tiers in one pass. Use this for almost every invocation.",
    )
    _add_common_args(p_create)
    p_create.add_argument("--no-shared", action="store_true", help="Skip shared files during render-tree phase.")
    p_create.add_argument(
        "--tiers",
        required=False,
        help=(
            "Comma-separated tier names for the scaffold phase. "
            "Required for code backends; ignored for --format drawio."
        ),
    )
    p_create.add_argument(
        "--tier-ext", action="append", metavar="<tier>=<ext>",
        help="Override the file extension for a tier. Repeatable.",
    )
    p_create.set_defaults(func=cmd_create)

    return parser


def main(argv: List[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "output", None):
        args.output = args.workspace

    # Flip `--tests-root` default when the user picked drawio and left the
    # code-flavoured default in place. Explicit `--tests-root tests` still
    # wins if the caller really wants both formats sharing a folder.
    if args.format == "drawio" and args.tests_root == "tests":
        args.tests_root = "diagrams"
    # md artifacts sit at the workspace root by convention — no sub-folder.
    if args.format == "md" and args.tests_root == "tests":
        args.tests_root = ""

    from invocation_log import log_cli_invocation

    started_at = datetime.now(timezone.utc).isoformat()
    t0 = time.perf_counter()
    stdout_capture = io.StringIO() if os.environ.get("STORIES_CLI_LOG") else None
    old_stdout = sys.stdout
    if stdout_capture is not None:
        sys.stdout = stdout_capture
    exit_code = 0
    stderr_tail = ""
    try:
        exit_code = args.func(args)
    except NotImplementedError as exc:
        stderr_tail = str(exc)
        _emit_error(str(exc))
        exit_code = 3
    except ValueError as exc:
        stderr_tail = str(exc)
        _emit_error(str(exc))
        exit_code = 2
    finally:
        if stdout_capture is not None:
            sys.stdout = old_stdout
            captured = stdout_capture.getvalue()
            sys.stdout.write(captured)
        else:
            captured = ""

    elapsed = time.perf_counter() - t0
    written: List[str] = []
    if captured.strip():
        try:
            payload = json.loads(captured)
            written = list(payload.get("written") or [])
        except json.JSONDecodeError:
            pass
    log_cli_invocation(
        argv=sys.argv if argv is None else ["stories/cli/main.py", *argv],
        started_at=started_at,
        elapsed_seconds=elapsed,
        exit_code=exit_code,
        command=getattr(args, "command", None),
        fmt=getattr(args, "format", None),
        workspace=getattr(args, "workspace", None),
        output=getattr(args, "output", None),
        tests_root=getattr(args, "tests_root", None),
        view=getattr(args, "view", None),
        dry_run=bool(getattr(args, "dry_run", False)),
        written=written,
        stderr_tail=stderr_tail or None,
    )
    if os.environ.get("STORIES_SKILL_TRACE"):
        try:
            from stories.src.skill.skill_trace import log_cli as trace_cli

            trace_cli(
                argv=sys.argv if argv is None else ["stories/cli/main.py", *argv],
                command=getattr(args, "command", None),
                fmt=getattr(args, "format", None),
                workspace=getattr(args, "workspace", None),
                written=written,
                exit_code=exit_code,
            )
        except ImportError:
            pass
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
