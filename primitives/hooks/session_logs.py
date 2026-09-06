"""Session-scoped hook log paths — always under ``.context/sessions/{name}/logs/``."""

from __future__ import annotations

import shutil
from datetime import date
from pathlib import Path

_ACTIVE = Path(".context") / "sessions" / "_active"
DEFAULT_SESSION = "default"

# Legacy repo-root paths removed on session close.
_LEGACY_LOG_PATHS = (
    Path(".context") / "prompt-log.txt",
    Path("primitives/hooks/dispatch.debug"),
    Path("primitives/hooks/skill_inject.debug"),
    Path("primitives/hooks/prompt_echo.debug"),
    Path("primitives/hooks/prompt_echo/prompt_echo.debug"),
)


def write_active_session(repo_root: Path, name: str) -> None:
    slug = (name or "").strip() or DEFAULT_SESSION
    path = repo_root / _ACTIVE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(slug, encoding="utf-8")
    session_folder(repo_root, slug).mkdir(parents=True, exist_ok=True)
    session_logs_dir_for(repo_root, slug).mkdir(parents=True, exist_ok=True)


def clear_active_session(repo_root: Path) -> None:
    path = repo_root / _ACTIVE
    if path.is_file():
        path.unlink()


def active_session_name(repo_root: Path) -> str:
    path = repo_root / _ACTIVE
    if path.is_file():
        text = path.read_text(encoding="utf-8").strip()
        if text:
            return text
    return DEFAULT_SESSION


def session_folder(repo_root: Path, name: str) -> Path:
    return repo_root / ".context" / "sessions" / name


def session_logs_dir_for(repo_root: Path, name: str) -> Path:
    return session_folder(repo_root, name) / "logs"


def ensure_default_session(repo_root: Path) -> Path:
    """Create ``.context/sessions/default/`` at repo root when no session is active."""
    folder = session_folder(repo_root, DEFAULT_SESSION)
    folder.mkdir(parents=True, exist_ok=True)
    session_logs_dir_for(repo_root, DEFAULT_SESSION).mkdir(parents=True, exist_ok=True)
    session_md = folder / "session.md"
    if not session_md.is_file():
        session_md.write_text(
            "\n".join(
                [
                    f"# Session: {DEFAULT_SESSION}",
                    "",
                    "## Start",
                    "",
                    f"- **date:** {date.today().isoformat()}",
                    "- **note:** implicit default — no named work session open",
                    "",
                ]
            ),
            encoding="utf-8",
        )
    return folder


def session_logs_dir(repo_root: Path) -> Path:
    active = repo_root / _ACTIVE
    if active.is_file():
        name = active_session_name(repo_root)
    else:
        ensure_default_session(repo_root)
        name = DEFAULT_SESSION
    return session_logs_dir_for(repo_root, name)


def session_log_path(repo_root: Path, filename: str) -> Path:
    directory = session_logs_dir(repo_root)
    directory.mkdir(parents=True, exist_ok=True)
    return directory / filename


def consolidate_logs_for_close(repo_root: Path, session_name: str) -> None:
    """Move hook runtime logs into the session folder before archiving to closed."""
    slug = (session_name or "").strip() or DEFAULT_SESSION
    dest_logs = session_logs_dir_for(repo_root, slug)
    dest_logs.mkdir(parents=True, exist_ok=True)

    def _move_into(file_path: Path) -> None:
        if not file_path.is_file():
            return
        target = dest_logs / file_path.name
        try:
            if target.exists():
                target.unlink()
            shutil.move(str(file_path), str(target))
        except OSError:
            try:
                shutil.copy2(str(file_path), str(target))
                file_path.unlink(missing_ok=True)
            except OSError:
                pass

    default_logs = session_logs_dir_for(repo_root, DEFAULT_SESSION)
    if default_logs.is_dir() and default_logs != dest_logs:
        for item in list(default_logs.iterdir()):
            if item.is_file():
                _move_into(item)
        try:
            if default_logs.is_dir() and not any(default_logs.iterdir()):
                default_logs.rmdir()
        except OSError:
            pass

    for rel in _LEGACY_LOG_PATHS:
        _move_into(repo_root / rel)

    clear_active_session(repo_root)


def wipe_session_logs(repo_root: Path) -> None:
    """Legacy name — close uses ``consolidate_logs_for_close`` instead."""
    consolidate_logs_for_close(repo_root, active_session_name(repo_root))
