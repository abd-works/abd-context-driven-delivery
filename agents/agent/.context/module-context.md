# agent — module context

## Purpose

The `agent` module implements the redesigned Agent orchestration model for GitHub #55: backlog (`backlog`, `current_task`, `completed_tasks`), participant lifecycle for doer → judge → optional human, JSONL session logging via `AgentSessionLog` / `CliAgentSessionLog`, a stub tools-CLI turn fence (`Turn`, `ToolCall`), queue drain via `run_task_queue`, task templates via `AgentTaskTemplateStore`, `AgentSession.open` / `open_existing` / `finish` with branch/worktree binding and chat persist on a primary `Repo` (InMemoryRepo for vanilla specs), `SubAgent` for the first runnable two-role path (non-blocking child per doer/judge role), `CliAgent` for CLI bind/launch/close (worktree workspace root, ensure chat, chat context fence, `close_agents` / `cleanup` / `close_cli_session`) plus transcript watching (`AgentRuntimeTranscriptWatcher`, `AIChatFault`) with stubbed `AIChatInstance.run_prompt`, and `WorkTicket` / `Workflow` for ticket create/start/finish (InMemory Issue/Project, sibling worktree, issue body → contextRoot, finish lands close commit + Done).

## Seam

`Agent.run_task_queue`, `Agent.run_next_task`, `Agent.load_template`, `Agent.kick`, `Agent.add_tasks`, `Agent.clear_backlog`, `SubAgent`, `CliAgent`, `CliAgentSessionLog`, `AgentRuntimeTranscriptWatcher`, `AIChatFault`, `AIChatInstance`, `AgentSession.open`, `AgentSession.open_existing`, `AgentSession.close`, `AgentSession.finish`, `AgentSession.mint_turn`, `Workspace.open`, `Turn.open`, `Turn.finish`, `Turn.append_tool`, `AgentSessionLog` event writers, `AgentTaskTemplateStore.add`, `AgentTaskTemplateStore.load`, `WorkTicket.create`, `WorkTicket.open_session`, `WorkTicket.start`, `WorkTicket.finish`, `Workflow.create_ticket`, `Workflow.start`, `Workflow.finish`, `Branch.commit`, `Branch.push`, `Branch.merge_from`, `Repo.Worktree.create_sibling`, `Repo.Worktree.remove`

## Constraint

Agent owns AgentSessionLog writes for send, accept, done, verdict, and fault. Kit Turns are owned by the (stub) tools CLI lifecycle — Agent must never finish a kit Turn from task completion. On task rerun, mint a new turn id; keep the same session name and context root. `clear_backlog` empties backlog only (never current or completed). Launching the next task is refused while any current-task participant is in flight. `run_task_queue` drains the backlog; `run_next_task` settles one head. `validation_error` skips the task and advances; other AgentFault kinds stop the run. Caller sets `contextRoot` independently of `session.folder`. Session is opened before run / run_task_queue. AgentSession attaches to one primary repo only — Workspace refuses multi-repo session span when no primary is set. SubAgent launches one non-blocking child per doer and judge role on the same AgentSession and contextRoot; session close tears those children down. CliAgent binds workspace root to `session.branch.worktree.path` before launch; refuses durable launch when no branch worktree exists yet. CliAgent ensures one `AIChatInstance` per participant and sets `workspacePath` / `sessionName` / `contextRoot` on that chat. CliAgent wires accept / done / verdict awaits through `AgentRuntimeTranscriptWatcher` against fake or live `.jsonl`; accept timeout with a dead runtime raises `AIChatFault` `not_accepted`; no transcript growth raises `AIChatFault` `stall`. On judge FAIL, CliAgent increments `failCount` and retries under `maxFails`; at the limit raises `AgentFault` `judge_fail_limit`. CliAgent `close_agents` stops live doer/judge chats and clears bindings (no zombie PIDs); `cleanup` removes orchestration temps under contextRoot `.context` without deleting durable session artifacts; `close_cli_session` runs close_agents + cleanup then `session.close`. WorkTicket.create sets Issue status Backlog; start sets In Progress then openSession (session name from kebab title + number, sibling worktree `{abbrev}-{issue}` beside primary, never inside). Workflow.start opens the ticket session, binds SubAgent by default (CliAgent when selected), adds one AgentTask linked via `task.tickets`, writes `issue-body.md` under contextRoot, then `run_task_queue`. WorkTicket.finish is issue-only (Done + close). AgentSession.finish gathers chat paths, stops the agent, finishes hanging turns, lands a close commit, persists chats on that commit (refs/notes/chats + AnnotatedTag `chat/{branch}`), pushes/merges, and removes a sibling worktree when pushed. Workflow.finish runs session.finish then ticket.finish then session.close. Chats attach on finish work session only — never on Turn.finish or AgentSession.close.

