fidelity: modules
issue: 55
workspace:
  code: agents/
  context: agents/.context/
// inventory of current kits — agent-facing or called outside package; internal-only dropped
// resource-oriented: navigate tickets → issue; session → branch → worktree — no cloned primitives
// visibility: _prefix = private (in-class only); no _ = public (called from outside the class)

# git
// resource hierarchy — parent owns child resources; no lookup verbs

## Repo
// public: open, find_root, collections; resource navigation only
root
find_root path
open path
  branches
       Branch
  checkedOutBranches
       Branch
  agentSessions
       AgentSession
  // orchestration data under {root}/.agent_sessions/{name}/ — primary repo only; no multi-repo session
  defaultSessionName
  // Open Default Agent Session — default name when none given
  project
       Project
  tags
       AnnotatedTag

## InMemoryRepo : Repo
// same public API as Repo; for specs with explicit no_branch only — never Agent._repo in production

## Branch
// public: checkout, commit, push, merge, chats; private: _persist_chats
name
  head
       Commit
  worktree
       Worktree
  agentSession
       AgentSession
  // correlates to this checkout
  chats
  // get/set — transcript paths; append at finish work session; lookup via AnnotatedTag chat/{branch.name}
checkout
checkout_or_create
  // branch name supplied by caller — AgentSession.open passes session/{name}
commit paths message
merge branch
push
push_to remote
has_unpushed_commits
is_dirty
set_dirty dirty
clear_stash
fetch
pull
merge_from branch
_persist_chats commit  // private
  // Finish Work Session — path → refs/notes/chats on commit; append AnnotatedTag chat/{branch.name}
  // same contract as WorkSession.save_chat today

## Commit
// public: format, from_message, workflow_message; notes.read, notes.find_mistakes
sha
subject
trailers
format subject trailers
from_message sha message
workflow_message subject issue state
  notes
    note text
    read
    find_mistakes

## Worktree
// public: add, remove, create_sibling
path
primary
linked
add path
remove
create_sibling path
  // sibling worktree beside primary clone — path supplied by caller (Workflow); never inside primary

## Project
// public: link_repository, status_option_names, theme_option_names
owner
number
link_repository
  states
       Status
  issues
       Issue
status_option_names
theme_option_names

## Issue
// public: create, close, set_status, set_type, set_theme, set_project_theme, add_label, add_theme, parse_number, github_ref
number
title
body
url
  state
       Status
closed
labels
parse_number ref
github_ref owner repo number
close
set_status state
add_label name
add_theme theme
set_project_theme theme
set_type name
create title body

## Status
// properties only — project field option name; board-defined, not fixed Backlog/In Progress/Done
name

## AnnotatedTag
// public: write, read, list
name
message
write name message 
read name
list

# workspace
// IDE entry: path + repos → pick primary Repo → AgentSessions / Branch.agentSession
// multi-root OK; AgentSession hangs off one Repo only (driving changes) — no multi-repo session

## Workspace
// public: lookupPath, upsertPath, open, load, save
// private: _refuse_multi_repo_session
path
  repos
       Repo
  pathOverrides
       PathOverride
primaryRepo
  // Reject Multi Repo Session Span — AgentSession attaches to one primary repo only
lookupPath tool fidelity
upsertPath tool fidelity path
open
  -> _refuse_multi_repo_session
  // default: isolate — branch session/{name} + worktree (see AgentSession.open)
  // opt-out: explicit no_branch / branch=False — tests only; log isolated: false
  // never implicit InMemoryRepo in production Agent._repo
load
save
_refuse_multi_repo_session  // private
  // policy gate — session must not span more than one repo when multiple roots

## PathOverride
// properties only
tool
fidelity
path

# Agent

// minimal public surface — open, resume, close, finish
// caller sets name, goal, contextRoot before open; branch + worktree created inside open

## AgentSession
// public: open, resume, close, finish outcome
// private: _gather_chat_paths, _recreate_scaffolding
  repo
       Repo
