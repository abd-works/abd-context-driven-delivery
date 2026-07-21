# Grill Answers

### Current logging baseline

Today _log_action_request in primitives/actions/action.py appends to log-action-requests.txt beside the toolset class when an @action is expanded ? name + recipe tool steps only, not actual 	ool: run invocations, args, or results. Separate richer traces already exist under primitives/tools/.sessions/logs/ for agent-bdd harness runs. Backlog item: "log all tool / agentic calls".

### Primary job of better logging

Primary job is debug live AI sessions - reconstruct actual tool and action invocations through the Tools run choke point. Also integrate the other existing logs (action-expansion log-action-requests.txt and agent-bdd .sessions/logs) into that same story rather than leaving three separate trails.

### Unified log location

Session folder is the hub. Every run (tool or action) appends into the active session log dir (same shape as agent-bdd .sessions/logs). Expansion events and harness traces land there too when a session exists; fall back to a default session when chat has none. Drop scattered log-action-requests.txt as the primary trail.

### Active session binding

Optional session field on every run request YAML. When omitted, use a default session name. Harness and chat write the same folder shape under .sessions/logs. Smallest extension of the existing Tools run document.

### Event richness and verbose mode

Indexed events plus optional payload files (recommended base). Verbose mode stores full payloads; default off. User can say log full retrospectively - last payload is reconstructed and stored as if verbose had been on, and verbose turns on for subsequent events.

### Opt-in via at-log annotation

Logging is applied to any tool or action with an at-log annotation (same annotation pattern as concept). Not global for every call - authors mark which members participate. Need to add the annotation to the tooling surface.

### at-log is a marker the runner checks

at-log is a marker decorator that sets a flag on the callable. ToolsetRunner and the action expander consult it before appending to sessionLogHub. It does not join the action instruction chain like sketch or grill_with_context. Stacks with at-tool and at-action without changing expansion prose.

### Verbose and log_full control surface

Fields on the run request YAML control logging. Examples - log full for retro flush plus verbose on, log verbose, log off. Same document the AI already writes; harness can set it too. No separate logging toolset required for the control channel.

### Logging ownership

at-log and sessionLogHub live inside Tools next to ToolsetRunner and run parsing. Actions drops its private log-action-requests.txt path and consults the same hub when expanding at-log actions. Actions may depend on Tools; Tools does not depend on Actions.

### Sessions root

Session logs live beside the Tools package at primitives/tools/.sessions/logs/{session}/. Same neighborhood as existing agent-bdd tools sessions. Bare session names on run requests resolve there; default session name when omitted is default.

