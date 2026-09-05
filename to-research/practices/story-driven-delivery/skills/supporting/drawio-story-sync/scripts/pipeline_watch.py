"""Watchdog-based watcher for the abd-practice-pipeline.

Runs as a long-lived VSCode task launched on `folderOpen`. Watches:

  - **/*.drawio
  - **/*.story-graph.json

On every change, calls `pipeline.py on-edit --path <changed>`. Debounces
with a small timer so editors that write atomically (rename / save) don't
fire twice.

Modes (--mode):
  on      — fully automatic; calls pipeline with --non-interactive
  off     — exits immediately; watcher is disabled
  prompt  — calls pipeline without --non-interactive; gates may ask
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import threading
import time
from pathlib import Path

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer


SCRIPT_DIR = Path(__file__).resolve().parent
PIPELINE = SCRIPT_DIR / "pipeline.py"

WATCHED_SUFFIXES = (".drawio", "story-graph.json")
DEBOUNCE_SECONDS = 2.0


def notify(msg: str) -> None:
    """Show a Windows Toast notification via winotify (best-effort, background thread)."""
    def _show():
        try:
            from winotify import Notification
            n = Notification(app_id="DrawIO Sync", title="DrawIO Sync", msg=msg)
            n.show()
        except Exception:
            pass
    threading.Thread(target=_show, daemon=True).start()


COOLDOWN_SECONDS = 10.0  # ignore re-fires on the same file after processing it


class PipelineHandler(FileSystemEventHandler):
    def __init__(self, root: Path, mode: str) -> None:
        self.root = root
        self.mode = mode
        self._timers: dict[str, threading.Timer] = {}
        self._cooldowns: dict[str, float] = {}
        self._lock = threading.Lock()

    # Side-car suffixes produced by the sync/render commands — never re-trigger on these
    _SIDECAR_SUFFIXES = (
        "-exploration.drawio",
        "-increments.drawio",
        "-update-report.json",
        "-extracted.json",
        "-layout.json",
    )

    def _in_cooldown(self, path: str) -> bool:
        return time.monotonic() - self._cooldowns.get(path, 0) < COOLDOWN_SECONDS

    def _interesting(self, path: str) -> bool:
        p = Path(path)
        # ignore dotfiles and outputs nested under hidden dirs
        if any(part.startswith(".") for part in p.parts):
            return False
        # ignore side-car files produced by the pipeline itself
        name = p.name
        if any(name.endswith(s) for s in self._SIDECAR_SUFFIXES):
            return False
        if not any(name.endswith(s) for s in WATCHED_SUFFIXES):
            return False
        return True

    def _schedule(self, path: str) -> None:
        with self._lock:
            if self._in_cooldown(path):
                return
            existing = self._timers.pop(path, None)
            if existing is not None:
                existing.cancel()
            timer = threading.Timer(DEBOUNCE_SECONDS, self._fire, args=[path])
            timer.daemon = True
            self._timers[path] = timer
            timer.start()

    def _fire(self, path: str) -> None:
        with self._lock:
            self._timers.pop(path, None)
            if self._in_cooldown(path):
                return
            now = time.monotonic()
            self._cooldowns[path] = now
            # also pre-emptively cool down the paired output file
            p = Path(path)
            if p.name.endswith("story-graph.json"):
                paired = str(p.with_suffix(".drawio"))
            elif p.name.endswith(".drawio"):
                paired = str(p.with_name(p.stem + ".story-graph.json"))
            else:
                paired = None
            if paired:
                self._cooldowns[paired] = now
        print(f"[watch] change: {path}", flush=True)
        cmd = [sys.executable, str(PIPELINE), "--root", str(self.root)]
        if self.mode == "on":
            cmd.append("--non-interactive")
        cmd += ["on-edit", "--path", path]
        result = subprocess.run(cmd, check=False)
        if result.returncode == 0:
            fname = Path(path).name
            if fname.endswith("story-graph.json"):
                print("[watch] notifying: DrawIO updated", flush=True)
                notify(f"{fname} → outline + exploration + increments updated")
            elif fname.endswith(".drawio"):
                print("[watch] notifying: graph synced", flush=True)
                notify(f"{fname} → story-graph.json synced")

    def on_modified(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return
        if self._interesting(event.src_path):
            self._schedule(event.src_path)

    def on_created(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return
        if self._interesting(event.src_path):
            self._schedule(event.src_path)

    def on_moved(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return
        dest = getattr(event, "dest_path", None)
        if dest and self._interesting(dest):
            self._schedule(dest)


def main() -> int:
    parser = argparse.ArgumentParser(description="abd-practice-pipeline watcher")
    parser.add_argument("--root", required=True, help="Engagement root to watch")
    parser.add_argument(
        "--mode",
        choices=["on", "off", "prompt"],
        default="prompt",
        help="Sync mode: on=automatic, off=disabled, prompt=ask per gate",
    )
    args = parser.parse_args()

    if args.mode == "off":
        print("[watch] mode=off — watcher disabled, exiting", flush=True)
        return 0

    root = Path(args.root).resolve()
    print(f"[watch] starting on {root} (mode={args.mode})", flush=True)
    handler = PipelineHandler(root, args.mode)
    observer = Observer()
    observer.schedule(handler, str(root), recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
    return 0


if __name__ == "__main__":
    sys.exit(main())
