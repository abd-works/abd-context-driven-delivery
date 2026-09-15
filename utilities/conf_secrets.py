"""Load ``conf/.secrets`` (and imported files) into process environment.

Existing environment variables win. ``SECRETS_IMPORT`` is a loader directive
(comma-separated paths) and is not exported.
"""
from __future__ import annotations

import os
from pathlib import Path

_IMPORT_KEY = "SECRETS_IMPORT"


def parse_dotenv(content: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for raw in content.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip("\ufeff")
        key = key.strip().strip("\ufeff")
        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            value = value[1:-1]
        if key:
            out[key] = value.rstrip()
    return out


def default_secret_files(root: Path) -> list[Path]:
    root = root.resolve()
    files = [
        root / "conf" / ".secrets",
        root / "conf" / ".env",
        root.parent / "abd-works-repo" / "abd-answers" / "conf" / ".secrets",
    ]
    extra = os.environ.get("CDD_SECRETS_FILE", "").strip()
    if extra:
        files.insert(0, Path(extra).expanduser())
    return files


def _read_file(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    return parse_dotenv(path.read_text(encoding="utf-8-sig"))


def load_conf_secrets(root: Path, environ: dict[str, str] | None = None) -> list[str]:
    """Fill missing keys on ``environ`` (default ``os.environ``). Return loaded paths."""
    env = os.environ if environ is None else environ
    loaded: list[str] = []
    seen: set[str] = set()
    queue = list(default_secret_files(root))

    while queue:
        path = queue.pop(0).expanduser().resolve()
        key = str(path)
        if key in seen:
            continue
        seen.add(key)
        mapping = _read_file(path)
        if not mapping:
            continue
        loaded.append(key)
        imported = mapping.pop(_IMPORT_KEY, "").strip()
        for item in (p.strip() for p in imported.split(",") if p.strip()):
            queue.append(Path(item))
        for name, value in mapping.items():
            if value and not env.get(name):
                env[name] = value
    return loaded
