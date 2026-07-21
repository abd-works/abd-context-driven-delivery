# tool-action-logging sketch
# fidelity: development (implemented)
# owner: utilities/session_logging (Tools/Actions consult)

@log                          # marker on @tool or @action — not an instruction-chain wrapper
  sets flag on callable
  ToolsetRunner / _ActionExpander consult before append
  stacks with @tool / @action; does not change expansion prose
  # implemented: session_logging.log (re-exported from tools.tool)

----
sessionLogHub                 # owned by utilities — session_logging.SessionLogHub
  resolve session from runRequest.session or "default"
  logDir  utilities/session_logging/.sessions/logs/{session}
  verbose?  default off
  lastPayload   # kept even when verbose off — for retro log_full
  append event
  apply runRequest.log
    full     -> flush lastPayload; verbose on
    verbose  -> verbose on
    off      -> verbose off
  integrate harnessArtifacts   # deferred: ToolAgentBlock still writes its own artifacts

----
runRequest
  toolset
  context
  tool | action
  arguments
  session?          # optional; default -> "default"
  log?              # full | verbose | off

----
runEvent : logEvent
  timestamp
  kind tool|action|expansion
  toolset
  name
  summary           # always
  payloadRef?       # when verbose (or after retro log_full)
  ok
  error?

----
ToolsetRunner
  run_request
    -> sessionLogHub.apply runRequest.log
    when member has @log
      -> sessionLogHub.append runEvent
      -> keep lastPayload
      when verbose -> write payload files
    -> _ActionRunner when action
    -> tool invoke when tool

----
_ActionExpander                  # Actions package — depends on Tools hub
  expand
    when action has @log
      -> sessionLogHub.append expansion event
    # retired scattered log-action-requests.txt as primary trail

----
ToolAgentBlock
  session file stem -> same sessionLogHub.logDir when under tools/.sessions
  _write_artifact
  # deferred integration slice