## Public API

- `Agent` — orchestrates doer → judge → optional human; `add_tasks` / `clear_backlog` / `load_template`; `run_task_queue` drains backlog; `run_next_task` settles one item; `kick` retries the doer after FAIL
- `SubAgent` — Agent subtype; non-blocking child runtime per doer/judge role; tears children down on close
- `CliAgent` — Agent subtype; bind worktree + chat context; launch doer/judge with stubbed `AIChatInstance.run_prompt`; `max_fails` / `fail_count`; `close_agents` / `cleanup` / `close_cli_session`; transcript watcher timing fields
- `CliAgentSessionLog` — AgentSessionLog subtype; `bind_chat_context` / `run_chat` / `launch_judge` / `wait_doer`; kick carries `chatId` when bound
- `AgentRuntimeTranscriptWatcher` — polls transcript accept / growth-then-quiet / verdict (injectable clock)
- `AIChatInstance` — CLI chat boundary (`run_prompt`, `continue_chat`, `stop`, chat id, workspace path, alive)
- `AIChatFault` — CLI delivery fault (`not_accepted`, `stall`, `send_failed`, `connection`)
- `AgentTask` — backlog item with doer, optional judge/human, and `tickets` (WorkTicket links)
- `AgentParticipant` — doer, judge, or human role on a task; optional `chat` for CliAgent
- `AgentFault` — orchestration fault; `validation_error` skips, workflow kinds stop
- `AgentTaskTemplate` — blueprint prompts for backlog instantiation
- `AgentTaskTemplateStore` — catalog outside Agent (`add` / `load` / `list_all` / `find_matching`)
- `AgentSession` — named session folder, context root, branch/worktree, turns, and log; `open` / `open_existing` / `close` / `finish`
- `Workspace` — path + repos; `open` creates or opens-existing AgentSession on primary repo; refuses multi-repo span
- `Workspace.PathOverride` — tool/fidelity path override for Workspace.lookup_path
- `MultiRepoSessionError` — raised when a session would span more than one repo
- `Repo` / `InMemoryRepo` — primary-repo surface for session branch/worktree (in-memory for vanilla)
- `Branch` — `checkout_or_create`, `commit`, `push`, `merge_from`, `chats`, `worktree`, `agent_session`
- `Commit` — close-commit stub with note refs
- `AnnotatedTag` — append-oriented chat/{branch} tag book held by Repo
- `Repo.Worktree` — path + branch; `create_sibling` beside primary (never inside); `remove` for linked sibling
- `Issue` / `Project` / `Status` — InMemory gh issue and project board surface
- `WorkTicket` — `from_ref` / `create` / `open_session` / `start` / `finish` / `as_dict`; `session_name`; navigate fields via `issue`
- `Workflow` — `create_ticket` / `start` / `finish` → ticket + session lifecycle
- `WorkflowConfig` / `StartTicketResult` — workflow defaults and start outcome
- `AgentSessionLog` — append orchestration events (`open`, `send`, `accepted`, `done`, `verdict`, `open_turn`, `finish_turn`, `append_tool`, …)
- `Turn` — tools-CLI turn fence; `Guidance` carries sessionName / contextRoot / turnId
- `ToolCall` — one expand or run record on an open Turn

## Extend

Subtypes specialize participant runtime hooks. ChatAgent in-chat toolset lives in `chat_agent.py` (`open_session`, `enqueue_judged_job`, `enqueue_judged_job_from_ticket`, `run_doer`, `run_judge`, `run_backlog`, `read_log_kinds`, `eval`).

## Tests

| Layer | File | Runner |
|-------|------|--------|
| Vanilla BDD | `agent_spec.py` | `mamba agents/agent/agent_spec.py` |
| Agent BDD | `agent_agent_spec.py` | `python -m tools agent-spec agents/agent/agent_agent_spec.py` (ChatAgent in_chat: `AGENT_BDD_IN_CHAT=1`) |

Shared agent BDD helpers: `context_tools/agent_bdd/spec_helpers.py` (`chat_agent_tool_prompt`, `sessions_dir`, …). Session JSON under `.context/.agent_bdd_sessions/`.

## Dependencies

Stdlib only for increments 1–12. Session branch/worktree, finish chat persist, and ticket Issue/Project use in-package stubs so vanilla BDD does not require git/gh on PATH.
