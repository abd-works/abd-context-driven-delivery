import { spawn } from 'node:child_process'
import { connect } from 'node:net'
import { join } from 'node:path'

import { DRAWIO_PORT, drawioEditorUrl, type DrawioOpener } from './files/files-paths'

const HOST = '127.0.0.1'
const STARTED_WITHIN_MILLISECONDS = 10_000
const CHECK_MILLISECONDS = 250

export class DrawioViewerNotStarted extends Error {
  constructor(command: string, port: number) {
    super(`The draw.io viewer did not answer on port ${port}: run ${command} from the repository root.`)
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
// so it outlives this server, as the person may keep editing a diagram. It answers on DRAWIO_PORT, or on the port it is
// given, as a spec's viewer does, so a spec never reaches the person's viewer.
export class DrawioViewer {
  constructor(
    private readonly repository: string,
    private readonly python: string = process.env.PYTHON || 'python',
    private readonly port: number = DRAWIO_PORT,
  ) {}

  private get script(): string {
    return join(this.repository, 'tools', 'drawio_viewer', 'drawio_viewer.py')
  }

  private get command(): string {
    return `${this.python} tools/drawio_viewer/drawio_viewer.py . ${this.port}`
  }

  // The editor's address for path, a file named from project's root (this repository's when none is named), the viewer
  // started first when it is down.
  // opened names the Files server the diagram's links to files go through, and the chat and ticket they open for.
  async urlOf(path: string, project = '', opened?: DrawioOpener): Promise<string> {
    if (!(await answers(this.port))) await this.start()
    return drawioEditorUrl(path, project, this.port, opened)
  }

  private async start(): Promise<void> {
    spawn(this.python, [this.script, this.repository, String(this.port)], { cwd: this.repository, detached: true, stdio: 'ignore', windowsHide: true }).unref()
    for (let waited = 0; waited < STARTED_WITHIN_MILLISECONDS; waited += CHECK_MILLISECONDS) {
      if (await answers(this.port)) return
      await after(CHECK_MILLISECONDS)
    }
    throw new DrawioViewerNotStarted(this.command, this.port)
  }
}
