"""Structured eval trace — append only what matters to ``run.txt``."""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_TRACE_MARKER = ".stories-skill-trace"
_FLAG_RE = re.compile(r"--([a-z-]+)(?:=|\s+)(\"[^\"]*\"|\S+)")

_manifest_paths: set[str] = set()
_logged_assemble_keys: set[str] = set()
_logged_reads: set[str] = set()
_trace_file: Path | None = None
_trace_echo: bool = False


def set_trace_file(path: Path | str | None) -> None:
    global _trace_file
    _trace_file = Path(path) if path else None


def set_trace_echo(enabled: bool) -> None:
    global _trace_echo
    _trace_echo = enabled


def resolve_trace_path() -> Path | None:
    if _trace_file is not None:
        return _trace_file
    raw = os.environ.get("STORIES_SKILL_TRACE", "").strip()
    if raw:
        return Path(raw)
    marker = Path.cwd() / _TRACE_MARKER
    if marker.is_file():
        try:
            text = marker.read_text(encoding="utf-8").strip()
        except OSError:
            return None
        if text:
            return Path(text)
    return None


def append_block(title: str, body: str, *, path: Path | str | None = None) -> None:
    target = Path(path) if path is not None else resolve_trace_path()
    if target is None:
        return
    stamp = datetime.now(timezone.utc).isoformat()
    block = f"\n=== {title} [{stamp}] ===\n{body.rstrip()}\n"
    try:
        with target.open("a", encoding="utf-8") as handle:
            handle.write(block)
            handle.flush()
    except OSError:
        pass
    if _trace_echo:
        if title == "GENERATED" and len(body) > 800:
            sys.stdout.write(f"\n=== {title} ===\n({len(body)} chars → run.txt)\n")
        else:
            sys.stdout.write(block)
        sys.stdout.flush()


def emit_progress(line: str) -> None:
    """One-line live progress on console (always when echo on)."""
    if not _trace_echo:
        return
    sys.stdout.write(line.rstrip() + "\n")
    sys.stdout.flush()


def extract_flag(command: str, flag: str) -> str | None:
    for match in _FLAG_RE.finditer(command):
        if match.group(1) == flag:
            return match.group(2).strip("\"'")
    return None


def _normalize_manifest_path(path: str) -> str:
    return path.replace("\\", "/").lstrip("./")


def register_manifest(manifest: dict[str, Any]) -> None:
    global _manifest_paths
    paths: set[str] = set()
    for paths_list in (manifest.get("files_by_directory") or {}).values():
        for rel in paths_list:
            paths.add(_normalize_manifest_path(str(rel)))
    _manifest_paths = paths


def classify_read_path(path: str) -> str:
    norm = path.replace("\\", "/").lower()
    if "/evals/" in norm and "/expected/" in norm:
        return "eval-leak"
    if "/context/brief" in norm or norm.endswith("context/brief.md"):
        return "context"
    if norm.endswith("/skill.md") or "skill-workflow" in norm:
        return "bootstrap"
    tail = norm.split("/stories/", 1)[-1] if "/stories/" in norm else Path(path).name.lower()
    for manifest_rel in _manifest_paths:
        m = manifest_rel.lower()
        if tail == m or tail.endswith("/" + m) or norm.endswith("/" + m):
            return "generate-input"
        if Path(manifest_rel).name.lower() == Path(path).name.lower() and m in norm:
            return "generate-input"
    return "explore"


def should_log_read(path: str) -> bool:
    return classify_read_path(path) in (
        "generate-input",
        "context",
        "bootstrap",
        "eval-leak",
    )


def _display_path(path: str) -> str:
    normalized = path.replace("/", "\\")
    for needle in ("\\workspace-", "\\workspace\\"):
        if needle in normalized:
            tail = normalized.split(needle, 1)[1]
            parts = tail.split("\\", 1)
            if len(parts) == 2 and parts[1]:
                return parts[1].replace("\\", "/")
    if "/stories/" in path.replace("\\", "/"):
        return path.replace("\\", "/").split("/stories/", 1)[1]
    return Path(path).name


def log_read(path: str, *, path_hint: Path | str | None = None) -> None:
    """Log a meaningful read once (assembled MD, context, bootstrap)."""
    key = _normalize_manifest_path(_display_path(path))
    if key in _logged_reads:
        return
    category = classify_read_path(path)
    if category == "explore":
        return
    _logged_reads.add(key)
    labels = {
        "generate-input": "assembled",
        "context": "context",
        "bootstrap": "bootstrap",
        "eval-leak": "⚠ expected (leak)",
    }
    label = labels[category]
    display = _display_path(path)
    line = f"  READ  {label}: {display}\n"
    target = Path(path_hint) if path_hint is not None else resolve_trace_path()
    if target is not None:
        try:
            with target.open("a", encoding="utf-8") as handle:
                handle.write(line)
                handle.flush()
        except OSError:
            pass
    if _trace_echo:
        sys.stdout.write(line)
        sys.stdout.flush()


