import type { EngineInterface } from 'claude-code'

import { after } from '../board-chat/board'
import { reasonOf } from '../shared/failure'

// The draw.io viewer (tools/drawio_viewer in a CDD checkout, published inside this mod by the cdd home) serves the real
// draw.io editor on this port, and its Save writes the file back. A diagram opens there in the person's browser, with no message to the chat.
const VIEWER_PORT = 8791
const VIEWER_URL = `http://127.0.0.1:${VIEWER_PORT}`
const STARTED_WITHIN_MILLISECONDS = 10_000
const STARTED_CHECK_MILLISECONDS = 500

export const viewerUrlOf = (path: string): string => `${VIEWER_URL}/edit?f=${encodeURIComponent(path)}`

function isViewerUp($: EngineInterface): Promise<boolean> {
  return $.http
    .fetch(`${VIEWER_URL}/`)
    .then(answer => answer.ok)
    .catch(() => false)
}

// The viewer published with this mod, so a chat in any project has one; a mod loaded straight from a CDD checkout
// runs the checkout's own.
async function viewerScriptOf($: EngineInterface, top: string): Promise<string> {
  const published = `${$.plugin.root}/drawio-viewer/drawio_viewer.py`
  return (await $.fs.exists(published)) ? published : `${top}/tools/drawio_viewer/drawio_viewer.py`
}

// The viewer lives as long as this chat's mod, started from the repository's top so a path from the project opens.
async function startViewer($: EngineInterface): Promise<boolean> {
  const { exitCode, stdout } = await $.process.run(['git', 'rev-parse', '--show-toplevel'])
  if (exitCode !== 0) return false
  const top = stdout.trim()
  const script = await viewerScriptOf($, top)
  void (async () => {
    const viewer = $.process.spawn({ argv: ['python', script, '.', String(VIEWER_PORT)], cwd: top })
    for await (const { text } of viewer) $.ui.log(text, { to: 'debug' })
  })().catch(error => $.ui.log(`The draw.io viewer stopped: ${reasonOf(error)}`, { to: 'debug' }))
  for (let waited = 0; waited < STARTED_WITHIN_MILLISECONDS; waited += STARTED_CHECK_MILLISECONDS) {
    if (await isViewerUp($)) return true
    await after($, STARTED_CHECK_MILLISECONDS, '')
  }
  return false
}

// What opens a web address in the person's browser on this machine.
async function openerOf($: EngineInterface): Promise<string[]> {
  const system = await $.env.get('OS')
  return system === 'Windows_NT' ? ['cmd', '/c', 'start', '""'] : ['xdg-open']
}

// Opens path, a diagram named from the project, in the draw.io viewer, starting the viewer when nothing answers.
export async function openInDrawio($: EngineInterface, path: string): Promise<void> {
  if (!(await isViewerUp($)) && !(await startViewer($))) {
    $.ui.toast(`The draw.io viewer did not start: run python tools/drawio_viewer/drawio_viewer.py . ${VIEWER_PORT}`)
    return
  }
  const opened = await $.process.run([...(await openerOf($)), viewerUrlOf(path)])
  if (opened.exitCode !== 0) $.ui.toast(`${path} did not open in draw.io: ${opened.stderr.trim() || `exit ${opened.exitCode}`}`)
}
