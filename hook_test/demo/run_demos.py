#!/usr/bin/env python3
"""Fire each hook_test notification channel deliberately.

Run this from the repo root inside a Cloud Agent shell tool:

    python3 hook_test/demo/run_demos.py

For each demo it prints the marker string it is about to trigger so the log
and the transcript are easy to correlate. The script itself does not call
Cursor -- the *side effect* of running these commands is what fires each hook.

Demos:
    log     : plain shell command; expect beforeShellExecution + afterShellExecution
              + preToolUse + postToolUse rows in the log.
    stderr  : writes a marker command to stderr from the hook; look for
              "[hook_test]" lines in the Cursor Hooks output channel.
    deny    : agent tries a benign command containing HOOK_TEST_MARKER_DENY -
              the hook returns permission="deny" with a user_message + agent_message.
    ctx     : shell command containing HOOK_TEST_MARKER_CTX - postToolUse
              returns an additional_context string the agent should see.
    edit    : write to the sentinel file so afterFileEdit fires with a
              recognizable summary and an [hook_test] stderr line.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import subprocess
import sys
from pathlib import Path

HOOK_TEST_DIR = Path(__file__).resolve().parent.parent
SENTINEL = HOOK_TEST_DIR / "hook_test_sentinel.txt"


def _shell(cmd: str) -> int:
    print(f"$ {cmd}")
    proc = subprocess.run(cmd, shell=True, check=False)
    return proc.returncode


def demo_log() -> None:
    _shell("echo hook_test log demo -- expect beforeShell/afterShell/preTool/postTool rows")


def demo_stderr() -> None:
    _shell("echo HOOK_TEST_MARKER_STDERR trigger -- watch stderr / Hooks output channel")


def demo_deny() -> None:
    print(
        "The agent should run this next command *inside its own shell tool* so\n"
        "the hook denies it and returns a user_message + agent_message:\n"
        "    echo HOOK_TEST_MARKER_DENY -- this run should be blocked"
    )


def demo_ctx() -> None:
    _shell("echo HOOK_TEST_MARKER_CTX -- postToolUse should attach additional_context")


def demo_edit() -> None:
    stamp = _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")
    SENTINEL.write_text(f"hook_test sentinel edit at {stamp}\n", encoding="utf-8")
    print(f"Wrote {SENTINEL} (afterFileEdit should log this and emit an [hook_test] stderr line).")


DEMOS = {
    "log": demo_log,
    "stderr": demo_stderr,
    "deny": demo_deny,
    "ctx": demo_ctx,
    "edit": demo_edit,
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "demos",
        nargs="*",
        default=list(DEMOS),
        help=f"Which demos to run (default: all). Choices: {', '.join(DEMOS)}",
    )
    args = parser.parse_args()

    unknown = [d for d in args.demos if d not in DEMOS]
    if unknown:
        print(f"Unknown demos: {unknown}. Valid: {list(DEMOS)}", file=sys.stderr)
        return 2

    for name in args.demos:
        print(f"\n=== demo: {name} ===")
        DEMOS[name]()

    print("\nDone. Inspect results with: python3 hook_test/view_events.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
