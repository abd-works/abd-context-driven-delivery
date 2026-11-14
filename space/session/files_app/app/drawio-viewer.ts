import { spawn } from 'node:child_process'
import { connect } from 'node:net'
import { join } from 'node:path'

import { DRAWIO_PORT, drawioEditorUrl } from './files/files-paths'

const HOST = '127.0.0.1'
const STARTED_WITHIN_MILLISECONDS = 10_000
const CHECK_MILLISECONDS = 250

export class DrawioViewerNotStarted extends Error {
  constructor(command: string) {
    super(`The draw.io viewer did not answer on port ${DRAWIO_PORT}: run ${command} from the repository root.`)
    this.name = 'DrawioViewerNotStarted'
  }
}

const answers = (port: number): Promise<boolean> =>
  new Promise(resolve => {
    const probe = connect(port, HOST, () => {
      probe.end()
      resolve(true)
    })
    probe.on('error', () => resolve(false))
  })

const after = (milliseconds: number): Promise<void> => new Promise(resolve => setTimeout(resolve, milliseconds))

// The repository's draw.io viewer (tools/drawio_viewer/drawio_viewer.py), where a .drawio file opens instead of the
// source view: the real draw.io editor, which saves back to the file. Started on its own when nothing answers its port,
// so it outlives this server, as the person may keep editing a diagram.
export class DrawioViewer {
  constructor(
    private readonly repository: string,
    private readonly python: string = process.env.PYTHON || 'python',
  ) {}

  private get script(): string {
    return join(this.repository, 'tools', 'drawio_viewer', 'drawio_viewer.py')
  }

  private get command(): string {
    return `${this.python} tools/drawio_viewer/drawio_viewer.py . ${DRAWIO_PORT}`
  }

  // The editor's address for path, a file named from the repository's root, the viewer started first when it is down.
  async urlOf(path: string): Promise<string> {
    if (!(await answers(DRAWIO_PORT))) await this.start()
    return drawioEditorUrl(path)
  }

  private async start(): Promise<void> {
    spawn(this.python, [this.script, this.repository, String(DRAWIO_PORT)], { cwd: this.repository, detached: true, stdio: 'ignore', windowsHide: true }).unref()
    for (let waited = 0; waited < STARTED_WITHIN_MILLISECONDS; waited += CHECK_MILLISECONDS) {
      if (await answers(DRAWIO_PORT)) return
      await after(CHECK_MILLISECONDS)
    }
    throw new DrawioViewerNotStarted(this.command)
  }
}
