"""Ping the hook server, edit one example per fidelity, and check the injected rules."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

_PRACTICES = (
    "practices.agent_bdd.agent_bdd:AgentBdd",
    "practices.bdd.bdd:Bdd",
    "practices.cdd.cdd:Cdd",
    "practices.clean_engineering.clean_engineering:CleanEngineering",
    "practices.ddd.ddd:Ddd",
    "practices.stories.stories:Stories",
    "practices.ux.ux:Ux",
)
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


class HookExercise:
    """Touch one fidelity-named example and require that fidelity's rules in chat."""

    def __init__(self, repo: Path | str | None = None) -> None:
        self.repo = Path(repo or _REPO).resolve()

    def run(self) -> int:
        ping = self._ping()
        live = self._live_injects()
        checks = []
        for practice in self._practices():
            checks.extend(self._exercise_practice(practice))
        failed = [item for item in checks if not item["ok"]]
        report = {
            "ok": ping["ping"] == "pong" and live and not failed,
            "ping": ping["ping"],
            "host": ping.get("host"),
            "port": ping.get("port"),
            "live_injects": live,
            "checks": checks,
            "counts": {
                "checked": len(checks),
                "passed": len(checks) - len(failed),
                "failed": len(failed),
            },
        }
        json.dump(report, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0 if report["ok"] else 1

    def _ping(self) -> dict[str, Any]:
        from harness.hooks.hook_daemon import HookDaemon
        from harness.hooks.hook_server import HookServer

        address = HookDaemon().live_address(HookServer.state_path(self.repo))
        if address is None:
            return {"ping": "down"}
        host, port, pid = address
        return {"ping": "pong", "host": host, "port": port, "pid": pid}

    def _live_injects(self) -> bool:
        from harness.hooks.hook_server import HookServer

        sample = self._example_for("modules", "clean-engineering")
        if sample is None:
            return False
        try:
            result = HookServer.ensure(self.repo).handle_stdin(
                json.dumps(self._payload(sample)).encode("utf-8")
            )
        except Exception:
            return False
        return "domain-nouns-only" in (result.additional_context or "")

    def _server(self) -> Any:
        cached = getattr(self, "_hook_server", None)
        if cached is not None:
            return cached
        from harness.hooks.hook_server import HookServer

        self._hook_server = HookServer.from_handlers(
            self.repo / ".cursor" / "hook-handlers.json",
            repo=self.repo,
        )
        return self._hook_server

    def _payload(self, path: Path) -> dict[str, Any]:
        return {
            "hook_event_name": "postToolUse",
            "tool_name": "Write",
            "cwd": str(path.parent),
            "workspace_roots": [str(self.repo)],
            "tool_input": {"path": str(path)},
        }

    def _practices(self) -> list[Any]:
        from harness.agent_tools.agent_tools import AgentToolSet

        loaded = []
        for ref in _PRACTICES:
            practice = AgentToolSet.instantiate(ref)
            entries = getattr(getattr(practice, "fidelities", None), "entries", None) or {}
            if entries:
                loaded.append(practice)
        return loaded

    def _exercise_practice(self, practice: Any) -> list[dict[str, Any]]:
        checks = []
        fidelities = practice.fidelities
        for name in fidelities.entries:
            checks.append(
                self._exercise_fidelity(
                    practice,
                    fidelities[name],
                    name,
                    getattr(practice, "slug", None) or type(practice).__name__,
                )
            )
        return checks

    def _exercise_fidelity(
        self, practice: Any, fidelity: Any, name: str, practice_name: str
    ) -> dict[str, Any]:
        example = self._example_for(name, practice_name)
        slugs = self._rule_slugs(getattr(fidelity, "rules", None))
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
        except Exception as error:
            return {
                **base,
                "ok": False,
                "hook_fired": False,
                "error": f"{type(error).__name__}: {error}",
            }
        missing = [slug for slug in slugs if slug not in injected or slug not in chat]
        fired = True
        if not slugs:
            ok = bool(injected.strip())
            error = "" if ok else "hook returned no additional_context"
        else:
            ok = bool(injected.strip()) and not missing
            error = ""
            if not injected.strip():
                error = "hook returned no additional_context"
            elif missing:
                error = "injected chat is missing fidelity rules"
        return {
            **base,
            "ok": ok,
            "hook_fired": fired,
            "injected": bool(injected.strip()),
            "missing_rules": missing,
            "error": error,
        }

    def _fire(self, path: Path) -> tuple[str, str]:
        from harness.hooks.session_logs import SessionLogs

        result = self._server().handle_stdin(json.dumps(self._payload(path)).encode("utf-8"))
        injected = result.additional_context or ""
        logs = SessionLogs(self.repo)
        chat = logs.session_folder(logs.active_session_name()) / "last-chat-injected-rules.md"
        published = self.repo / ".cursor" / "rules" / "practices" / "chat-inject.mdc"
        chat_text = chat.read_text(encoding="utf-8") if chat.is_file() else ""
        published_text = published.read_text(encoding="utf-8") if published.is_file() else ""
        return injected, f"{chat_text}\n{published_text}"

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
        practices = self.repo / "practices"
        if practices.is_dir():
            roots.append(practices)
        return roots

    def _named_files(self, root: Path, needle: str, aliases: list[str]) -> list[Path]:
        found: list[Path] = []
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [name for name in dirnames if name not in _SKIP and not name.startswith(".")]
            folder = Path(dirpath)
            for name in filenames:
                path = folder / name
                posix = path.as_posix().casefold()
                in_examples = (
                    "/catalog/examples/" in posix
                    or "/examples/" in posix
                    or "/.examples/" in posix
                )
                if not in_examples or not self._named_for_fidelity(path, needle):
                    continue
                if not self._in_practice(path, aliases):
                    continue
                if path.stat().st_size > 1_000_000:
                    continue
                found.append(path)
        return found

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
        catalog = 0 if "/catalog/examples/" in posix else 1
        owned = 0 if self._in_practice(path, aliases) else 1
        return (catalog, owned, len(posix), posix)

    def _rule_slugs(self, rules: Any) -> list[str]:
        entries = getattr(rules, "entries", None) or {}
        slugs: list[str] = []
        for key, rule in entries.items():
            slug = str(getattr(rule, "slug", None) or key).strip()
            if slug and slug not in slugs:
                slugs.append(slug)
        return slugs

    def _touched(self, path: Path):
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
