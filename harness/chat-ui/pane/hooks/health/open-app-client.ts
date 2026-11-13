import type { EngineInterface } from 'claude-code'

import type { ServerHealthData } from '@cdd/harness/diagnostics/server-health'

import { boardPageUrl, repositoryFolder } from '../board-chat/board'
import { currentChatBar } from '../chat-bar/chat-bar-client'
import { openPage, startedBoard } from '../board-chat/board-server'
import { reasonOf } from '../shared/failure'
import { currentServerHealth, refreshHealth, ServerHealthClient } from './server-health-client'

// Pressing an app on the server health panel opens it in the Claude desktop app's browser pane, starting it first when it is not running.
export type AppName = 'Kanban app' | 'Graph app'

// The graph app is the explorer in harness/graph/app: its web server and its Vite app, each started by the repository's
// own start script, which stops any copy of that server first, starts one that outlives this chat, and prints where it
// answers once it does.
const GRAPH_APP = 'harness/graph/app'
const GRAPH_START_SCRIPTS = ['scripts/start_graph_web.py', 'scripts/start_graph_app.py']
const GRAPH_START_TIMEOUT_MS = 90_000
const GRAPH_START_BY_HAND = `Start it with: python scripts/start_graph_web.py, then python scripts/start_graph_app.py, in the repository's own folder.`

type Opening = { url: string; problem: string }

// An app being started takes no second press, so two presses do not start it twice.
const starting = new Set<AppName>()

async function graphAppPort($: EngineInterface): Promise<number | null> {
  const { report } = await currentServerHealth($)
  return new ServerHealthClient(report as ServerHealthData | null).graphAppPort
}

// The repository's own Python, which has cdd installed, else whichever python is on the path.
async function pythonOf($: EngineInterface, repository: string): Promise<string> {
  for (const python of [`${repository}/.venv/Scripts/python.exe`, `${repository}/.venv/bin/python`]) {
    if (await $.fs.exists(python)) return python
  }
  return 'python'
}

// The start script's report: where the server answers once it does, and its log when it did not start.
function reportOf(stdout: string): { url?: string; log?: string } {
  try {
    return JSON.parse(stdout) as { url?: string; log?: string }
  } catch {
    return {}
  }
}

async function startGraphApp($: EngineInterface): Promise<Opening> {
  const repository = await repositoryFolder($)
  if (!repository) return { url: '', problem: `The Graph app is not running and this chat is in no repository. ${GRAPH_START_BY_HAND}` }
  if (!(await $.fs.exists(`${repository}/${GRAPH_APP}/node_modules`))) return { url: '', problem: `The Graph app is not running and is not installed: run npm install in ${GRAPH_APP}.` }
  $.ui.toast('Starting the Graph app.')
  const python = await pythonOf($, repository)
  let url = ''
  for (const script of GRAPH_START_SCRIPTS) {
    const run = await $.process.run([python, script], { cwd: repository, timeoutMs: GRAPH_START_TIMEOUT_MS })
    const report = reportOf(run.stdout)
    if (run.exitCode !== 0) return { url: '', problem: `The Graph app did not start: ${script} failed${report.log ? `, see ${report.log}` : `: ${run.stderr.trim()}`}. ${GRAPH_START_BY_HAND}` }
    url = report.url ?? ''
  }
  return url ? { url, problem: '' } : { url: '', problem: `The Graph app started but did not say where it answers. ${GRAPH_START_BY_HAND}` }
}

// The Graph app on this chat's session path, so the graph it loads is the chat's own session's.
async function openingGraphApp($: EngineInterface): Promise<Opening> {
  await refreshHealth($)
  const port = await graphAppPort($)
  const opening = port !== null ? { url: `http://localhost:${port}`, problem: '' } : await startGraphApp($)
  const sessionPath = (await currentChatBar($)).sessionPath
  if (!opening.url || !sessionPath) return opening
  return { url: `${opening.url}/?${new URLSearchParams({ folder: sessionPath })}`, problem: '' }
}

// The board page showing this chat's repository with the chat's ticket selected, starting the board when nothing answers
// on its port, as /board does.
async function openingKanbanApp($: EngineInterface): Promise<Opening> {
  const { url, wasStarted, problem } = await startedBoard($)
  if (!url) return { url: '', problem }
  if (wasStarted) $.ui.toast('Started the Kanban app. It stops when this chat ends.')
  const ticket = (await currentChatBar($)).ticketName
  return { url: await boardPageUrl($, url, ticket ? { ticket } : {}), problem: '' }
}

// Opens app in the browser pane, else in the person's browser, saying why: as it is when it runs, else once it has started. The panel reads the server
// health again after, so a started app shows running.
export async function openApp($: EngineInterface, app: AppName): Promise<void> {
  if (starting.has(app)) return
  starting.add(app)
  try {
    const { url, problem } = app === 'Kanban app' ? await openingKanbanApp($) : await openingGraphApp($)
    if (!url) {
      $.ui.toast(problem)
      return
    }
    const said = await openPage($, url)
    if (said) $.ui.toast(`The ${app} at ${url}: ${said}`)
  } catch (failure) {
    $.ui.toast(`The ${app} did not open: ${reasonOf(failure)}`)
  } finally {
    starting.delete(app)
    await refreshHealth($)
  }
}
