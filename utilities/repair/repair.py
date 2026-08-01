"""Repair kit - record failures; when repairing, fix root cause."""

from __future__ import annotations

from datetime import date

from primitives.actions.action import action
from tools.tool import tool


class Repair:
    """log_fix records; repair fixes root cause. Same kit."""

    @tool
    def write_to_fix(
        self,
        artifact: str,
        rule: str,
        wrong: str,
        original: str,
        improved: str,
        status: str = "fixed",
        when: str = "",
    ) -> str:
        """Append one entry to ``{session.folder}/to-fix.log``."""
        folder = self._session.folder
        path = folder / "to-fix.log"
        folder.mkdir(parents=True, exist_ok=True)
        if not path.is_file():
            sprint = self._session.name or "session"
            path.write_text(
                f"# to-fix.log - {sprint} sprint\n"
                "# Log omissions/errors here. Each entry:\n"
                "#   when, artifact, rule, wrong (one line), original, improved\n"
                '# User phrase "to fix" = failed to do it right; '
                "fix immediately and append an entry.\n\n",
                encoding="utf-8",
            )

        def block(text: str) -> str:
            return "\n".join(
                f"  {line}"
                for line in text.replace("\r\n", "\n").rstrip("\n").split("\n")
            )

        entry = (
            "---\n"
            f"when: {when.strip() or date.today().isoformat()}\n"
            f"artifact: {artifact.strip()}\n"
            f"rule: {rule.strip()}\n"
            f"wrong: {' '.join(wrong.strip().splitlines())}\n"
            "original: |\n"
            f"{block(original)}\n"
            "improved: |\n"
            f"{block(improved)}\n"
            f"status: {status.strip() or 'fixed'}\n"
            "---\n"
        )
        existing = path.read_text(encoding="utf-8")
        sep = "" if existing.endswith("\n\n") else "\n" if existing.endswith("\n") else "\n\n"
        path.write_text(existing + sep + entry, encoding="utf-8")
        return str(path.resolve())

    @action
    def log_fix(
        self,
        artifact: str = "",
        rule: str = "",
        wrong: str = "",
        original: str = "",
        improved: str = "",
        status: str = "fixed",
    ) -> str:
        """log_fix"""
        self.active
        self.write_to_fix()
        return (
            "After correcting the failure, entry is in {session.folder}/to-fix.log "
            "({{artifact}} / {{rule}})."
        )

    @action
    def repair(self, asset: str, violation: str) -> str:
        """repair"""
        self.active
        self.scan()
        self.contexts
        self.examples
        self.templates
        self.validate()
        return "Repair {{asset}} under {session.path}/ until validate passes."