branch
name
goal
  agent
       Agent
  folder
  // {repo.root}/.agent_sessions/{name}/ — orchestration only (log, recorded session state)
  contextRoot
  // Path anywhere in repo — set by caller before open; not derived from name or folder
  log
       AgentSessionLog
  turns
       Turn
open
  -> repo.agentSessions
  -> branch.checkout_or_create
    // branch name session/{name} — convention here; not a separate primitive elsewhere
  -> branch.worktree
    // attach dedicated worktree (sibling beside primary for ticket flows)
    // skip worktree when caller passed explicit no_branch
  -> log.open
    // fields include isolated: true|false
resume
  // Open Existing — from session recorded on disk; dirty worktree preserved
  // code name: open_existing — must keep sketch name resume as the public verb
  // _recreate_scaffolding when folder missing — private, inside resume
  // with no worktree: checkout_or_create Branch worktree before resume; bind session.branch.worktree
close
  -> agent.close
    // stop live participants; clear session.agent link; do not delete session.folder
  -> log.close
  // never attach or persist chats — that happens on finish work session
finish outcome
  // finish work session — AgentSession lifecycle; land work, attach chats, merge, teardown worktree
  // not the same as Workflow.finish ticket or WorkTicket.finish (issue only)
  -> agent.close
    // CliAgent: close_agents + cleanup before commit (stop runtimes, clear bindings)
  -> turns
    -> turn.finish
      // hanging turns only — turn close commits work; never attaches chats
  -> branch.commit
    // close commit — session artifacts + scope paths
  -> closeCommit
    -> branch.head
  -> branch.chats
    <- _gather_chat_paths
  -> branch._persist_chats closeCommit
  -> branch.push
  -> branch.merge_from
  -> branch.worktree.remove
    // when clean and pushed — sibling worktree teardown
_gather_chat_paths  // private
  // transcript paths from AIChatInstance participants + orchestrator
_recreate_scaffolding  // private
  // inside resume when session.folder missing

## Agent
Agent(session)
// session omitted → Workspace → pick primary Repo → open/create AgentSession
// Job 1: task queue — backlog / current / done
// Job 2: participant orchestration — doer → judge → human; subtypes implement _send / _await_*
// thin: _ensure_session before run — session / turn lifecycle owned by AgentSession, tools CLI, Workflow
//
// public: add_tasks, clear_backlog, triage_backlog, load_template, close, kick, run
// private: _ensure_session, run-loop (_launch_next … _complete_task), _send / _await_*, _parse_task, …
session
model
log
  -> AgentSession.log
  // AgentSessionLog — orchestration audit; kit tool lines via append_tool
  tasks
       AgentTask
backlog
  // tasks where state = Backlog
currentTask
  // In Progress (at most one); doer/judge/human hang here
completedTasks
  // tasks where state = Done
add_tasks tasks  // @agent_tool — append to backlog
clear_backlog  // @agent_tool — empty backlog only; does not touch currentTask / completedTasks
triage_backlog  // @agent_tool
load_template template  // @agent_tool
  -> _instantiate_tasks template
  -> add_tasks
  // never retain template or a template list — Agent holds tasks only
close  // @agent_tool — stop live participants; does not finish AgentSession
kick  // @agent_tool
run text  // @agent_instructions
  -> _parse_task text
  -> add_tasks
  -> run
