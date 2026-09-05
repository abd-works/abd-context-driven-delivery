"""abd-practice-pipeline orchestrator.

Thin shell over the four engine CLIs. Does not reimplement any of them.

Subcommands:
  validate   --doc <md>                     # step 2 + 3
  save-graph --doc <md>  [--graph <json>]   # step 4 (gated by md_to_json)
  render     --graph <json> [--drawio <p>]  # step 5 (gated by json_to_drawio)
  sync-back  --drawio <drawio>              # step 6 (gated by drawio_to_json)
  run        --doc <md> [--skill <skill>]   # full 2..6, also runs validate first
  on-edit    --path <changed-file>          # dispatcher for hooks/watcher

Resolution:
  defaults <- pipeline.yaml at the engagement root
  override <- frontmatter `abd_pipeline:` on the markdown doc
  override <- per-doc `target_skill:` frontmatter (or `--skill` flag), else
              `default_practice_skill:` from pipeline.yaml

This script is intentionally small. The single source of truth for each step
remains the engine skill it calls.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


SCRIPT_DIR = Path(__file__).resolve().parent          # drawio-story-sync/scripts/
REPO_ROOT = SCRIPT_DIR.parent.parent.parent.parent   # agilebydesign-skills/

ENGINES = {
    "scanners": REPO_ROOT
    / "skills"
    / "skill-helpers"
    / "execute-skill-using-skills-rules"
    / "scripts"
    / "run_scanners.py",
    "story_graph": REPO_ROOT
    / "skills"
    / "story-driven-delivery"
    / "story-graph-ops"
    / "scripts"
    / "story_graph_cli.py",
    "drawio": REPO_ROOT
    / "skills"
    / "story-driven-delivery"
    / "drawio-story-sync"
    / "scripts"
    / "drawio_story_sync_cli.py",
}


# ---------------------------------------------------------------------------
# Config + frontmatter resolution
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class PipelineConfig:
    md_to_json: str = "prompt"
    json_to_drawio: str = "yes"
    drawio_to_json: str = "prompt"
    graph_suffix: str = "story-graph.json"
    drawio_suffix: str = ".drawio"
    default_skill: str = "skills/story-driven-delivery/abd-story-mapping"


def _coerce_gate(value: Any, fallback: str) -> str:
    if isinstance(value, bool):
        return "yes" if value else "no"
    if value is None:
        return fallback
    text = str(value).strip().lower()
    if text in {"yes", "y", "true"}:
        return "yes"
    if text in {"no", "n", "false"}:
        return "no"
    if text in {"prompt", "ask"}:
        return "prompt"
    return fallback


def load_workspace_config(root: Path) -> PipelineConfig:
    cfg_path = root / "pipeline.yaml"
    if not cfg_path.exists():
        return PipelineConfig()
    raw = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
    defaults = raw.get("defaults") or {}
    paths = raw.get("paths") or {}
    return PipelineConfig(
        md_to_json=_coerce_gate(defaults.get("md_to_json"), "prompt"),
        json_to_drawio=_coerce_gate(defaults.get("json_to_drawio"), "yes"),
        drawio_to_json=_coerce_gate(defaults.get("drawio_to_json"), "prompt"),
        graph_suffix=str(paths.get("graph_suffix", "story-graph.json")),
        drawio_suffix=str(paths.get("drawio_suffix", ".drawio")),
        default_skill=str(
            raw.get(
                "default_practice_skill",
                "skills/story-driven-delivery/abd-story-mapping",
            )
        ),
    )


_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def read_frontmatter(doc: Path) -> dict[str, Any]:
    if not doc.exists():
        return {}
    text = doc.read_text(encoding="utf-8")
    match = _FRONTMATTER_RE.match(text)
    if not match:
        return {}
    try:
        data = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError:
        return {}
    return data if isinstance(data, dict) else {}


def resolve_gate(name: str, doc_fm: dict[str, Any], cfg: PipelineConfig) -> str:
    fallback = getattr(cfg, name)
    pipeline_fm = doc_fm.get("abd_pipeline") or {}
    if isinstance(pipeline_fm, dict) and name in pipeline_fm:
        return _coerce_gate(pipeline_fm.get(name), fallback)
    return fallback


def resolve_skill(doc_fm: dict[str, Any], cli_skill: str | None, cfg: PipelineConfig) -> Path:
    if cli_skill:
        return _resolve_skill_path(cli_skill)
    fm_skill = doc_fm.get("target_skill")
    if isinstance(fm_skill, str) and fm_skill.strip():
        return _resolve_skill_path(fm_skill)
    return _resolve_skill_path(cfg.default_skill)


def _resolve_skill_path(value: str) -> Path:
    p = Path(value)
    if p.is_absolute():
        return p
    return (REPO_ROOT / p).resolve()


# ---------------------------------------------------------------------------
# Path conventions
# ---------------------------------------------------------------------------


def graph_path_for(doc: Path, cfg: PipelineConfig) -> Path:
    return doc.with_name(doc.stem + cfg.graph_suffix)


def drawio_path_for(graph: Path, cfg: PipelineConfig) -> Path:
    stem = graph.name
    if stem.endswith(cfg.graph_suffix):
        stem = stem[: -len(cfg.graph_suffix)]
    if not stem:
        stem = graph.stem  # plain "story-graph.json" → "story-graph"
    return graph.with_name(stem + cfg.drawio_suffix)


def graph_for_drawio(drawio: Path, cfg: PipelineConfig) -> Path:
    return drawio.with_name(drawio.stem + cfg.graph_suffix)


# ---------------------------------------------------------------------------
# y/n/p prompting
# ---------------------------------------------------------------------------


def gate_decision(name: str, value: str, *, non_interactive: bool) -> bool:
    """Return True (proceed) or False (skip). Print what was decided."""
    if value == "yes":
        print(f"  [gate {name}] = yes -> proceeding")
        return True
    if value == "no":
        print(f"  [gate {name}] = no -> skipping")
        return False
    if non_interactive or not sys.stdin.isatty():
        print(
            f"  [gate {name}] = prompt (non-interactive) -> deferring; "
            f"re-run interactively or set abd_pipeline.{name}: yes"
        )
        return False
    answer = input(f"  [gate {name}] proceed? [y/N] ").strip().lower()
    return answer in {"y", "yes"}


# ---------------------------------------------------------------------------
# Engine wrappers (subprocess shells)
# ---------------------------------------------------------------------------


def _run(cmd: list[str], *, cwd: Path | None = None, check: bool = True) -> int:
    print(f"  $ {' '.join(str(c) for c in cmd)}")
    proc = subprocess.run(cmd, cwd=cwd, check=False)
    if check and proc.returncode != 0:
        raise SystemExit(proc.returncode)
    return proc.returncode


def step_validate(doc: Path, skill: Path, cfg: PipelineConfig) -> int:
    """Step 2 + 3: AI-pass cue + scanner pass."""
    print(f"[step 2/3] validate {doc} against skill {skill.name}")
    if not skill.exists():
        print(f"  ! skill not found: {skill}")
        return 2
    rules_dir = skill / "rules"
    if rules_dir.exists():
        rules = sorted(rules_dir.glob("*.md"))
        print(f"  rules to apply ({len(rules)}):")
        for r in rules:
            print(f"    - {r.relative_to(skill)}")
    else:
        print("  (no rules/ directory; skill has no rules pass)")

    scanners_dir = skill / "scanners"
    if not scanners_dir.exists() or not any(scanners_dir.glob("*-scanner.py")):
        print("  (no scanners; rules pass is the only check)")
        return 0

    return _run(
        [
            sys.executable,
            str(ENGINES["scanners"]),
            "--skill-root",
            str(skill),
            "--workspace",
            str(doc.parent),
        ],
        check=False,
    )


def step_save_graph(doc: Path, graph: Path, cfg: PipelineConfig) -> int:
    """Step 4: write story-graph.json (the doc author still composes it).

    The minimal contract this orchestrator can keep without inferring graph
    structure from arbitrary practice MD: ensure a graph file exists and is
    valid. If it does not exist, write an empty-but-valid scaffold via
    `story_graph_cli.py write`. If it does exist, run `read` to validate.
    """
    print(f"[step 4] save-graph {graph}")
    graph.parent.mkdir(parents=True, exist_ok=True)
    if not graph.exists():
        scaffold = json.dumps(
            {"story_map": {"epics": []}, "version": 1, "source_doc": str(doc.name)},
            indent=2,
        )
        scaffold_file = graph.with_suffix(graph.suffix + ".tmp.json")
        scaffold_file.write_text(scaffold, encoding="utf-8")
        try:
            _run(
                [
                    sys.executable,
                    str(ENGINES["story_graph"]),
                    "write",
                    "--file",
                    str(graph),
                    "--input",
                    str(scaffold_file),
                ]
            )
        finally:
            scaffold_file.unlink(missing_ok=True)
    return _run(
        [sys.executable, str(ENGINES["story_graph"]), "read", "--file", str(graph)],
        check=False,
    )


def step_render(graph: Path, drawio: Path, mode: str = "outline") -> int:
    """Step 5: render the story-map drawio from JSON (always re-renders outline)."""
    action = "update" if drawio.exists() else "create"
    print(f"[step 5] render ({action}) {drawio} (mode={mode})")
    drawio.parent.mkdir(parents=True, exist_ok=True)
    return _run(
        [
            sys.executable,
            str(ENGINES["drawio"]),
            "render",
            "--mode", mode,
            "--graph", str(graph),
            "--out",   str(drawio),
        ],
        check=False,
    )


def step_sync_back(drawio: Path, graph: Path) -> int:
    """Step 6: drawio -> JSON (also re-renders companion diagrams)."""
    print(f"[step 6] sync-back {drawio} -> {graph}")
    rc = _run(
        [
            sys.executable,
            str(ENGINES["drawio"]),
            "sync",
            "--drawio",
            str(drawio),
            "--graph",
            str(graph),
        ],
        check=False,
    )
    if rc == 0:
        _run(
            [sys.executable, str(ENGINES["story_graph"]), "read", "--file", str(graph)],
            check=False,
        )
    return rc


# ---------------------------------------------------------------------------
# Top-level commands
# ---------------------------------------------------------------------------


def _workspace_root(args: argparse.Namespace) -> Path:
    """Return the engagement workspace root from --root or cwd."""
    if getattr(args, "root", None):
        return Path(args.root).resolve()
    return Path.cwd()


def cmd_validate(args: argparse.Namespace) -> int:
    cfg = load_workspace_config(_workspace_root(args))
    doc = Path(args.doc).resolve()
    fm = read_frontmatter(doc)
    skill = resolve_skill(fm, args.skill, cfg)
    return step_validate(doc, skill, cfg)


def cmd_save_graph(args: argparse.Namespace) -> int:
    cfg = load_workspace_config(_workspace_root(args))
    doc = Path(args.doc).resolve()
    fm = read_frontmatter(doc)
    gate = resolve_gate("md_to_json", fm, cfg)
    if not gate_decision("md_to_json", gate, non_interactive=args.non_interactive):
        return 0
    graph = Path(args.graph).resolve() if args.graph else graph_path_for(doc, cfg)
    rc = step_save_graph(doc, graph, cfg)
    if rc != 0:
        return rc
    # cascade to render if json_to_drawio is yes
    cascade = resolve_gate("json_to_drawio", fm, cfg)
    if gate_decision("json_to_drawio", cascade, non_interactive=args.non_interactive):
        drawio = drawio_path_for(graph, cfg)
        rc = step_render(graph, drawio, mode="outline")
    return rc


def cmd_render(args: argparse.Namespace) -> int:
    cfg = load_workspace_config(_workspace_root(args))
    graph = Path(args.graph).resolve()
    drawio = Path(args.drawio).resolve() if args.drawio else drawio_path_for(graph, cfg)
    return step_render(graph, drawio, mode=args.mode)


def cmd_sync_back(args: argparse.Namespace) -> int:
    cfg = load_workspace_config(_workspace_root(args))
    drawio = Path(args.drawio).resolve()
    graph = Path(args.graph).resolve() if args.graph else graph_for_drawio(drawio, cfg)
    # find a sibling MD to read frontmatter for the gate (best-effort)
    sibling_md = drawio.with_suffix(".md")
    fm = read_frontmatter(sibling_md) if sibling_md.exists() else {}
    gate = resolve_gate("drawio_to_json", fm, cfg)
    if not gate_decision("drawio_to_json", gate, non_interactive=args.non_interactive):
        return 0
    return step_sync_back(drawio, graph)


def cmd_run(args: argparse.Namespace) -> int:
    cfg = load_workspace_config(_workspace_root(args))
    doc = Path(args.doc).resolve()
    fm = read_frontmatter(doc)
    skill = resolve_skill(fm, args.skill, cfg)
    print(f"== abd-practice-pipeline run ==\n  doc:   {doc}\n  skill: {skill}")
    rc = step_validate(doc, skill, cfg)
    if rc != 0:
        print("  validation failed -> halting before save-graph; fix and re-run")
        return rc
    save_args = argparse.Namespace(
        doc=str(doc), graph=None, non_interactive=args.non_interactive
    )
    return cmd_save_graph(save_args)


def cmd_on_edit(args: argparse.Namespace) -> int:
    """Dispatcher for the watcher / Cursor afterFileEdit hook."""
    path = Path(args.path).resolve()
    cfg = load_workspace_config(_workspace_root(args))
    if path.suffix == ".md" and "story" in path.parts:
        fm = read_frontmatter(path)
        skill = resolve_skill(fm, None, cfg)
        rc = step_validate(path, skill, cfg)
        if rc != 0:
            return rc
        gate = resolve_gate("md_to_json", fm, cfg)
        if gate_decision("md_to_json", gate, non_interactive=True):
            graph = graph_path_for(path, cfg)
            rc = step_save_graph(path, graph, cfg)
            if rc != 0:
                return rc
            cascade = resolve_gate("json_to_drawio", fm, cfg)
            if gate_decision("json_to_drawio", cascade, non_interactive=True):
                step_render(graph, drawio_path_for(graph, cfg))
        return 0
    if path.suffix == ".drawio":
        sibling_md = path.with_suffix(".md")
        fm = read_frontmatter(sibling_md) if sibling_md.exists() else {}
        gate = resolve_gate("drawio_to_json", fm, cfg)
        if gate_decision("drawio_to_json", gate, non_interactive=True):
            return step_sync_back(path, graph_for_drawio(path, cfg))
        return 0
    if path.name.endswith(cfg.graph_suffix):
        drawio = drawio_path_for(path, cfg)
        if not drawio.exists():
            print(f"  (skipping: {drawio.name} does not exist — create it first)")
            return 0
        cascade = cfg.json_to_drawio
        if gate_decision("json_to_drawio", cascade, non_interactive=True):
            rc = step_render(path, drawio, mode="outline")
            if rc != 0:
                return rc
            # Also re-render exploration and increments drawio if they exist
            stem = drawio.stem  # e.g. "story-graph"
            exploration = drawio.with_name(stem + "-exploration.drawio")
            if exploration.exists():
                print(f"[step 5+] re-render exploration {exploration.name}")
                step_render(path, exploration, mode="exploration")
            increments = drawio.with_name(stem + "-increments.drawio")
            if increments.exists():
                print(f"[step 5+] re-render increments {increments.name}")
                step_render(path, increments, mode="increments")
        return 0
    print(f"  (no pipeline action for {path})")
    return 0


# ---------------------------------------------------------------------------
# argparse plumbing
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="pipeline.py", description="abd-practice-pipeline")
    p.add_argument(
        "--non-interactive",
        action="store_true",
        help="Treat 'prompt' gates as defer (do not block on input).",
    )
    p.add_argument(
        "--root",
        default=None,
        help="Engagement workspace root (for pipeline.yaml lookup). Defaults to cwd.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("validate", help="Step 2+3: rules pass + scanner pass")
    sp.add_argument("--doc", required=True)
    sp.add_argument("--skill", default=None, help="Override target skill path")
    sp.set_defaults(func=cmd_validate)

    sp = sub.add_parser("save-graph", help="Step 4: write story-graph.json")
    sp.add_argument("--doc", required=True)
    sp.add_argument("--graph", default=None)
    sp.set_defaults(func=cmd_save_graph)

    sp = sub.add_parser("render", help="Step 5: render .drawio from JSON")
    sp.add_argument("--graph", required=True)
    sp.add_argument("--drawio", default=None)
    sp.add_argument(
        "--mode",
        default="outline",
        choices=["outline", "exploration", "increments"],
    )
    sp.set_defaults(func=cmd_render)

    sp = sub.add_parser("sync-back", help="Step 6: drawio -> JSON")
    sp.add_argument("--drawio", required=True)
    sp.add_argument("--graph", default=None)
    sp.set_defaults(func=cmd_sync_back)

    sp = sub.add_parser("run", help="Full validate+save+render flow")
    sp.add_argument("--doc", required=True)
    sp.add_argument("--skill", default=None)
    sp.set_defaults(func=cmd_run)

    sp = sub.add_parser("on-edit", help="Hook/watcher dispatcher")
    sp.add_argument("--path", required=True)
    sp.set_defaults(func=cmd_on_edit)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args) or 0


if __name__ == "__main__":
    os.environ.setdefault("PYTHONUTF8", "1")
    sys.exit(main())
