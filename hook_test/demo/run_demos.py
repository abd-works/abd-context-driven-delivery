#!/usr/bin/env python3
"""Fire each hook_test injection/notification channel deliberately.

Run this from the repo root inside a Cloud Agent shell tool:

    python3 hook_test/demo/run_demos.py             # all demos
    python3 hook_test/demo/run_demos.py ctx rewrite # named demos

Each demo either performs a side effect (running a shell command, editing the
sentinel file, arming the stop-followup flag) that will *cause a hook to fire*
inside the current Cloud Agent, or prints instructions telling the agent what
command to run so the corresponding response field is emitted.

Available demos (one per documented injection channel that works in cloud):

    log        Plain command that logs beforeShell/afterShell/preTool/postTool.
    stderr     Command with HOOK_TEST_MARKER_STDERR; hook writes to stderr.
    deny       Explains how to trigger permission=deny with user_message +
               agent_message. The agent must run the marked command itself.
    ctx        Command with HOOK_TEST_MARKER_CTX; postToolUse returns
               additional_context that the agent sees after the tool result.
    rewrite    Command with HOOK_TEST_MARKER_REWRITE; preToolUse rewrites the
               command via updated_input. The Shell tool actually runs the
               rewritten command.
    edit       Edits hook_test/hook_test_sentinel.txt so afterFileEdit fires.
    prompt     Explains how to trigger beforeSubmitPrompt block (requires the
               user to submit a prompt containing HOOK_TEST_MARKER_DENY).
    followup   Creates hook_test/state/stop_followup_pending. On the next stop
               hook the tester emits `followup_message`, which the agent loop
               auto-submits as a new user message.
    subagent   Explains how to trigger the subagentStart deny / subagentStop
               followup_message channels.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import subprocess
import sys
from pathlib import Path

HOOK_TEST_DIR = Path(__file__).resolve().parent.parent
SENTINEL = HOOK_TEST_DIR / "hook_test_sentinel.txt"
STATE_DIR = HOOK_TEST_DIR / "state"
STOP_FOLLOWUP_FLAG = STATE_DIR / "stop_followup_pending"


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
        "For the deny channel, the agent must run this command *inside its own\n"
        "Shell tool* (not this demo script). The hook will then return\n"
        "permission='deny' with user_message + agent_message:\n"
        "    echo HOOK_TEST_MARKER_DENY -- this run should be blocked"
    )


def demo_ctx() -> None:
    _shell("echo HOOK_TEST_MARKER_CTX -- postToolUse should attach additional_context")


def demo_rewrite() -> None:
    print(
        "For updated_input the agent must run this command *inside its own\n"
        "Shell tool*. preToolUse will rewrite the command, and Cursor will run\n"
        "the rewritten version instead. The agent will see:\n"
        "    - the requested command containing 'HOOK_TEST_MARKER_REWRITE'\n"
        "    - the actual executed command containing 'REWRITTEN_BY_HOOK'\n"
        "Command for the agent to run:\n"
        "    echo about HOOK_TEST_MARKER_REWRITE"
    )


def demo_edit() -> None:
    stamp = _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")
    SENTINEL.write_text(f"hook_test sentinel edit at {stamp}\n", encoding="utf-8")
    print(f"Wrote {SENTINEL} (afterFileEdit should log this and emit an [hook_test] stderr line).")


def demo_prompt() -> None:
    print(
        "For beforeSubmitPrompt the *user* must send a chat message containing\n"
        "HOOK_TEST_MARKER_DENY. The hook will return continue=false with a\n"
        "user_message, blocking the prompt before it reaches the model.\n"
        "Only reachable when a human is typing prompts; not directly triggerable\n"
        "from a Cloud Agent shell demo."
    )


def demo_followup() -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    STOP_FOLLOWUP_FLAG.write_text(
        _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds") + "\n",
        encoding="utf-8",
    )
    print(
        f"Armed {STOP_FOLLOWUP_FLAG}.\n"
        "On the *next* stop hook firing, hook_test will return a\n"
        "`followup_message` that the agent loop will auto-submit as a new\n"
        "user turn. The flag is deleted after firing, so it only triggers once.\n"
        "loop_limit is set to 2 in .cursor/hooks.json, so this cannot loop\n"
        "uncontrollably even if the flag were re-armed."
    )


def demo_subagent() -> None:
    print(
        "For subagentStart deny / subagentStop followup_message, spawn a Task\n"
        "subagent with a task string that contains the relevant marker:\n"
        "    HOOK_TEST_MARKER_DENY      -> subagentStart returns permission=deny\n"
        "    HOOK_TEST_MARKER_FOLLOWUP  -> subagentStop returns followup_message\n"
        "                                  when the subagent completes\n"
        "Because this demo script cannot invoke the Task tool, hand these\n"
        "markers to the agent instead."
    )


DEMOS = {
    "log": demo_log,
    "stderr": demo_stderr,
    "deny": demo_deny,
    "ctx": demo_ctx,
    "rewrite": demo_rewrite,
    "edit": demo_edit,
    "prompt": demo_prompt,
    "followup": demo_followup,
    "subagent": demo_subagent,
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