run  // @agent_tool
  // never opens kit Turns — those open in external tools CLI after slash
  -> _ensure_session
  -> _launch_next
  -> _launch_doer
  -> _wait_doer
  -> _launch_judge
  // skip when no judge
  -> _wait_verdict
  // skip when no judge — _complete_task auto-passes once doer is done
  -> _launch_human
  // skip when no human
  -> _wait_human
  // skip when no human
  -> _complete_task
  // once per backlog head until empty
  _ensure_session  // private
    -> session.open
  _launch_next  // private
    -> backlog
    -> log.launch_next task
    // never second _send while currentTask participant in flight (doer | judge | human)
    // Launch Next Task As Current — refuse when any participant still in flight
  _launch_doer  // private
    -> _send currentTask.doer
    -> log.send participant
    -> _await_accept currentTask.doer
    -> log.accepted participant
  _wait_doer  // private
    -> _await_done currentTask.doer
    // before return: dispatch-back is signal only — never Turn.finish callback
    -> log.done participant
  _launch_judge  // private
    // skip when no judge
    // always default validate slashes mirroring doer prompt when judge present
    -> _send currentTask.judge
    -> log.send participant
    -> _await_accept currentTask.judge
    -> log.accepted participant
  _wait_verdict  // private
    -> _await_verdict currentTask.judge
    -> log.verdict participant result
  _launch_human  // private
    // skip when no human
    -> _send currentTask.human
    -> log.send participant
    -> _await_accept currentTask.human
    -> log.accepted participant
  _wait_human  // private
    -> _await_done currentTask.human
    -> log.done participant
  _complete_task  // private
    -> currentTask
    -> log.complete_task task
    // never Turn.finish — kit Turns already finished in external tools CLI
    // no judge: auto-pass once doer done — mark task Done and advance
    // on PASS: _launch_next when backlog remains
    // on FAIL: kick doer and retry same task — CliAgent enforces maxFails / failCount
    // Complete Task And Advance Queue — validation_error skips task; workflow fault stops process
  _advance_queue  // private
_send participant  // private
_await_accept participant  // private
_await_done participant  // private
_await_verdict participant  // private
_raise fault  // private
  -> fault.raise
_parse_task text  // private
_instantiate_tasks template  // private
// must: Agent owns AgentSessionLog writes for send/accept/done/verdict/fault
// must: kit Turns owned by external tools CLI lifecycle begin/end

## AgentTask
// properties only — queue item; state Backlog | In Progress | Done
state
// Backlog | In Progress | Done — agent queue; not the GitHub Project column
index
// optional log field on launch / complete / done
prompt
// doer work — include slash commands (/clean_engineering.model, /bdd.behavior, …); no tools/actions/utilities lists
  doer
       AgentParticipant
  judge
       AgentParticipant
  // optional — default: validate slashes for same kits named in doer prompt (+ judge extras)
  human
       AgentParticipant
  tickets
       WorkTicket
  // zero or more — navigate issue title/body/number via ticket.issue; no duplicated refs

## AgentParticipant
// properties only — doer | judge | human role on a task
type
// doer | judge | human
prompt
// slash-bearing instructions for this role (judge may be derived from doer)
state
// idle | sending | awaiting_accept | running | awaiting_verdict | done | faulted
  fault
       Fault

## Fault
// public: raise — records on session log then propagates
kind
detail
participant
     AgentParticipant
recordedAt
raise
  -> session.log.append_fault fault
  // always before propagate

## AgentFault : Fault
kind
// judge_fail_limit | parse_failed | invariant | validation_error
// validation_error — Complete Task And Advance Queue skips task; workflow fault stops process

## AIChatFault : Fault
// CLI delivery faults — CliAgent transcript watcher; ChatAgent may share kinds
kind
// not_accepted | stall | send_failed | connection

## AgentSessionLog
// public: open, close, open_turn, finish_turn, append_*, send, accepted, done, verdict, set_backlog, add_tasks, launch_next, complete_task, kick, …
// private: _write
// JSONL write API — called from AgentSession, Agent, Turn, tools CLI
session
path
// {session.folder}/agent-session.jsonl
_write kind fields  // private
  // one JSON object per line — always: kind, ts, ts_ms; optional: since_last_s
  // plus kind-specific fields below (omit null/empty — keep records small)
open
  // = AgentSession.open — { kind, name, branch, worktreePath, contextRoot, startedAt, … }
close
  // = AgentSession.close — { kind, name, endedAt, outcome, … }
open_turn turn
  // = Turn.open — { kind, name, action }
finish_turn turn
  // = Turn.finish — { kind, name, sha, subject, … }
