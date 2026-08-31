#!/usr/bin/env python3
"""Entry point invoked by every hook wired up in .cursor/hooks.json.

Usage (from hooks.json):
    python3 hook_test/hook_logger.py <hook_name>

The hook name is required so we know which schema to expect on stdin and what
response shape to emit on stdout. See hook_test/README.md for the full list of
supported hooks and the notification each one can produce.
"""

from __future__ import annotations

import sys
import traceback
from typing import Any

from hook_lib import (
    MARKER_CTX,
    MARKER_DENY,
    MARKER_FOLLOWUP,
    MARKER_STDERR,
    SENTINEL_EDIT_NAME,
    build_summary,
    emit,
    note_stderr,
    payload_haystack,
    read_payload,
    record,
)


def _has(payload: dict[str, Any], marker: str) -> bool:
    return marker in payload_haystack(payload)


def handle_before_shell_execution(payload: dict[str, Any]) -> dict[str, Any]:
    haystack = payload_haystack(payload)
    if MARKER_STDERR in haystack:
        note_stderr(f"beforeShellExecution saw a marker in: {payload.get('command')!r}")
    if MARKER_DENY in haystack:
        record("beforeShellExecution", payload, {"decision": "deny"})
        return {
            "permission": "deny",
            "user_message": "hook_test: blocked because command contained HOOK_TEST_MARKER_DENY (this is the visible user_message notification).",
            "agent_message": "hook_test: beforeShellExecution denied this command. The agent sees THIS text as feedback, proving the hook fired.",
        }
    record("beforeShellExecution", payload, {"decision": "allow"})
    return {"permission": "allow"}


def handle_after_shell_execution(payload: dict[str, Any]) -> dict[str, Any]:
    if MARKER_STDERR in payload_haystack(payload):
        note_stderr(f"afterShellExecution observed marker command (exit metadata: duration={payload.get('duration')}ms)")
    record("afterShellExecution", payload)
    return {}


def handle_before_read_file(payload: dict[str, Any]) -> dict[str, Any]:
    file_path = str(payload.get("file_path", ""))
    if "secret_do_not_read" in file_path:
        record("beforeReadFile", payload, {"decision": "deny"})
        return {
            "permission": "deny",
            "user_message": "hook_test: blocked read of a file whose path contains 'secret_do_not_read'.",
        }
    record("beforeReadFile", payload, {"decision": "allow"})
    return {"permission": "allow"}


def handle_after_file_edit(payload: dict[str, Any]) -> dict[str, Any]:
    file_path = str(payload.get("file_path", ""))
    if file_path.endswith(SENTINEL_EDIT_NAME):
        note_stderr(f"afterFileEdit noticed sentinel edit at {file_path}")
    record("afterFileEdit", payload)
    return {}


def handle_pre_tool_use(payload: dict[str, Any]) -> dict[str, Any]:
    haystack = payload_haystack(payload)
    if MARKER_DENY in haystack:
        record("preToolUse", payload, {"decision": "deny"})
        return {
            "permission": "deny",
            "user_message": "hook_test: preToolUse blocked this tool call (marker present).",
            "agent_message": "hook_test: preToolUse denied. The agent should see this message and adjust.",
        }
    record("preToolUse", payload, {"decision": "allow"})
    return {"permission": "allow"}


def handle_post_tool_use(payload: dict[str, Any]) -> dict[str, Any]:
    response: dict[str, Any] = {}
    if MARKER_CTX in payload_haystack(payload):
        response["additional_context"] = (
            "hook_test: postToolUse injected this additional_context because a "
            "HOOK_TEST_MARKER_CTX was seen. The agent should read this string as "
            "extra context after the tool result."
        )
        record("postToolUse", payload, {"injected_context": True})
    else:
        record("postToolUse", payload)
    return response


def handle_post_tool_use_failure(payload: dict[str, Any]) -> dict[str, Any]:
    record(
        "postToolUseFailure",
        payload,
        {
            "failure_type": payload.get("failure_type"),
            "error_message": payload.get("error_message"),
        },
    )
    note_stderr(
        f"postToolUseFailure: tool={payload.get('tool_name')!r} "
        f"type={payload.get('failure_type')!r} err={str(payload.get('error_message'))[:200]!r}"
    )
    return {}


