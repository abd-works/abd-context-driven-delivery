import { execFileSync } from 'node:child_process'
import { existsSync } from 'node:fs'
import { join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

// The checkout these specs belong to, and the Python of its virtual environment, which the server runs on.
const CHECKOUT = resolve(fileURLToPath(new URL('.', import.meta.url)), '..', '..', '..', '..', '..')
const VENV_PYTHON = [join(CHECKOUT, '.venv', 'Scripts', 'python.exe'), join(CHECKOUT, '.venv', 'bin', 'python')]
const SPEC_SERVER = ['-m', 'harness.mcp.spec_support']
// Set by the install, so a process that inherits the environment knows the home is its run's, not the person's.
const RUN_HOME = 'CDD_SPEC_RUN_HOME'

const python = (): string => VENV_PYTHON.find(path => existsSync(path)) ?? 'python'

const runSpecServer = (...words: string[]): string =>
  execFileSync(python(), [...SPEC_SERVER, ...words], { cwd: CHECKOUT, encoding: 'utf-8', env: { ...process.env, PYTHONUTF8: '1' } })

// A ~/.cdd of the spec file's own, serving this checkout as it is on disk, on a port of its own. The cdd server it starts
// at the first call sees this checkout's code and the spec file's environment, such as its chats folder, and no other
// spec file's calls; the person's own cdd server is never touched.
// Playwright loads its config with type stripping alone, which cannot read constructor parameter properties.
export class ThrowawayCddHome {
  readonly folder: string
  readonly port: number

  private constructor(folder: string, port: number) {
    this.folder = folder
    this.port = port
  }

  static install(): ThrowawayCddHome {
    const { home, port } = JSON.parse(runSpecServer('install')) as { home: string; port: number }
    process.env.CDD_HOME = home
    process.env.CDD_SERVER_PORT = String(port)
    process.env[RUN_HOME] = home
    return new ThrowawayCddHome(home, port)
  }

  // One home for a whole Playwright run: its workers load the config again and inherit the home the run installed.
  static forRun(): ThrowawayCddHome {
    return ThrowawayCddHome.ofRun() ?? ThrowawayCddHome.install()
  }

  static ofRun(): ThrowawayCddHome | null {
    const home = process.env[RUN_HOME]
    return home ? new ThrowawayCddHome(home, Number(process.env.CDD_SERVER_PORT)) : null
  }

  close(): void {
    runSpecServer('stop', this.folder, String(this.port))
  }
}