def _manifest_summary(manifest: dict[str, Any]) -> list[str]:
    files_by_dir = manifest.get("files_by_directory") or {}
    lines: list[str] = []
    total = 0
    for directory, paths in sorted(files_by_dir.items()):
        for rel in sorted(paths):
            lines.append(f"  - {rel}")
            total += 1
    lines.insert(0, f"reading list ({total} files):")
    return lines


def _assemble_key(params: dict[str, str]) -> str:
    return "|".join(params.get(k, "") for k in ("phase", "fidelity", "format"))


def log_assemble_call(
    *,
    params: dict[str, str],
    manifest: dict[str, Any] | None,
    command: str,
    path: Path | str | None = None,
) -> None:
    key = _assemble_key(params)
    if key in _logged_assemble_keys:
        return
    _logged_assemble_keys.add(key)
    fidelity = params.get("fidelity", "?")
    fmt = params.get("format", "?")
    phase = params.get("phase", "?")
    if manifest is None:
        body = f"{fidelity}/{fmt}/{phase}  (not captured)"
    else:
        if manifest.get("phase") == "generate":
            register_manifest(manifest)
        summary = _manifest_summary(manifest)
        body = f"{fidelity}/{fmt}/{phase}\n" + "\n".join(summary)
    append_block("ASSEMBLE", body, path=path)


def log_stories_cli_call(
    *,
    command: str,
    params: dict[str, str],
    written: list[str] | None = None,
    output: str | None = None,
    exit_code: int | None = None,
    path: Path | str | None = None,
) -> None:
    lines = [f"$ {command.strip()}", "params:"]
    lines.extend(f"  --{k} {v}" for k, v in params.items())
    if exit_code is not None:
        lines.append(f"exit: {exit_code}")
    if written:
        lines.append("written:")
        lines.extend(f"  - {w}" for w in written)
    if output and output.strip():
        lines.append("stdout:")
        lines.append(output.strip()[:2000])
    append_block("STORIES CLI", "\n".join(lines), path=path)


def log_scanner_call(
    *,
    command: str,
    exit_code: int,
    violations: list[dict] | None = None,
    scanner_names: list[str] | None = None,
    per_scanner: list[tuple[str, str, str]] | None = None,
    path: Path | str | None = None,
) -> None:
    v = violations or []
    overall = "PASS" if not v and exit_code == 0 else "FAIL"
    lines: list[str] = []

    if per_scanner:
        for name, tag, reason in per_scanner:
            if tag in ("SKIP", "NO_SCANNER"):
                lines.append(f"  {name}: {tag}" + (f"  ({reason})" if reason else ""))
            elif tag == "FAIL":
                lines.append(f"  {name}: FAIL" + (f"  — {reason}" if reason else ""))
            else:
                lines.append(f"  {name}: PASS")
        n_pass = sum(1 for _, t, _ in per_scanner if t == "PASS")
        n_fail = sum(1 for _, t, _ in per_scanner if t == "FAIL")
        n_skip = sum(1 for _, t, _ in per_scanner if t in ("SKIP", "NO_SCANNER"))
        lines.append(f"→ {'PASS' if n_fail == 0 else 'FAIL'}  ({n_pass} pass, {n_fail} fail, {n_skip} skip/no-scanner)")
    elif scanner_names:
        # Names extracted from command, overall result only
        for name in scanner_names:
            lines.append(f"{name}: {overall}")
        # Per-violation detail for any recorded violations
        for item in v[:8]:
            rule = item.get("rule", item.get("source", "?"))
            msg = item.get("message", item.get("stderr_tail", str(item)))
            loc = item.get("location", "")
            suffix = f"  [{loc}]" if loc else ""
            lines.append(f"  FAIL {rule}: {msg}{suffix}")
        if len(v) > 8:
            lines.append(f"  … and {len(v) - 8} more")
    else:
        lines.append(f"$ {command.strip()}")
        lines.append(f"→ {overall}  ({len(v)} violation(s))")

    append_block("SCANNER", "\n".join(lines), path=path)


def log_write_deliverable(path: str, *, path_hint: Path | str | None = None) -> None:
    append_block("WRITE", _display_path(path), path=path_hint)


def fetch_assemble_manifest(
    *,
    skill_root: Path,
    fidelity: str,
    fmt: str,
    phase: str,
) -> dict[str, Any] | None:
    import subprocess
    import sys

    script = Path(__file__).resolve().parent / "assembly" / "assemble_components.py"
    repo_root = Path(__file__).resolve().parents[3]
    cmd = [
        sys.executable,
        str(script),
        "--skill-root",
        str(skill_root),
        "--fidelity",
        fidelity,
        "--format",
        fmt,
        "--phase",
        phase,
    ]
    env = os.environ.copy()
    env.pop("STORIES_SKILL_TRACE", None)
    env["PYTHONPATH"] = str(repo_root)
    completed = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(repo_root),
        env=env,
        check=False,
    )
    if completed.returncode != 0 or not completed.stdout.strip():
        return None
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError:
        return None
    return payload if isinstance(payload, dict) else None


