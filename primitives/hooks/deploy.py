"""Hook deploy metadata — skill payloads for harness; dispatch wiring for hooks.json."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from hooks.hook import Hook, HookHarness

DISPATCH_SCRIPT = "primitives/hooks/dispatch.py"


@dataclass(frozen=True)
class HookBinding:
    """One ``@hook`` operation discovered during harness deploy."""

    event: str
    operation: str
    slug: str = ""
    owner: str = ""
    folder: str = ""

    @classmethod
    def from_source(cls, source: dict) -> HookBinding:
        return cls(
            event=str(source.get("event") or ""),
            operation=str(source.get("operation") or ""),
            slug=str(source.get("slug") or source.get("name") or ""),
            owner=str(source.get("owner") or ""),
            folder=str(source.get("folder") or ""),
        )

    def deploy_slug(self) -> str:
        """Hook toggle skill prefix — the ``@hook`` operation name."""
        return self.operation or self.slug

    def event_suffix(self) -> str:
        return Hook.normalize_event(self.event)

    def toggle_flag(self) -> Path:
        owner_slug = self.owner.lower() if self.owner else "toolset"
        return Path(".context") / "hooks" / owner_slug / f"{self.operation}_{self.event_suffix()}.enabled"

    def skill_name(self, *, enabled: bool) -> str:
        suffix = "on" if enabled else "off"
        return f"{self.deploy_slug()}_{self.event_suffix()}_{suffix}"

    def overview(self, *, enabled: bool) -> str:
        verb = "Enable" if enabled else "Disable"
        return (
            f"{verb} `{self.deploy_slug()}` hook on "
            f"`{self.event}` ({self.event_suffix().replace('_', ' ')}) "
            f"for {self.owner or 'toolset'}."
        )

    def instructions(self, *, enabled: bool) -> str:
        verb = "Enable" if enabled else "Disable"
        flag = self.toggle_flag()
        body = (
            f"{verb} the `{self.deploy_slug()}` hook on Cursor event `{self.event}`.\n\n"
            f"Flag file: `{flag.as_posix()}`\n"
        )
        if enabled:
            body += (
                "\nCreate the flag file (empty is fine). The hook dispatcher runs "
                f"`{self.operation}` when this flag exists.\n"
            )
        else:
            body += "\nRemove the flag file so the dispatcher skips this handler.\n"
        return body

    def skill_sources(self) -> list[dict]:
        """Return harness skill payloads for on/off toggle skills."""
        return [
            {
                "name": self.skill_name(enabled=enabled),
                "overview": self.overview(enabled=enabled),
                "body": self.instructions(enabled=enabled),
                "folder": self.folder,
            }
            for enabled in (True, False)
        ]


def hook_skill_sources(source: dict) -> tuple[list[dict], set[str]]:
    """Skill payloads for harness to place; Cursor events to wire in hooks.json."""
    binding = HookBinding.from_source(source)
    events = {binding.event} if binding.event else set()
    return binding.skill_sources(), events


def deploy_dispatch(repo_root: Path, events: set[str]) -> None:
    """Sync ``dispatch.py`` entries in ``.cursor/hooks.json`` to *events* only."""
    HookHarness(script=DISPATCH_SCRIPT).sync_dispatch(
        repo_root / ".cursor" / "hooks.json",
        events,
    )
