"""Concurrency safeguards for story_graph_cli.py write.

Covers:
  - advisory lock is taken during write and cleaned up after
  - a live lock refuses the write (exit 4)
  - a stale lock (>300s) is auto-cleaned
  - --force overrides a live lock
  - --expect-sha matching allows the write
  - --expect-sha mismatch refuses the write (exit 3)
  - sha subcommand prints a stable hex digest
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

import pytest

_CLI = Path(__file__).resolve().parents[1] / "scripts" / "story_graph_cli.py"


def _run(*args: str, stdin: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(_CLI), *args],
        input=stdin,
        capture_output=True,
        text=True,
    )


def _seed_graph(tmp_path: Path) -> Path:
    p = tmp_path / "story-graph.json"
    p.write_text('{"epics": [], "increments": []}\n', encoding="utf-8")
    return p


def test_normal_write_succeeds(tmp_path):
    p = _seed_graph(tmp_path)
    r = _run("write", "--file", str(p), stdin='{"epics": [{"name": "E1"}], "increments": []}')
    assert r.returncode == 0, r.stderr


def test_lock_file_cleaned_up_after_successful_write(tmp_path):
    p = _seed_graph(tmp_path)
    _run("write", "--file", str(p), stdin='{"epics": [], "increments": []}')
    assert not (p.with_name(p.name + ".lock")).exists()


def test_live_lock_refuses_write(tmp_path):
    p = _seed_graph(tmp_path)
    lock = p.with_name(p.name + ".lock")
    lock.write_text(
        json.dumps({"pid": 99999, "acquired_at": time.time(), "host": "other"}),
        encoding="utf-8",
    )
    try:
        r = _run("write", "--file", str(p), stdin='{"epics": [], "increments": []}')
        assert r.returncode == 4, r.stderr
        assert "concurrent write refused" in r.stderr
    finally:
        if lock.exists():
            lock.unlink()


def test_stale_lock_is_auto_cleaned(tmp_path):
    p = _seed_graph(tmp_path)
    lock = p.with_name(p.name + ".lock")
    # Timestamp old enough to be > _STALE_LOCK_SECONDS (300)
    lock.write_text(
        json.dumps({"pid": 1, "acquired_at": 1.0, "host": "old"}),
        encoding="utf-8",
    )
    r = _run("write", "--file", str(p), stdin='{"epics": [{"name": "after-stale"}], "increments": []}')
    assert r.returncode == 0, r.stderr
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["epics"][0]["name"] == "after-stale"


def test_force_overrides_live_lock(tmp_path):
    p = _seed_graph(tmp_path)
    lock = p.with_name(p.name + ".lock")
    lock.write_text(
        json.dumps({"pid": 99999, "acquired_at": time.time(), "host": "other"}),
        encoding="utf-8",
    )
    r = _run("write", "--file", str(p), "--force", stdin='{"epics": [], "increments": []}')
    assert r.returncode == 0, r.stderr


def test_sha_subcommand_matches_file_digest(tmp_path):
    p = _seed_graph(tmp_path)
    r = _run("sha", "--file", str(p))
    assert r.returncode == 0, r.stderr
    expected = hashlib.sha256(p.read_bytes()).hexdigest()
    assert r.stdout.strip() == expected


def test_expect_sha_matching_allows_write(tmp_path):
    p = _seed_graph(tmp_path)
    sha = hashlib.sha256(p.read_bytes()).hexdigest()
    r = _run(
        "write", "--file", str(p), "--expect-sha", sha,
        stdin='{"epics": [{"name": "ok"}], "increments": []}',
    )
    assert r.returncode == 0, r.stderr


def test_expect_sha_mismatch_refuses_write(tmp_path):
    p = _seed_graph(tmp_path)
    stale = hashlib.sha256(b"not-the-current-content").hexdigest()
    # Modify the file so its current sha differs from stale.
    p.write_text('{"epics": [{"name": "changed"}], "increments": []}\n', encoding="utf-8")
    r = _run(
        "write", "--file", str(p), "--expect-sha", stale,
        stdin='{"epics": [], "increments": []}',
    )
    assert r.returncode == 3, r.stderr
    assert "--expect-sha mismatch" in r.stderr
    # File was not overwritten.
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["epics"][0]["name"] == "changed"


def test_force_bypasses_expect_sha_mismatch(tmp_path):
    p = _seed_graph(tmp_path)
    stale = hashlib.sha256(b"not-the-current-content").hexdigest()
    p.write_text('{"epics": [{"name": "A"}], "increments": []}\n', encoding="utf-8")
    r = _run(
        "write", "--file", str(p), "--expect-sha", stale, "--force",
        stdin='{"epics": [{"name": "forced"}], "increments": []}',
    )
    assert r.returncode == 0, r.stderr
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["epics"][0]["name"] == "forced"
