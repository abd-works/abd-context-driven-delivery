"""Ping the hook server, edit one example per fidelity, and check the injected rules."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

if TYPE_CHECKING:
    from harness.guidance.guidance import FidelityGuidance, PracticeGuidance
    from harness.guidance.rule import RulesCollection
    from harness.hooks.hook_server import HookServer

_SKIP = {
    ".git",
    ".venv",
    "__pycache__",
    "node_modules",
    ".codeql",
}
_TEXT_SUFFIXES = {
    ".md",
    ".mdc",
    ".py",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".html",
    ".drawio",
    ".json",
    ".txt",
    ".yml",
    ".yaml",
}


CheckReport = dict[str, Any]
"""One JSON entry of the exercise report, as written to stdout."""

_LARGEST_EXAMPLE_BYTES = 1_000_000
"""Examples bigger than this are generated data, not a hand-written example worth touching."""


class HookExercise:
    """Touch one fidelity-named example and require that fidelity's rules in chat."""

    def __init__(self, repo: Path | str | None = None) -> None:
        self.repo = Path(repo or _REPO).resolve()
        self._hook_server: HookServer | None = None

    def run(self) -> int:
        ping = self._ping()
        live = self._live_injects()
        checks = [check for practice in self._practices() for check in self._exercise_practice(practice)]
        report = self._report(ping, live, checks)
        json.dump(report, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0 if report["ok"] else 1

    def _report(self, ping: CheckReport, live: CheckReport, checks: list[CheckReport]) -> CheckReport:
        failed = [item for item in checks if not item["ok"]]
        return {
            "ok": ping["ping"] == "pong" and live["live_injects"] and not failed,
            "ping": ping["ping"],
            "host": ping.get("host"),
            "port": ping.get("port"),
            **live,
            "checks": checks,
            "counts": {"checked": len(checks), "passed": len(checks) - len(failed), "failed": len(failed)},
        }

    def _ping(self) -> CheckReport:
        from harness.hooks.hook_daemon import HookDaemon

        address = HookDaemon(self.repo).live_address()
        if address is None:
            return {"ping": "down"}
        return {"ping": "pong", "host": address.host, "port": address.port, "pid": address.pid}

    def _live_injects(self) -> CheckReport:
        """Whether the running hook daemon injects a fidelity's rules, with the reason when it could not be asked."""
        from harness.hooks.hook_daemon import HookDaemon, HookDaemonUnavailable

        sample = self._example_for("modules", "clean-engineering")
        if sample is None:
            return {"live_injects": False, "live_error": "no clean-engineering modules example found"}
        try:
            result = HookDaemon(self.repo).ensure().handle_stdin(json.dumps(self._payload(sample)).encode("utf-8"))
        except (HookDaemonUnavailable, OSError) as error:
            return {"live_injects": False, "live_error": f"{type(error).__name__}: {error}"}
        return {"live_injects": "domain-nouns-only" in (result.get("additional_context") or "")}

    def _server(self) -> HookServer:
        if self._hook_server is None:
            from harness.hooks.hook_server import HookServer

            self._hook_server = HookServer.from_handlers(self.repo / ".cursor" / "hook-handlers.json", repo=self.repo)
        return self._hook_server

    def _payload(self, path: Path) -> CheckReport:
        return {
            "hook_event_name": "postToolUse",
            "tool_name": "Write",
            "cwd": str(path.parent),
            "workspace_roots": [str(self.repo)],
            "conversation_id": "hook-exercise",
            "tool_input": {"path": str(path)},
        }

    def _practices(self) -> list[PracticeGuidance]:
        """Every installed practice with fidelities, found the way the installer finds toolsets."""
        from harness.agent_tools.agent_tools import AgentToolSet
        from harness.guidance.guidance import PracticeGuidance
        from harness.installation.repository_toolsets import RepositoryToolsets

        practice_classes = [
            toolset for toolset in RepositoryToolsets(self.repo).classes() if issubclass(toolset, PracticeGuidance)
        ]
        practices = [AgentToolSet.instantiate(toolset) for toolset in practice_classes]
        return [practice for practice in practices if practice.fidelities.entries]

    def _exercise_practice(self, practice: PracticeGuidance) -> list[CheckReport]:
        practice_name = getattr(practice, "slug", None) or type(practice).__name__
        fidelities = practice.fidelities
        return [self._exercise_fidelity(practice_name, name, fidelities[name]) for name in fidelities.entries]

    def _exercise_fidelity(self, practice_name: str, name: str, fidelity: FidelityGuidance) -> CheckReport:
        example = self._example_for(name, practice_name)
        slugs = self._rule_slugs(fidelity.rules)
        base = {
            "practice": practice_name,
            "fidelity": name,
            "example": str(example) if example is not None else "",
            "expected_rules": slugs,
        }
        if example is None:
            return {**base, "ok": False, "hook_fired": False, "error": "no example file named for this fidelity"}
        try:
            with self._touched(example):
                injected, chat = self._fire(example)
        except OSError as error:
            return {**base, "ok": False, "hook_fired": False, "error": f"{type(error).__name__}: {error}"}
        return {**base, **self._injection_outcome(slugs, injected, chat)}

    def _injection_outcome(self, slugs: list[str], injected: str, chat: str) -> CheckReport:
        """Whether the hook injected anything and, when the fidelity has rules, whether every one reached the chat."""
        missing = [slug for slug in slugs if slug not in injected or slug not in chat]
        error = ""
        if not injected.strip():
            error = "hook returned no additional_context"
        elif missing:
            error = "injected chat is missing fidelity rules"
        return {
            "ok": not error,
            "hook_fired": True,
            "injected": bool(injected.strip()),
            "missing_rules": missing,
            "error": error,
        }

    def _fire(self, path: Path) -> tuple[str, str]:
        from space.session.sessions import Sessions

        result = self._server().handle_stdin(json.dumps(self._payload(path)).encode("utf-8"))
        injected = result.additional_context or ""
        folder = Sessions(self.repo).current().work_folder
        chat = folder / "last-chat-injected-rules.md"
        remembered = folder / "chat-injections" / "hook-exercise.md"
        chat_text = chat.read_text(encoding="utf-8") if chat.is_file() else ""
        remembered_text = remembered.read_text(encoding="utf-8") if remembered.is_file() else ""
        return injected, f"{chat_text}\n{remembered_text}"

    def _example_for(self, fidelity: str, practice: str) -> Path | None:
        needle = fidelity.casefold().replace("_", "-")
        aliases = self._practice_aliases(practice)
        matches = [
            path
            for root in self._search_roots()
            for path in self._named_files(root, needle, aliases)
        ]
        if not matches:
            return None
        return sorted(matches, key=lambda path: self._rank(path, aliases))[0]

    def _search_roots(self) -> list[Path]:
        roots: list[Path] = []
        parent = self.repo.parent
        if parent.is_dir():
            for child in sorted(parent.iterdir()):
                catalog = child / "catalog" / "examples"
                if catalog.is_dir():
                    roots.append(catalog)
        local = self.repo / "catalog" / "examples"
        if local.is_dir() and local not in roots:
            roots.append(local)
        practices = self.repo / "cdd_guidance" / "practices"
        if practices.is_dir():
            roots.append(practices)
        return roots

    def _named_files(self, root: Path, needle: str, aliases: list[str]) -> list[Path]:
        found: list[Path] = []
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [name for name in dirnames if name not in _SKIP and not name.startswith(".")]
            folder = Path(dirpath)
            found.extend(
                folder / name for name in filenames if self._is_fidelity_example(folder / name, needle, aliases)
            )
        return found

    def _is_fidelity_example(self, path: Path, needle: str, aliases: list[str]) -> bool:
        posix = path.as_posix().casefold()
        in_examples = "/catalog/_examples/" in posix or "/examples/" in posix or "/_examples/" in posix
        return (
            in_examples
            and self._named_for_fidelity(path, needle)
            and self._in_practice(path, aliases)
            and path.stat().st_size <= _LARGEST_EXAMPLE_BYTES
        )

    def _named_for_fidelity(self, path: Path, needle: str) -> bool:
        stem = path.stem.casefold().replace("_", "-")
        start = 0
        while True:
            found = stem.find(needle, start)
            if found < 0:
                return False
            end = found + len(needle)
            before = found == 0 or not stem[found - 1].isalnum()
            after = end == len(stem) or not stem[end].isalnum()
            if before and after:
                return True
            start = found + 1

    def _in_practice(self, path: Path, aliases: list[str]) -> bool:
        parts = {part.casefold().replace("_", "-") for part in path.parts}
        return any(alias in parts for alias in aliases)

    def _practice_aliases(self, practice: str) -> list[str]:
        folded = practice.casefold().replace("_", "-")
        return list(dict.fromkeys((folded, folded.replace("-", "_"))))

    def _rank(self, path: Path, aliases: list[str]) -> tuple[int, int, str]:
        posix = path.as_posix().casefold()
        catalog = 0 if "/catalog/_examples/" in posix else 1
        owned = 0 if self._in_practice(path, aliases) else 1
        return (catalog, owned, len(posix), posix)

    def _rule_slugs(self, rules: RulesCollection) -> list[str]:
        entries = rules.entries or {}
        slugs: list[str] = []
        for key, rule in entries.items():
            slug = str(getattr(rule, "slug", None) or key).strip()
            if slug and slug not in slugs:
                slugs.append(slug)
        return slugs

    def _touched(self, path: Path) -> _FileTouch:
        return _FileTouch(path)


class _FileTouch:
    """Append a newline to a text example, then put the original bytes back."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self._original = b""

    def __enter__(self) -> Path:
        self._original = self.path.read_bytes()
        suffix = self.path.suffix.casefold()
        if suffix in _TEXT_SUFFIXES:
            self.path.write_bytes(self._original + b"\n")
        else:
            os.utime(self.path, None)
        return self.path

    def __exit__(self, *args: object) -> None:
        self.path.write_bytes(self._original)


if __name__ == "__main__":
    raise SystemExit(HookExercise().run())