append_tool toolCall
  // = ToolCall — { kind, toolset, name, summary, ok, error?, role }
  // also mirrors hanging Turn.toolCalls
append_fault fault
  // = Fault — { kind, fault.kind, detail, participant, recordedAt }
send participant
  // = Agent._send — { kind, participant, prompt? }
accepted participant
  // runtime — { kind, participant }
done participant
  // runtime — { kind, participant }
verdict participant result
  // = Agent._wait_verdict — { kind, participant, result, notes? }
set_backlog tasks
  // = Agent.set_backlog — { kind, backlog: [prompts…] }
add_tasks tasks
  // = Agent.add_tasks — { kind, tasks: [prompts…] }
launch_next task
  // = Agent._launch_next — { kind, prompt, hasJudge?, hasHuman? }
complete_task task
  // = Agent._complete_task — { kind, prompt, outcome, duration_s? }
validation_error detail
  // Complete Agent Task With Judge — validate action error on session log
human_feedback feedback
  // Complete Agent Task With Judge and Human — feedback before doer retry
kick participant
  // = Agent.kick — { kind, participant }

## Turn
// public: open, close, finish, record_mistake, record_correction
// opened/closed by external tools CLI — a finished Turn is the commit; no TurnCommit
session
  // AgentSession — branch/worktree for git
name
sha
// set on finish when a commit lands
subject
// commit subject; used as the message when finish commits
hanging
  toolCalls
       ToolCall
  mistakes
       Mistake
  correction
       Correction
open
  // must: external tools CLI → action.begin — never Agent.run
  // context guidance: session name, context root, new turn id, tool guidance text
  // on task rerun: new turn id; same session name and context root as first run
  -> session.log.open_turn turn
close
finish prompt result context
  // must: external tools CLI → action.end — never Agent._complete_task
  // never attach chats — finish work session owns chat persistence
  -> session.branch.commit paths subject
  // always via Branch (worktree) — Turn never owns a separate git handle
  // on success: set sha + subject on this Turn
  -> session.log.finish_turn turn
record_mistake
record_correction

## Mistake
// properties only
annotate

## Correction
// properties only
add mistake

## ToolCall
// properties only
toolset
name
summary
ok
error
role
// expansion | run

## AgentTaskTemplate
// properties only — blueprint; not live AgentTask instances
name
tasks
// blueprint prompts (with slashes) — not live instances
description

## AgentTaskTemplateStore
// public: add, load, list_all, find_matching — catalog outside Agent
root
add template
load name
list_all
find_matching prompt

## ChatAgent : Agent
// public: kick (+ inherited Agent public API)
// private: _send, _await_*
// parent chat IS the doer/judge/human runtime — Complete Agent Task Using Chat Agent
// tools/actions/utilities in prompts run in this window; _run_tools_cli_for is a no-op
// verdict arrives via parent /agent tool (typed PASS/FAIL), not a child transcript
// human: do not invoke slash / ToolsCli — post a parent message (look at X Y Z + URL of the work), wait for typed feedback
_send participant  // private
_await_accept participant  // private
_await_done participant  // private
_await_verdict participant  // private
_next_human_feedback  // private — text typed in the parent window
kick  // @agent_tool

## SubAgent : Agent
// public: kick (+ inherited Agent public API)
// private: _send, _await_*, _launch, _tear_down_children
// FIRST runnable two-role path — before CliAgent; one task with doer + judge runtime prompt roles
_send participant  // private
_await_accept participant  // private
_await_done participant  // private
_await_verdict participant  // private
kick  // @agent_tool
_launch participant  // private — non-blocking child for doer or judge (both required for judged tasks)
_tear_down_children  // private — on session.close for SubAgent
  files
       AgentRuntimeFileSync
  // session.folder/runtime/{doer,judge,healer}.{in,out} — same FileSync as CliAgent jsonl
// child decides kits; empty-actions path may performTurn-wrap — still inside child, not Agent.open
// @agent_tool / slash surface = ops on Agent subtypes (same as CliAgent) — no separate *Tool type