def handle_subagent_start(payload: dict[str, Any]) -> dict[str, Any]:
    task = str(payload.get("task", ""))
    if MARKER_DENY in task:
        record("subagentStart", payload, {"decision": "deny"})
        return {
            "permission": "deny",
            "user_message": "hook_test: subagentStart blocked (marker in task).",
        }
    record("subagentStart", payload, {"decision": "allow"})
    return {"permission": "allow"}


def handle_subagent_stop(payload: dict[str, Any]) -> dict[str, Any]:
    task = str(payload.get("task", ""))
    if MARKER_FOLLOWUP in task and payload.get("status") == "completed":
        record("subagentStop", payload, {"followup": True})
        return {
            "followup_message": "hook_test: subagentStop injected this follow-up message (visible in transcript as a new user turn)."
        }
    record("subagentStop", payload)
    return {}


def handle_before_submit_prompt(payload: dict[str, Any]) -> dict[str, Any]:
    prompt = str(payload.get("prompt", ""))
    if MARKER_DENY in prompt:
        record("beforeSubmitPrompt", payload, {"decision": "block"})
        return {
            "continue": False,
            "user_message": "hook_test: beforeSubmitPrompt blocked the submission (marker in prompt).",
        }
    record("beforeSubmitPrompt", payload)
    return {"continue": True}


def handle_pre_compact(payload: dict[str, Any]) -> dict[str, Any]:
    record("preCompact", payload)
    return {
        "user_message": (
            "hook_test: context is being compacted "
            f"({payload.get('context_usage_percent')}% used, "
            f"compacting {payload.get('messages_to_compact')} messages)."
        )
    }


def handle_stop(payload: dict[str, Any]) -> dict[str, Any]:
    record("stop", payload)
    return {}


def handle_after_agent_response(payload: dict[str, Any]) -> dict[str, Any]:
    record("afterAgentResponse", payload)
    return {}


def handle_after_agent_thought(payload: dict[str, Any]) -> dict[str, Any]:
    record("afterAgentThought", payload)
    return {}


HANDLERS = {
    "beforeShellExecution": handle_before_shell_execution,
    "afterShellExecution": handle_after_shell_execution,
    "beforeReadFile": handle_before_read_file,
    "afterFileEdit": handle_after_file_edit,
    "preToolUse": handle_pre_tool_use,
    "postToolUse": handle_post_tool_use,
    "postToolUseFailure": handle_post_tool_use_failure,
    "subagentStart": handle_subagent_start,
    "subagentStop": handle_subagent_stop,
    "beforeSubmitPrompt": handle_before_submit_prompt,
    "preCompact": handle_pre_compact,
    "stop": handle_stop,
    "afterAgentResponse": handle_after_agent_response,
    "afterAgentThought": handle_after_agent_thought,
}


def _permissive_default(hook: str) -> dict[str, Any]:
    if hook in {"beforeShellExecution", "preToolUse", "beforeReadFile", "subagentStart"}:
        return {"permission": "allow"}
    if hook == "beforeSubmitPrompt":
        return {"continue": True}
    return {}


def main() -> int:
    hook = sys.argv[1] if len(sys.argv) > 1 else "unknown"
    payload = read_payload()
    handler = HANDLERS.get(hook)
    try:
        if handler is None:
            record(hook, payload, {"note": "no handler; logged only"})
            emit(_permissive_default(hook))
            return 0
        response = handler(payload)
        emit(response)
        return 0
    except Exception as exc:  # noqa: BLE001 - hooks must fail open
        try:
            record(
                hook,
                payload,
                {
                    "handler_error": repr(exc),
                    "traceback": traceback.format_exc(limit=4),
                    "summary": build_summary(hook, payload) + " [HANDLER_ERROR]",
                },
            )
        except Exception:  # pragma: no cover
            pass
        emit(_permissive_default(hook))
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
