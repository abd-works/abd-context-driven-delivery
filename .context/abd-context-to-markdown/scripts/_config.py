"""Shared config: ROOT, MEMORY, ASSETS for resolving relative paths.

Bootstrap is from the **abd-context-to-memory agent** (parent of ``skills/``), not other repos or bots.

**Config files** (loaded first; keys become process environment for the script run):

- ``<agent>/conf/.secrets`` — primary place for ``OPENAI_API_KEY`` and optional ``CONTENT_MEMORY_ROOT=``
- ``<agent>/conf/.env`` — same ``KEY=value`` format; then optional ``<this_skill>/.env``, ``cwd/.env``

**Topic root** ``ROOT`` (after loading config):

1. ``CONTENT_MEMORY_ROOT`` if set (usually **in** ``conf/.secrets``, not a shell export)
2. Current working directory — when you ``cd`` to your corpus before running scripts

**Per-run override:** pass ``--path`` / ``--memory`` / ``--rag`` where documented.

Orchestration and workspace policy: **[AGENTS.md](../../../AGENTS.md)**. Do not confuse with agile_bots
``WORKING_AREA``, MCP, or bot config.

Under ``ROOT``: ``markdown/`` (converted sources + **structural scan reports**), ``memory/`` (chunks,
``context_chunking_spec.yaml``, ``rag/`` for FAISS when embedded).
"""
import os
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
_SKILL_ROOT = _SCRIPTS.parent
_REPO_ROOT = _SKILL_ROOT.parent.parent

try:
    from dotenv import load_dotenv

    for p in (
        _REPO_ROOT / "conf" / ".secrets",
        _REPO_ROOT / "conf" / ".env",
        _SKILL_ROOT / ".env",
        Path.cwd() / ".env",
    ):
        if p.exists():
            load_dotenv(p, override=True)
except ImportError:
    pass


def _get_root() -> Path:
    if "CONTENT_MEMORY_ROOT" in os.environ and os.environ["CONTENT_MEMORY_ROOT"].strip():
        return Path(os.environ["CONTENT_MEMORY_ROOT"]).expanduser().resolve()
    return Path.cwd().resolve()


def ensure_root() -> None:
    """Exit if ROOT points at a missing path."""
    if not ROOT.exists():
        print("Memory path not found:", ROOT, file=sys.stderr)
        print(
            "Set CONTENT_MEMORY_ROOT in <agent>/conf/.secrets (or conf/.env), or cd to your topic/corpus folder before running scripts.",
            file=sys.stderr,
        )
        sys.exit(1)


ROOT = _get_root()
MEMORY = ROOT / "memory"
ASSETS = ROOT / "assets"