## AgentRuntimeFileSync
// process-to-process over files — THE wait for CliAgent and SubAgent. Same operations; paths differ.
// SubAgent: requestPath={role}.in replyPath={role}.out
// CliAgent: same jsonl for both (accept = user line; done = growth then quiet)
// ChatAgent has no FileSync.
// public: send, wait_accept, wait_done, read_verdict, stop
acceptSeconds
stallSeconds
quietSeconds
requestPath
replyPath
send role prompt
wait_accept
  // Time Accept — timeout → AIChatFault not_accepted
wait_done
  // Time Done — request file still holds work → keep waiting; empty + no reply → AIChatFault stall
  // growth then quietSeconds → done
read_verdict
  // PASS or FAIL; AIChatFault when unreadable — never default PASS
stop

# CliAgent

## CliAgent : Agent
// CLI-only: AIChatInstance handle + AgentRuntimeFileSync + CliAgentSessionLog
// public @agent_tool: kick, close_agents, cleanup, close_cli_session (+ inherited close, run, backlog ops)
// private: _ensure_session override, _launch_* / _wait_* / _complete_task overrides, chat bind helpers
maxFails
failCount
  files
       AgentRuntimeFileSync
// clocks live on FileSync, not on CliAgent and not on AIChatInstance
// session.log is CliAgentSessionLog
_bind_workspace_root  // private
  // bind agent runtime workspace to session.branch.worktree.path (git checkout)
_pending_session  // private
  // no durable CliAgent session on main before branch worktree exists
_persist_prompt_to_task_file prompt
  // Launch Doer — under session.contextRoot when argv would be too long
_ensure_session  // private — override Agent
  -> session.open
  -> _bind_workspace_root
    // Set Chat Context — before first task when branch worktree exists
_launch_doer  // private — override Agent
  -> _send currentTask.doer
    -> _ensure_chat currentTask.doer
    -> _bind_chat_context currentTask.doer
      // chat.workspacePath = worktree; chat.sessionName = session.name; chat.contextRoot = session.contextRoot
    -> currentTask.doer.chat.run prompt
      // uses chatId + workspacePath already set on this instance
      // prompt = participant.prompt (slashes)
    -> log.run chat prompt
    -> log.send participant
    // after chat.run returns: Agent plane ends — never tools.ps1 / Turn.open here
  -> _await_accept currentTask.doer
    -> files.wait_accept
    // on timeout and not chat.alive: always AIChatFault not_accepted
    -> log.accepted participant
  -> currentTask.doer.chat._invoke_slash command
    // AIChatInstance plane after spawn — Agent does not call this; realization of live chat
    // skip when freeform only
    // slash → external tools CLI (unchanged) — sessionName + workspacePath on fence/cwd
    // Turn open/finish + append_tool happen inside that external path
_wait_doer  // private — override Agent
  -> _await_done currentTask.doer
    -> files.wait_done
    // dispatch-back: poll only — never Turn.finish → Agent
    // on stall: always AIChatFault stall
    -> log.wait_doer
    -> log.done participant
_launch_judge  // private — override Agent
  // skip when no judge
  -> _send currentTask.judge
    -> _ensure_chat currentTask.judge
    -> _bind_chat_context currentTask.judge
      // same workspacePath + sessionName as doer — one AgentSession; own chat instance
    -> currentTask.judge.chat.run prompt
    -> log.run chat prompt
    -> log.launch_judge
    -> log.send participant
  -> _await_accept currentTask.judge
    -> files.wait_accept
    -> log.accepted participant
  -> currentTask.judge.chat._invoke_slash command
    // slash → external tools CLI (unchanged)
_wait_verdict  // private — override Agent
  -> _await_verdict currentTask.judge
    -> files.read_verdict
    -> log.verdict participant result
_complete_task  // private — override Agent
  // on FAIL under maxFails: kick doer and retry same task; increment failCount
  // on FAIL at maxFails: raise AgentFault judge_fail_limit
