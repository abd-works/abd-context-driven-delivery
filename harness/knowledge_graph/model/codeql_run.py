"""Run a GraphRule's .ql via the CodeQL CLI."""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import List, Optional


def run_graph_query(ql_path: Path, root: Path) -> List[dict]:
    if shutil.which("codeql") is None:
        return []
    database = _database(root)
    if database is None:
        return []
    with tempfile.TemporaryDirectory() as folder:
        bqrs = Path(folder) / "results.bqrs"
        decoded = Path(folder) / "results.json"
        run = subprocess.run(
            [
                "codeql",
                "query",
                "run",
                str(ql_path),
                "--database",
                str(database),
                "--output",
                str(bqrs),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        if run.returncode != 0 or not bqrs.is_file():
            return []
        decode = subprocess.run(
            [
                "codeql",
                "bqrs",
                "decode",
                str(bqrs),
                "--format=json",
                f"--output={decoded}",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        if decode.returncode != 0 or not decoded.is_file():
            return []
        payload = json.loads(decoded.read_text(encoding="utf-8"))
    return _rows(payload)


def _database(root: Path) -> Optional[Path]:
    codeql = root / ".codeql"
    if not codeql.is_dir():
        return None
    for child in codeql.iterdir():
        if child.is_dir() and child.name.endswith("-db"):
            return child
    return None


def _rows(payload: dict) -> List[dict]:
    from .codeql import Rows as CodeQLRows

    tuples = payload.get("#select", {}).get("tuples", [])
    rows: List[dict] = []
    for item in tuples:
        if not item:
            continue
        first = item[0]
        name = CodeQLRows.entity_name(first)
        message = item[1] if len(item) > 1 else ""
        if isinstance(message, dict):
            message = message.get("label", "")
        contributor = item[2] if len(item) > 2 else None
        if isinstance(contributor, dict):
            contributor = contributor.get("label")
        file, line = CodeQLRows.entity_location(first)
        row = {"name": name, "message": str(message)}
        kind = CodeQLRows.entity_kind(first)
        if kind:
            row["kind"] = kind
        if file:
            row["file"] = file
        if line:
            row["line"] = line
        if contributor:
            row["contributor"] = str(contributor)
        rows.append(row)
    return rows
