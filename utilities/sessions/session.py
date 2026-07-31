"""Named sprint session under ``{path}/.context/sessions/{name}/``."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path


def docs_dir(destination: str | Path) -> Path:
    """Resolve where process docs live for a destination.

    - Sprint folder (``.../.context/sessions/{name}``) -> write flat into that folder
    - Working area or module root -> ``{destination}/.context/``
    """
    dest = Path(destination)
    if dest.name and dest.parent.name == "sessions":
        return dest
    return dest / ".context"


class ISession(ABC):
    """Sprint: durable ``path``, process docs in ``folder``, event logs in ``log``."""

    # Identity fields - concrete on Session (dataclass); listed here for the interface surface.
    path: str
    name: str | None

    @property
    @abstractmethod
    def folder(self) -> Path: ...

    @property
    @abstractmethod
    def log(self) -> Path: ...

    @property
    @abstractmethod
    def session_md(self) -> Path: ...

    @classmethod
    @abstractmethod
    def load(cls, path: str, name: str) -> ISession: ...

    @abstractmethod
    def ensure_started(
        self,
        *,
        goal: str = "",
        fidelities: str = "",
        contexts: str = "",
    ) -> Path: ...

    @abstractmethod
    def close(self, *, outcome: str = "", handoff: str = "handoff.md") -> Path: ...

    @abstractmethod
    def to_dict(self) -> dict[str, str | None]: ...


@dataclass
class Session(ISession):
    """Current sprint: durable root is ``path``; process docs live in ``folder``."""

    path: str
    name: str | None = None
    goal: str = ""
    fidelities: str = ""
    contexts: str = ""
    started: str = field(default_factory=lambda: date.today().isoformat())
    ended: str = ""
    outcome: str = ""
    handoff: str = ""

    @property
    def folder(self) -> Path:
        if not self.name:
            raise ValueError(
                "session name is not set - confirm working path and session slug with the "
                "user, then call create_session before grill/sketch/handoff"
            )
        return Path(self.path) / ".context" / "sessions" / self.name

    @property
    def log(self) -> Path:
        """Directory for append-only session event logs."""
        return self.folder / "logs"

    @property
    def session_md(self) -> Path:
        return self.folder / "session.md"

    def to_dict(self) -> dict[str, str | None]:
        folder: str | None
        try:
            folder = str(self.folder)
        except ValueError:
            folder = None
        return {
            "path": self.path,
            "name": self.name,
            "folder": folder,
            "goal": self.goal or None,
            "fidelities": self.fidelities or None,
            "contexts": self.contexts or None,
            "started": self.started or None,
            "ended": self.ended or None,
            "outcome": self.outcome or None,
            "handoff": self.handoff or None,
        }

    def __repr__(self) -> str:
        return f"Session(path={self.path!r}, name={self.name!r})"

    @classmethod
    def load(cls, path: str, name: str) -> Session:
        """Load from ``{path}/.context/sessions/{name}/session.md`` when present."""
        session = cls(path=path, name=name)
        md = session.session_md
        if not md.is_file():
            return session
        return cls._parse(md.read_text(encoding="utf-8"), path=path, name=name)

    def ensure_started(
        self,
        *,
        goal: str = "",
        fidelities: str = "",
        contexts: str = "",
    ) -> Path:
        """Create sprint folder + session.md Start when missing; refresh fields if provided."""
        if not self.name:
            raise ValueError("session name is required to create a sprint folder")
        if goal:
            self.goal = goal
        if fidelities:
            self.fidelities = fidelities
        if contexts:
            self.contexts = contexts
        if not self.started:
            self.started = date.today().isoformat()
        self.folder.mkdir(parents=True, exist_ok=True)
        if not self.session_md.is_file():
            self.session_md.write_text(self._render(), encoding="utf-8")
        elif goal or fidelities or contexts:
            if not self.ended:
                self.session_md.write_text(self._render(), encoding="utf-8")
        return self.session_md

    def close(self, *, outcome: str = "", handoff: str = "handoff.md") -> Path:
        """Write End section (and handoff link) into session.md."""
        if not self.session_md.is_file():
            self.ensure_started()
        self.ended = date.today().isoformat()
        if handoff:
            self.handoff = handoff
        if not outcome and self.handoff:
            outcome = "handoff written"
        if outcome:
            self.outcome = outcome
        self.session_md.write_text(self._render(), encoding="utf-8")
        return self.session_md

    def _render(self) -> str:
        lines = [
            f"# Session: {self.name}",
            "",
            "## Start",
            "",
            f"- **date:** {self.started}",
            f"- **path:** {self.path}",
            f"- **goal:** {self.goal or '(unset)'}",
            f"- **fidelities:** {self.fidelities or '(unset)'}",
            f"- **contexts:** {self.contexts or '(unset)'}",
            "",
        ]
        if self.ended or self.outcome or self.handoff:
            lines.extend(
                [
                    "## End",
                    "",
                    f"- **ended:** {self.ended or '(unset)'}",
                    f"- **outcome:** {self.outcome or '(unset)'}",
                    f"- **handoff:** {self.handoff or '(unset)'}",
                    "",
                ]
            )
        return "\n".join(lines)

    @classmethod
    def _parse(cls, text: str, *, path: str, name: str) -> Session:
        fields: dict[str, str] = {}
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped.startswith("- **") or ":**" not in stripped:
                continue
            key, _, value = stripped.partition(":**")
            key = key.removeprefix("- **").strip()
            value = value.strip()
            if value.startswith("(") and value.endswith(")"):
                value = ""
            fields[key] = value
        return cls(
            path=fields.get("path") or path,
            name=name,
            goal=fields.get("goal", ""),
            fidelities=fields.get("fidelities", ""),
            contexts=fields.get("contexts", ""),
            started=fields.get("date", "") or date.today().isoformat(),
            ended=fields.get("ended", ""),
            outcome=fields.get("outcome", ""),
            handoff=fields.get("handoff", ""),
        )