_auto_kick_stalled_doer  // private — when queue did not advance after stall
_send participant  // private
_bind_chat_context participant  // private
  // copies session.name, session.contextRoot, branch.worktree.path onto participant.chat
_await_accept participant  // private
_await_done participant  // private
_await_verdict participant  // private
_ensure_chat participant  // private
  // CliAgentParticipant + one AIChatInstance (Cursor…|Vscode…) if missing
kick participant  // @agent_tool
  -> participant.chat.resume
  -> log.kick participant
  // Kick Stalled Participant / Kick Stalled Doer — auto without user when queue did not advance
close_agents  // @agent_tool
  // stop live doer and judge agent runtime processes; clear chat bindings
cleanup  // @agent_tool
  // remove orchestration temps; never delete durable session artifacts
close_cli_session  // @agent_tool
  -> close_agents
  -> cleanup
  -> session.close
    // Close Cli Agent Session — no live CLI processes or stale bindings; then Close Agent Session
// Agent.run enter/exit: log.run / log.run_stopped
// _bind_chat_context: log.bind_chat_context
// clear_backlog / add_tasks: log.clear_backlog / log.add_tasks

## CliAgentSessionLog : AgentSessionLog
// public: bind_chat_context, run, wait_doer, launch_judge, run_stopped, recovery, error (+ inherited log kinds)
// private: _write
bind_chat_context participant
  // = CliAgent._bind_chat_context — { kind, chatId, pid, workspacePath, sessionName }
run chat prompt
  // = AIChatInstance.run — { kind, chatId, prompt, argv?, pid? }
launch_judge
  // = CliAgent._launch_judge — { kind, index?, judge.chatId }
wait_doer
  // = CliAgent._wait_doer — { kind, index? }
run
  // = Agent.run enter — { kind }
run_stopped reason
  // runtime — { kind, reason }
launch_next task
  // override — + index; = Agent._launch_next
complete_task task
  // override — + index, summary?, refs?, duration_s?; = Agent._complete_task
verdict participant result
  // override — + index, notes?, duration_s?
kick participant
  // override — + chatId; = CliAgent.kick
recovery
  // runtime — { kind, index?, detail }
error detail
  // runtime — { kind, detail, index? }

## CliAgentParticipant : AgentParticipant
// properties only — adds chat for CLI runtime
  chat
       AIChatInstance
// one AIChatInstance per CLI participant — CursorChatInstance | VscodeChatInstance | …

## AIChatInstance
// public: run, continue, stop
// private: _invoke_slash
// Chat handle only — spawn and identity. NOT a wait state machine.
// No received / waiting / accepted / done. No clocks. No verdict parse (FileSync.read_verdict).
chatId
pid
alive
workspacePath
// spawn cwd — branch worktree; ToolsCli cwd; not contextRoot
sessionName
// fence copy from AgentSession — not wait state
contextRoot
// fence copy from AgentSession — artifacts; not wait state
model
mode
run prompt
  // spawn / deliver prompt to the chat process
_invoke_slash command  // private
  // must: fence carries sessionName; never remanifest; never omit session
list_chats
continue
  // same chatId
stop
  // terminate process / clear pid — FileSync.stop is the wait-side halt

## SubAgentChatInstance : AIChatInstance
// child process that reads/writes FileSync paths — not a second wait implementation

## CursorChatInstance : AIChatInstance
// public: create_chat
create_chat
// sets chatId on this instance — spawn is how this realization receives a request

## VscodeChatInstance : AIChatInstance

## ClaudeChatInstance : AIChatInstance

## ChatAgentRuntime : AIChatInstance
// parent chat window — handle only; no FileSync, no clocks

# workflow

## Workflow
// public: backlog, capture_backlog, start ticket, finish ticket, create_ticket
  workspace
       Workspace
  repo
       Repo
  // primary from workspace.repos
  ticket
       WorkTicket
  session
       AgentSession
  agent
       Agent
  // SubAgent | CliAgent | ChatAgent — /agent type; default SubAgent
