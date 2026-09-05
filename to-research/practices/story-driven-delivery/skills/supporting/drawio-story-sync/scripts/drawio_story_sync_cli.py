#!/usr/bin/env python3
"""CLI for story DrawIO render and layout (**drawio-story-sync** + **story-graph-ops**).

Put **this** ``scripts`` directory and **story-graph-ops** ``scripts`` on ``PYTHONPATH``,
or run from this repo layout where the sibling skill exists (paths are added automatically).

Example (PowerShell):

```text
$env:PYTHONPATH = "C:\\dev\\agilebydesign-skills\\skills\\drawio-story-sync\\scripts;C:\\dev\\agilebydesign-skills\\skills\\story-graph-ops\\scripts"
cd C:\\dev\\agilebydesign-skills\\skills\\drawio-story-sync\\scripts
python drawio_story_sync_cli.py render --mode outline --graph C:\\tmp\\story-graph.json --out C:\\tmp\\story-map.drawio
python drawio_story_sync_cli.py sync --drawio C:\\tmp\\story-map.drawio --graph C:\\tmp\\story-graph.json
```
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Optional, Tuple

if TYPE_CHECKING:
    from story_graph_ops.update_report import UpdateReport

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

_MODES = {
    'outline': 'render-outline',
    'story-map': 'render-outline',
    'exploration': 'render-exploration',
    'acceptance-criteria': 'render-exploration',
    'increments': 'render-increments',
    'thin-slicing': 'render-increments',
    'thin-slices': 'render-increments',
    'prioritization': 'render-increments',
}

# Skill-aligned fixed companion file names (no stem prefix).
# These match the skill names one-to-one:
#   abd-story-acceptance-criteria  →  acceptance-criteria.drawio
#   abd-thin-slicing         →  thin-slicing.drawio
_COMPANION_AC = 'acceptance-criteria.drawio'
_COMPANION_THIN = 'thin-slicing.drawio'

# Standalone diagram stems that are fixed-name companions (not suffixed from an outline stem).
_FIXED_COMPANION_STEMS = {'thin-slicing', 'acceptance-criteria'}


def _ensure_story_graph_ops_path() -> None:
    """Sibling ``story-graph-ops/scripts`` (same layout as ``story_io_synchronizer``)."""
    ops = _SCRIPT_DIR.parent / 'story-graph-ops' / 'scripts'
    if ops.is_dir() and str(ops) not in sys.path:
        sys.path.insert(0, str(ops))


def _diagram_type_for_load(cli_value: str) -> str:
    """Map CLI ``--diagram-type`` to ``DrawIOStoryMap.load(..., diagram_type=...)``."""
    if cli_value in ('exploration', 'acceptance-criteria'):
        return 'acceptance_criteria'
    if cli_value in ('thin-slicing', 'thin-slices'):
        return 'increments'
    return cli_value


def _companion_stem(drawio_path: Path) -> str:
    """Strip legacy ``-increments`` / ``-exploration`` suffixes so companions use the outline stem.

    Fixed-name companions (``thin-slicing``, ``acceptance-criteria``) have no outline
    stem prefix, so return ``""`` — callers use ``_COMPANION_AC`` / ``_COMPANION_THIN``
    directly instead.
    """
    s = drawio_path.stem
    if s in _FIXED_COMPANION_STEMS:
        return ''
    for suf in ('-increments', '-exploration', '-acceptance-criteria', '-thin-slicing', '-outline'):
        if s.endswith(suf):
            return s[: -len(suf)] or s
    return s


def _unlink_diagram_stale_sidecars(drawio_path: Path) -> list:
    """Remove transient JSON beside a .drawio stem after **sync** (diagram → graph apply).

    Deletes ``<stem>-update-report.json``, ``<stem>-layout.json``, and
    ``<stem>-extracted.json`` so stale diff artifacts do not linger. Not used after
    **render** (graph → diagram), so layout can still load for the next outline render.
    """
    removed: list = []
    parent = drawio_path.parent
    stem = drawio_path.stem
    for name in (
        f'{stem}-update-report.json',
        f'{stem}-layout.json',
        f'{stem}-extracted.json',
    ):
        p = parent / name
        if p.is_file():
            try:
                p.unlink()
                removed.append(str(p))
            except OSError:
                pass
    return removed


def cmd_render(args: argparse.Namespace) -> int:
    _ensure_story_graph_ops_path()
    from drawio_story_sync.story_io_synchronizer import DrawIOSynchronizer

    mode = (args.mode or 'outline').lower().replace('_', '-')
    renderer = _MODES.get(mode)
    if not renderer:
        print(f"Unknown mode {args.mode!r}. Use: {', '.join(sorted(set(_MODES)))}", file=sys.stderr)
        return 2

    sync = DrawIOSynchronizer()
    kw = {}
    if args.scope:
        kw['scope'] = args.scope
    sync.render(args.graph, args.out, renderer_command=renderer, **kw)
    print(json.dumps({'status': 'ok', 'output': str(args.out), 'mode': mode, 'renderer_command': renderer}))
    return 0


def cmd_save_layout(args: argparse.Namespace) -> int:
    _ensure_story_graph_ops_path()
    from drawio_story_sync.story_io_synchronizer import DrawIOSynchronizer

    r = DrawIOSynchronizer().save_layout(args.drawio)
    print(json.dumps(r))
    return 0 if r.get('status') == 'success' else 1


def _write_report(
    diagram: Path,
    graph: Path,
    report_out: Optional[Path],
    scope: Optional[str],
    diagram_type: str = 'outline',
) -> Tuple[Path, Path, 'UpdateReport', 'DrawIOStoryMap']:
    """Load diagram, diff vs graph, save extracted + update-report.

    Returns ``(extracted_path, report_path, report, drawio_map)``.
    """
    _ensure_story_graph_ops_path()
    from drawio_story_sync.drawio_story_map import DrawIOStoryMap
    from story_graph_ops.nodes import StoryMap

    if not diagram.is_file():
        raise FileNotFoundError(f'Missing diagram: {diagram}')
    if not graph.is_file():
        raise FileNotFoundError(f'Missing graph: {graph}')

    load_type = _diagram_type_for_load(diagram_type)
    drawio_map = DrawIOStoryMap.load(diagram, diagram_type=load_type)
    from drawio_story_sync.story_io_synchronizer import DrawIOSynchronizer, load_story_graph_json

    DrawIOSynchronizer().save_layout(diagram)

    original = StoryMap(load_story_graph_json(graph))
    if scope:
        filtered = original.filter_by_name(scope)
        if filtered is not None:
            original = filtered

    extracted_path = diagram.parent / f'{diagram.stem}-extracted.json'
    drawio_map.save_as_json(extracted_path)
    report = drawio_map.generate_update_report(original)
    out = Path(report_out) if report_out else diagram.parent / f'{diagram.stem}-update-report.json'
    report.save(out)
    return extracted_path, out, report, drawio_map


def cmd_apply_report(args: argparse.Namespace) -> int:
    """Apply ``*-update-report.json`` to ``story-graph.json`` using **story_graph_ops** (no DrawIO)."""
    _ensure_story_graph_ops_path()
    from story_graph_ops.nodes import StoryMap
    from story_graph_ops.update_report import UpdateReport

    report_path = Path(args.report)
    graph_path = Path(args.graph)
    if not report_path.is_file():
        print(f"Missing report: {report_path}", file=sys.stderr)
        return 2
    if not graph_path.is_file():
        print(f"Missing graph: {graph_path}", file=sys.stderr)
        return 2

    report = UpdateReport.from_dict(json.loads(report_path.read_text(encoding='utf-8')))
    story_map = StoryMap.from_json_file(graph_path)
    story_map.apply_update_report(report, apply_ac_patches=True)
    if not getattr(args, 'dry_run', False):
        story_map.save()
    print(json.dumps({'status': 'ok', 'graph_path': str(graph_path), 'dry_run': bool(getattr(args, 'dry_run', False))}))
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    try:
        extracted_path, out, _, _ = _write_report(
            Path(args.drawio),
            Path(args.graph),
            args.report_out,
            args.scope,
            diagram_type=args.diagram_type,
        )
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        return 2
    print(json.dumps({'status': 'ok', 'report_path': str(out), 'extracted_path': str(extracted_path)}))
    return 0


def cmd_sync(args: argparse.Namespace) -> int:
    """Diff diagram vs graph, apply report, then re-render exploration + increments from graph."""
    try:
        extracted_path, report_path, report, drawio_map = _write_report(
            Path(args.drawio),
            Path(args.graph),
            args.report_out,
            args.scope,
            diagram_type=args.diagram_type,
        )
    except FileNotFoundError as e:
        print(str(e), file=sys.stderr)
        return 2

    _ensure_story_graph_ops_path()
    from story_graph_ops.nodes import StoryMap

    dry = bool(getattr(args, 'dry_run', False))
    story_map = StoryMap.from_json_file(Path(args.graph))
    story_map.apply_update_report(report)
    if _diagram_type_for_load(args.diagram_type) == 'acceptance_criteria':
        from drawio_story_sync.diagram_ac_sync import apply_per_story_diagram_ac

        apply_per_story_diagram_ac(drawio_map, story_map)
    removed_sidecars: list = []
    if not dry:
        story_map.save()
        removed_sidecars = _unlink_diagram_stale_sidecars(Path(args.drawio))

    refreshed: list = []
    if not dry and not getattr(args, 'no_refresh_diagrams', False):
        from drawio_story_sync.story_io_synchronizer import DrawIOSynchronizer

        sync = DrawIOSynchronizer()
        diagram = Path(args.drawio)
        parent = diagram.parent
        exp_out = (
            Path(args.out_exploration)
            if getattr(args, 'out_exploration', None)
            else parent / _COMPANION_AC
        )
        inc_out = (
            Path(args.out_increments)
            if getattr(args, 'out_increments', None)
            else parent / _COMPANION_THIN
        )
        kw = {}
        if args.scope:
            kw['scope'] = args.scope
        sync.render(Path(args.graph), exp_out, renderer_command='render-exploration', **kw)
        sync.render(Path(args.graph), inc_out, renderer_command='render-increments', **kw)
        refreshed = [str(exp_out), str(inc_out)]

    print(json.dumps({
        'status': 'ok',
        'graph_path': str(Path(args.graph)),
        'report_path': str(report_path),
        'extracted_path': str(extracted_path),
        'dry_run': dry,
        'report_has_changes': report.has_changes,
        'refreshed_diagrams': refreshed,
        'removed_sidecars': removed_sidecars,
    }))
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description='DrawIO story map render / sync helpers')
    sub = p.add_subparsers(dest='cmd', required=True)

    r = sub.add_parser('render', help='Render story-graph.json to .drawio')
    r.add_argument('--mode', default='outline', help='outline | exploration | increments (+ aliases)')
    r.add_argument('--graph', type=Path, required=True, help='Path to story-graph.json')
    r.add_argument('--out', type=Path, required=True, help='Output .drawio path')
    r.add_argument('--scope', help='Optional story/epic/sub-epic name to filter graph')
    r.set_defaults(func=cmd_render)

    s = sub.add_parser('save-layout', help='Write *-layout.json next to a .drawio')
    s.add_argument('--drawio', type=Path, required=True)
    s.set_defaults(func=cmd_save_layout)

    _diagram_type_kw = dict(
        choices=('outline', 'story-map',
                 'increments', 'thin-slicing',
                 'exploration', 'acceptance-criteria'),
        default='outline',
        help=(
            'Kind of --drawio file (default: outline). '
            'Use thin-slicing / increments for thin-slicing.drawio, '
            'acceptance-criteria / exploration for acceptance-criteria.drawio'
        ),
    )

    g = sub.add_parser('report', help='Extract diagram, diff vs story graph, write update report JSON')
    g.add_argument('--drawio', type=Path, required=True)
    g.add_argument('--graph', type=Path, required=True)
    g.add_argument('--report-out', type=Path, help='Defaults to <stem>-update-report.json beside diagram')
    g.add_argument('--scope', help='Optional filter on original story map')
    g.add_argument('--diagram-type', **_diagram_type_kw)
    g.set_defaults(func=cmd_report)

    a = sub.add_parser(
        'apply-report',
        help='Apply update-report JSON to story-graph.json (story_graph_ops; no diagram read)',
    )
    a.add_argument('--graph', type=Path, required=True, help='Path to story-graph.json to update')
    a.add_argument('--report', type=Path, required=True, help='Path to *-update-report.json')
    a.add_argument('--dry-run', action='store_true', help='Apply in memory only; do not write graph')
    a.set_defaults(func=cmd_apply_report)

    y = sub.add_parser(
        'sync',
        help='Diagram → update story-graph.json, then re-render exploration + increments companions',
    )
    y.add_argument(
        '--drawio',
        type=Path,
        required=True,
        help='Story-map .drawio: outline, or *-increments.drawio / *-exploration.drawio with matching --diagram-type',
    )
    y.add_argument('--graph', type=Path, required=True, help='Path to story-graph.json')
    y.add_argument('--report-out', type=Path, help='Defaults to <stem>-update-report.json beside diagram')
    y.add_argument('--scope', help='Optional filter on story map when diffing/applying')
    y.add_argument('--diagram-type', **_diagram_type_kw)
    y.add_argument('--dry-run', action='store_true', help='Diff only; do not write graph or diagrams')
    y.add_argument(
        '--no-refresh-diagrams',
        action='store_true',
        help='Skip re-rendering <stem>-exploration.drawio and <stem>-increments.drawio',
    )
    y.add_argument('--out-exploration', type=Path, help='Override exploration output path')
    y.add_argument('--out-increments', type=Path, help='Override increments output path')
    y.set_defaults(func=cmd_sync)

    args = p.parse_args()
    return int(args.func(args))


if __name__ == '__main__':
    raise SystemExit(main())