def parse_assemble_params(command: str) -> dict[str, str]:
    skill_root = extract_flag(command, "skill-root") or "stories"
    return {
        "skill-root": skill_root,
        "fidelity": extract_flag(command, "fidelity") or "?",
        "format": extract_flag(command, "format") or "?",
        "phase": extract_flag(command, "phase") or "?",
    }


def resolve_skill_root(skill_root_raw: str) -> Path:
    root = Path(skill_root_raw)
    if root.is_absolute():
        return root
    repo = Path(__file__).resolve().parents[3]
    return (repo / root).resolve()


def replay_assemble_manifest(command: str) -> dict[str, Any] | None:
    if "assemble_components" not in command.lower():
        return None
    params = parse_assemble_params(command)
    return fetch_assemble_manifest(
        skill_root=resolve_skill_root(params["skill-root"]),
        fidelity=params["fidelity"],
        fmt=params["format"],
        phase=params["phase"],
    )


def log_cli(
    *,
    argv: list[str],
    command: str | None,
    fmt: str | None,
    workspace: str | None,
    written: list[str] | None,
    exit_code: int,
) -> None:
    params: dict[str, str] = {}
    if command:
        params["command"] = command
    if fmt:
        params["format"] = fmt
    if workspace:
        params["workspace"] = workspace
    log_stories_cli_call(
        command=" ".join(argv),
        params=params,
        written=written,
        exit_code=exit_code,
    )


# Legacy alias used by assemble CLI
def log_assemble(
    manifest: dict[str, Any],
    *,
    anomalies: list[dict[str, Any]] | None = None,
    path: Path | str | None = None,
) -> None:
    params = {
        "skill-root": "stories",
        "fidelity": ",".join(manifest.get("fidelities") or []),
        "format": str(manifest.get("format", "?")),
        "phase": str(manifest.get("phase", "?")),
    }
    log_assemble_call(
        params=params,
        manifest=manifest,
        command="assemble_components.py (subprocess)",
        path=path,
    )


def log_agent_artifacts(
    sources: list[tuple[str, Path]],
    *,
    max_chars: int = 12000,
    path: Path | str | None = None,
) -> None:
    if not sources:
        append_block("GENERATED", "(none)", path=path)
        return
    lines: list[str] = []
    for rel, file_path in sources:
        lines.append(f"--- {rel} ---")
        try:
            text = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            lines.append(f"(binary, {file_path.stat().st_size} bytes)")
            continue
        except OSError as exc:
            lines.append(f"(unreadable: {exc})")
            continue
        if len(text) > max_chars:
            half = max_chars // 2
            text = f"{text[:half]}\n… [{len(text) - max_chars} chars truncated] …\n{text[-half:]}"
        lines.append(text.rstrip())
        lines.append("")
    append_block("GENERATED", "\n".join(lines).rstrip(), path=path)


def log_runner_scanners(
    *,
    results: list[tuple[str, str, int, list[dict]]],
    total_violations: int,
    path: Path | str | None = None,
) -> None:
    lines: list[str] = []
    for scanner_name, status, violation_count, violations in results:
        if "SKIP" in status:
            continue
        tag = "PASS" if "PASS" in status else "FAIL"
        line = f"{scanner_name}: {tag}"
        lines.append(line)
        for v in violations[:3]:
            rule = v.get("rule", v.get("source", "?"))
            msg = v.get("message", str(v))
            loc = v.get("location", "")
            suffix = f"  [{loc}]" if loc else ""
            lines.append(f"  FAIL {rule}: {msg}{suffix}")
    append_block("EVAL SCANNERS", "\n".join(lines), path=path)


def log_runner_coarse_judge(*, verdict: str, reason: str, path: Path | str | None = None) -> None:
    append_block(
        f"EVAL JUDGE → {verdict}",
        reason or "(no reason)",
        path=path,
    )


def log_runner_harvest(
    *,
    harvested: list[tuple[str, str]],
    missing: list[str],
    path: Path | str | None = None,
) -> None:
    lines: list[str] = []
    if harvested:
        for manifest_rel, source_rel in harvested:
            if manifest_rel == source_rel:
                lines.append(f"  - {manifest_rel}")
            else:
                lines.append(f"  - {manifest_rel} ← {source_rel}")
    if missing:
        lines.append("missing:")
        lines.extend(f"  - {m}" for m in missing)
    append_block("EVAL HARVEST", "\n".join(lines) if lines else "(nothing harvested)", path=path)
