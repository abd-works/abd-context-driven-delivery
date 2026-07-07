"""Sync stories/ → .cursor/skills/stories/ before an eval run.

The deployed copy is what cursor-agent auto-loads. Without this sync, an eval
run tests a stale snapshot of the skill instead of the developer's latest.
"""

from __future__ import annotations

import shutil
from pathlib import Path


_ABD_SKILLS_ROOT = Path(__file__).resolve().parents[2]  # stories/src/ → stories/ → repo root
_STORIES_SOURCE = _ABD_SKILLS_ROOT / "stories"
_STORIES_DEPLOY = _ABD_SKILLS_ROOT / ".cursor" / "skills" / "stories"

_EXCLUDED_SUBPATHS = (
    "evals",              # never deploy the eval cases into the running skill
    "rules",              # skip fixture data under rules/<name>/evals/ too — see filter below
    "__pycache__",
    ".pytest_cache",
)


def deploy_stories_skill() -> Path:
    """Copy stories/ to .cursor/skills/stories/, replacing the previous deploy.

    Excludes coarse-eval cases and per-rule fixture data — the deployed skill
    ships rule.md and scanner.py but not evals/pass|fail data.
    Returns the deploy destination path.
    """
    if _STORIES_DEPLOY.exists():
        shutil.rmtree(_STORIES_DEPLOY)
    _STORIES_DEPLOY.mkdir(parents=True, exist_ok=True)

    for source in _STORIES_SOURCE.rglob("*"):
        relative = source.relative_to(_STORIES_SOURCE)
        if _is_excluded(relative):
            continue
        target = _STORIES_DEPLOY / relative
        if source.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)

    return _STORIES_DEPLOY


def _is_excluded(relative: Path) -> bool:
    parts = relative.parts
    if not parts:
        return False
    # Top-level evals/ folder
    if parts[0] == "evals":
        return True
    if "__pycache__" in parts:
        return True
    if ".pytest_cache" in parts:
        return True
    # rules/<name>/evals/... — skip fixture data, keep rule.md + scanner.py
    if len(parts) >= 3 and parts[0] == "rules" and parts[2] == "evals":
        return True
    return False


if __name__ == "__main__":
    dest = deploy_stories_skill()
    print(f"deployed stories → {dest}")