backlog focus context
  -> ticket.create title body
    -> ticket.issue.create
    -> ticket.issue.set_status Backlog
  -> agent.run
    // default SubAgent; /agent type selects CliAgent | ChatAgent
capture_backlog focus body
  -> ticket.create title body
start ticket
  -> ticket.from ticket
    -> repo.project.issues
  -> ticket.start
    -> ticket.issue.set_status In Progress
    -> ticket.openSession
      -> workflow.session
      -> session.name
        <- ticket.sessionName
      -> session.goal
        <- ticket.title
      -> session.contextRoot
        <- workspace.lookupPath
      -> session.open
        -> repo.agentSessions
        -> session.branch.checkout_or_create
          // branch name session/{session.name}
        -> session.branch.worktree.create_sibling
          // {primary.parent}/{repo-abbrev}-{issue-number}
        -> session.log.open
  -> session.agent
    -> agent.session
    // /agent type — default SubAgent; CliAgent | ChatAgent when selected
  -> agent.add_tasks
    // one task; task.tickets includes ticket; doer prompt from ticket.issue
  -> ticket.issue.body
    -> session.contextRoot
      issue-body.md
  -> agent.run
finish ticket
  // Workflow lifecycle — close the ticket; orchestrates session finish + issue close + session close
  -> session.finish outcome
    // finish work session — full tree under AgentSession.finish
  -> ticket.finish
    -> ticket.issue.set_status Done
    -> ticket.issue.close
  -> session.close
    -> session.log.close
create_ticket title body
  -> ticket.create title body

## WorkTicket
// public: from, create, openSession, start, finish, set_type, set_theme, set_status, as_dict
  repo
       Repo
  workflow
       Workflow
  issue
       Issue
  session
       AgentSession
  // after openSession — branch via session.branch, worktree via session.branch.worktree
sessionName
  // kebab-case title + issue number — ticket business rule; drives session.name on open
number
  -> issue.number
title
  -> issue.title
body
  -> issue.body
url
  -> issue.url
type
theme
state
  -> issue.state
from ref
  -> repo.project.issues
  -> issue
create title body
  -> repo
  -> issue.create title body
  -> issue.set_status Backlog
  -> set_type
  -> set_theme
openSession
  -> workflow.session
  -> session.name
    <- sessionName
  -> session.goal
    <- title
  -> session.contextRoot
    <- workflow.workspace.lookupPath
  -> session.open
    -> repo.agentSessions
    -> session.branch.checkout_or_create
      // branch name session/{session.name}
    -> session.branch.worktree.create_sibling
      // {primary.parent}/{repo-abbrev}-{issue-number}
    -> session.log.open
start
  -> issue.set_status In Progress
  -> openSession
finish
  // WorkTicket lifecycle — issue only; does not finish work session or close AgentSession
  -> issue.set_status Done
  -> issue.close
set_type name
  -> issue.set_type name
set_theme theme
  -> issue.add_theme theme
set_status state
  -> issue.set_status state
as_dict

## WorkflowConfig
// properties only
projectOwner
projectNumber
defaultBranch

# external participants
// not redesigned here — existing kits/CLIs agents call into

## ToolsCli
// primitives/tools — tools.ps1; slash YAML → action begin/execute/end; Turn open/finish; append_tool
// fence: sessionName, contextRoot, workspacePath (worktree cwd)

## ChatAgentKit
// thin slash `/agent` — bind session name, forward to ChatAgent; no queue/participant/healer logic

## SubAgentKit
// thin slash `/sub-agent` — prepare_channel (mailbox waiters) then Agent.run

## CliAgentKit
// thin slash `/cli-agent` — prepare_channel (bind) then Agent.run; no one-shot open+add+run in the kit

## Healer
// eval after judged FAIL — not a fourth participant type; same Agent runtime as doer/judge
// stories: Complete Agent Task With Judge — healer runs before give-up; then skip or judge_fail_limit

