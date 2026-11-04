"""Session-scoped hook log paths — always under ``.sessions/{name}/logs/``."""

from __future__ import annotations

import shutil
from datetime import date
from pathlib import Path


class SessionLogs:
    """Active session folder and hook runtime logs under the repo root."""

    ACTIVE = Path(".sessions") / "_active"
    LEGACY_ACTIVE = Path(".context") / "sessions" / "_active"
    MAIN_SESSION = "main"
    LEGACY_LOG_PATHS = (
        Path(".context") / "prompt-log.txt",
        Path("installation/hooks/dispatch.debug"),
        Path("harness/hooks/dispatch.debug"),
        Path("installation/hooks/prompt_notify.debug"),
        Path("tools/prompt_notify.debug"),
        Path("tools/prompt_notify/prompt_notify.debug"),
        Path("tools/prompt_log.debug"),
        Path("tools/prompt_log/prompt_log.debug"),
    )

    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root

    def write_active_session(self, name: str) -> None:
        slug = (name or "").strip() or self.MAIN_SESSION
        legacy_active = self.repo_root / self.LEGACY_ACTIVE
        if legacy_active.is_file():
            legacy_active.unlink()
        path = self.repo_root / self.ACTIVE
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(slug, encoding="utf-8")
        self.session_folder(slug).mkdir(parents=True, exist_ok=True)
        self.logs_dir_for(slug).mkdir(parents=True, exist_ok=True)

    def clear_active_session(self) -> None:
        path = self.repo_root / self.ACTIVE
        if path.is_file():
            path.unlink()

    def active_session_name(self) -> str:
        for rel in (self.ACTIVE, self.LEGACY_ACTIVE):
            path = self.repo_root / rel
            if path.is_file():
                text = path.read_text(encoding="utf-8").strip()
                if text:
                    return text
        return self.MAIN_SESSION

    def session_folder(self, name: str) -> Path:
        slug = (name or "").strip() or self.MAIN_SESSION
        dest = self.repo_root / ".sessions" / slug
        legacy = self.repo_root / ".context" / "sessions" / slug
        if legacy.is_dir() and not dest.exists():
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(legacy), str(dest))
        return dest

    def logs_dir_for(self, name: str) -> Path:
        return self.session_folder(name) / "logs"

    def ensure_main_session(self) -> Path:
        """Create ``.sessions/main/`` at repo root when no named session is active."""
        folder = self.session_folder(self.MAIN_SESSION)
        folder.mkdir(parents=True, exist_ok=True)
        self.logs_dir_for(self.MAIN_SESSION).mkdir(parents=True, exist_ok=True)
        session_md = folder / "session.md"
        if not session_md.is_file():
            session_md.write_text(self._main_session_markdown(), encoding="utf-8")
        return folder

    def _main_session_markdown(self) -> str:
        return "\n".join(
            [
                f"# Session: {self.MAIN_SESSION}",
                "",
                "## Start",
                "",
                f"- **date:** {date.today().isoformat()}",
                "- **note:** the session in use when no named work session is open",
                "",
            ]
        )

    def session_logs_dir(self) -> Path:
        active = self.repo_root / self.ACTIVE
        if active.is_file():
            name = self.active_session_name()
        else:
            self.ensure_main_session()
            name = self.MAIN_SESSION
        return self.logs_dir_for(name)

    def session_log_path(self, filename: str) -> Path:
        directory = self.session_logs_dir()
        directory.mkdir(parents=True, exist_ok=True)
        return directory / filename

    def consolidate_logs_for_close(self, session_name: str) -> None:
        """Move hook runtime logs into the session folder before archiving to closed."""
        slug = (session_name or "").strip() or self.MAIN_SESSION
        dest_logs = self.logs_dir_for(slug)
        dest_logs.mkdir(parents=True, exist_ok=True)
        self._move_main_logs_into(dest_logs)
        for rel in self.LEGACY_LOG_PATHS:
            self._move_log_into(self.repo_root / rel, dest_logs)
        self.clear_active_session()

    def _move_main_logs_into(self, dest_logs: Path) -> None:
        main_logs = self.logs_dir_for(self.MAIN_SESSION)
        if not main_logs.is_dir() or main_logs == dest_logs:
            return
        for item in list(main_logs.iterdir()):
            if item.is_file():
                self._move_log_into(item, dest_logs)
        if main_logs.is_dir() and not any(main_logs.iterdir()):
            main_logs.rmdir()

    def _move_log_into(self, file_path: Path, dest_logs: Path) -> None:
        if not file_path.is_file():
            return
        target = dest_logs / file_path.name
        if target.exists():
            target.unlink()
        try:
            shutil.move(str(file_path), str(target))
        except OSError:
            shutil.copy2(str(file_path), str(target))
            file_path.unlink(missing_ok=True)
