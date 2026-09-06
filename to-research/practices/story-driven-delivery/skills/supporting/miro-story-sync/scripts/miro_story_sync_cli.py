#!/usr/bin/env python3
"""CLI for Miro story-map render (**miro-story-sync** + **story-graph-ops**).

Put **`common/`**, **this skill's `scripts/`**, and **story-graph-ops**
``scripts/`` on ``PYTHONPATH``, or run from the standard monorepo layout
where the sibling skills exist (paths are added automatically).

Example (PowerShell):

```text
$env:MIRO_ACCESS_TOKEN = "<your token>"
python miro_story_sync_cli.py render --mode outline `
    --graph C:\\tmp\\story-graph.json `
    --board uXjVK123abc=
python miro_story_sync_cli.py render --mode outline `
    --graph C:\\tmp\\story-graph.json --dry-run
```

``--dry-run`` swaps in ``InMemoryMiroTransport`` so you can verify rendering
without contacting Miro. Without a token (and without ``--dry-run``) the CLI
exits non-zero and prints the auth requirement.

Board ID resolution order (``--board`` omitted):
  1. ``conf/miro.json`` beside the project root (parent of graph's parent dir).
  2. Interactive prompt — user pastes a Miro board URL; the ID is extracted and
     saved back to ``conf/miro.json`` for future runs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Optional

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))


_BOARD_URL_RE = re.compile(r'miro\.com/app/board/([^/?#]+)')
_MODES = {
    'outline': 'render-outline',
    'story-map': 'render-outline',
    'exploration': 'render-exploration',
    'acceptance-criteria': 'render-exploration',
}


def _conf_path(graph: Path) -> Path:
    """Return ``<project-root>/conf/miro.json`` inferred from the graph path."""
    return graph.resolve().parent.parent / 'conf' / 'miro.json'


def _load_conf(graph: Path) -> dict:
    cp = _conf_path(graph)
    if cp.exists():
        try:
            return json.loads(cp.read_text(encoding='utf-8'))
        except Exception:
            return {}
    return {}


def _save_conf(graph: Path, data: dict) -> None:
    cp = _conf_path(graph)
    cp.parent.mkdir(parents=True, exist_ok=True)
    cp.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')


def _board_id_from_url(url: str) -> Optional[str]:
    m = _BOARD_URL_RE.search(url)
    return m.group(1) if m else None


def _resolve_board_id(cli_board: Optional[str], graph: Path, dry_run: bool) -> Optional[str]:
    """Return board ID from: CLI arg → conf/miro.json → interactive prompt."""
    if cli_board:
        return cli_board
    if dry_run:
        return None

    conf = _load_conf(graph)
    if conf.get('board_id'):
        print(f"[miro-story-sync] board_id from conf: {conf['board_id']}", file=sys.stderr)
        return conf['board_id']

    print('[miro-story-sync] No board ID found in conf/miro.json.', file=sys.stderr)
    url = input('  Paste the Miro board URL: ').strip()
    board_id = _board_id_from_url(url)
    if not board_id:
        # Maybe they pasted just the ID directly
        board_id = url or None
    if board_id:
        conf['board_id'] = board_id
        conf['board_url'] = url if url.startswith('http') else f'https://miro.com/app/board/{board_id}/'
        _save_conf(graph, conf)
        print(f"  Saved to {_conf_path(graph)}", file=sys.stderr)
    return board_id


def _ensure_repo_paths() -> None:
    """Sibling ``lib/``, ``story-graph-ops/scripts`` (mirrors miro_story_sync._bootstrap)."""
    skill_root = _SCRIPT_DIR.parent
    skills_dir = skill_root.parent
    package_root = skills_dir.parent
    for p in (
        package_root / "lib",
        skills_dir / "common",
        skills_dir / "story-graph-ops" / "scripts",
    ):
        s = str(p)
        if p.is_dir() and s not in sys.path:
            sys.path.insert(0, s)


def _skill_secrets_path() -> Path:
    """Return ``<story-driven-delivery>/conf/secrets.json`` relative to this script."""
    # _SCRIPT_DIR = .../story-driven-delivery/skills/supporting/miro-story-sync/scripts
    return _SCRIPT_DIR.parent.parent.parent.parent / 'conf' / 'secrets.json'


def _load_token() -> Optional[str]:
    """Return Miro access token from env var or conf/secrets.json fallback.

    Resolution order:
      1. ``MIRO_ACCESS_TOKEN`` environment variable.
      2. ``miro_access_token`` key in ``<story-driven-delivery>/conf/secrets.json``.
    """
    token = os.environ.get('MIRO_ACCESS_TOKEN')
    if token:
        return token
    secrets_path = _skill_secrets_path()
    if secrets_path.exists():
        try:
            data = json.loads(secrets_path.read_text(encoding='utf-8'))
            token = data.get('miro_access_token')
            if token:
                print(f'[miro-story-sync] token loaded from {secrets_path}', file=sys.stderr)
                return token
        except Exception:
            pass
    return None


def _build_transport(board_id: Optional[str], dry_run: bool):
    """Return ``(transport, transport_name, dry_run_actual)``.

    Falls back to ``InMemoryMiroTransport`` when ``--dry-run`` is set or when
    no ``MIRO_ACCESS_TOKEN`` is configured (so ``render`` works locally for
    smoke tests without surprising the user with HTTP errors).

    Token resolution order:
      1. ``MIRO_ACCESS_TOKEN`` environment variable.
      2. ``miro_access_token`` in ``<story-driven-delivery>/conf/secrets.json``.
    """
    from miro_story_sync.miro_transport import (
        InMemoryMiroTransport,
        MiroTransportError,
        RestMiroTransport,
    )

    if dry_run or not board_id:
        return InMemoryMiroTransport(), 'InMemoryMiroTransport', True
    token = _load_token()
    if not token:
        return InMemoryMiroTransport(), 'InMemoryMiroTransport', True
    try:
        return RestMiroTransport(board_id, access_token=token), 'RestMiroTransport', False
    except MiroTransportError:
        return InMemoryMiroTransport(), 'InMemoryMiroTransport', True


def _graph_hash(graph: Path) -> str:
    """Return the SHA-256 hex digest of the story-graph.json file contents."""
    return hashlib.sha256(graph.read_bytes()).hexdigest()


def cmd_render(args: argparse.Namespace) -> int:
    _ensure_repo_paths()
    from miro_story_sync.miro_story_synchronizer import MiroSynchronizer
    from miro_story_sync.miro_transport import RestMiroTransport

    mode = (args.mode or 'outline').lower().replace('_', '-')
    renderer = _MODES.get(mode)
    if not renderer:
        print(
            f"Unknown mode {args.mode!r}. Use: {', '.join(sorted(set(_MODES)))}",
            file=sys.stderr,
        )
        return 2

    dry_run = bool(getattr(args, 'dry_run', False))
    resume = bool(getattr(args, 'resume', False))
    board_id = _resolve_board_id(getattr(args, 'board', None), args.graph, dry_run)

    transport, transport_name, dry_run_actual = _build_transport(board_id, dry_run)

    if isinstance(transport, RestMiroTransport):
        checkpoint_path = _conf_path(args.graph).parent / 'miro-sync-checkpoint.json'
        transport.setup_checkpoint(
            checkpoint_path,
            _graph_hash(args.graph),
            mode,
            resume,
        )

    sync = MiroSynchronizer(transport=transport)
    kw = {}
    if args.scope:
        kw['scope'] = args.scope
    result = sync.render(args.graph, renderer_command=renderer, **kw)

    print(json.dumps({
        'status': 'ok',
        'graph': str(args.graph),
        'mode': mode,
        'renderer_command': renderer,
        'transport': transport_name,
        'dry_run': dry_run_actual,
        'board_id': result.get('board_id'),
        'item_count': result.get('item_count', 0),
        'summary': result.get('summary'),
    }))
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description='Miro story map render helpers')
    sub = p.add_subparsers(dest='cmd', required=True)

    r = sub.add_parser('render', help='Render story-graph.json onto a Miro board')
    r.add_argument('--mode', default='outline', help='outline | story-map | exploration | acceptance-criteria')
    r.add_argument('--graph', type=Path, required=True, help='Path to story-graph.json')
    r.add_argument('--board', help='Miro board id (omit with --dry-run)')
    r.add_argument(
        '--dry-run',
        action='store_true',
        help='Use InMemoryMiroTransport; nothing is sent to Miro.',
    )
    r.add_argument(
        '--resume',
        action='store_true',
        help=(
            'Resume from an existing checkpoint if one is found, even if status==complete. '
            'Skips board-clear and re-creates only missing items.'
        ),
    )
    r.add_argument('--scope', help='Optional story/epic/sub-epic name to filter graph')
    r.set_defaults(func=cmd_render)

    args = p.parse_args()
    return int(args.func(args))


if __name__ == '__main__':
    raise SystemExit(main())
