import { execFile } from 'node:child_process'
import { existsSync } from 'node:fs'
import { join, resolve } from 'node:path'

import { HttpException } from './http-exception'

const INTERNAL_ERROR = 500
// A build or an install prints more than execFile keeps by default.
const OUTPUT_BYTES = 16 * 1024 * 1024

export type Run = (command: string, args: string[], folder: string) => Promise<void>

type Step = { name: string; command: string; args: string[]; folder: string }

export class UpdateStepFailed extends HttpException {
  constructor(step: string, reason: string) {
    super(INTERNAL_ERROR, `Update failed at ${step}: ${reason}`)
    this.name = 'UpdateStepFailed'
  }
}

const runInFolder: Run = (command, args, folder) =>
  new Promise((done, failed) => {
    execFile(command, args, { cwd: folder, windowsHide: true, maxBuffer: OUTPUT_BYTES }, (error, _stdout, stderr) =>
      error ? failed(new Error(String(stderr).trim() || error.message)) : done(),
    )
  })

// The checkout's own virtual environment holds the packages the installer imports.
const pythonIn = (repository: string): string => {
  const inEnvironment = process.platform === 'win32' ? join(repository, '.venv', 'Scripts', 'python.exe') : join(repository, '.venv', 'bin', 'python')
  return existsSync(inEnvironment) ? inEnvironment : 'python'
}

// One press brings the board and every chat onto the checkout's latest commit: the installer pulls it through the
// repository and pins the cdd server to it, this server builds the page from it, then restarts so its own routes are
// the new ones too. The pin restarts the cdd server, so it runs as its own process rather than as a cdd call.
export class BoardUpdate {
  private readonly repository: string

  constructor(
    private readonly appFolder: string,
    private readonly restartServer: () => void = () => undefined,
    private readonly run: Run = runInFolder,
  ) {
    this.repository = resolve(appFolder, '..', '..', '..')
  }

  async update(): Promise<{ is_updated: boolean }> {
    for (const step of this.steps()) await this.runStep(step)
    return { is_updated: true }
  }

  // Called once the answer has gone out, so the page hears that the update worked before this server goes away.
  restart(): void {
    this.restartServer()
  }

  private steps(): Step[] {
    return [
      { name: 'get latest and re-pin', command: pythonIn(this.repository), args: ['scripts/install.py', '--ide', 'Claude', '--update'], folder: this.repository },
      { name: 'rebuild', command: process.execPath, args: [join(this.appFolder, 'node_modules', 'vite', 'bin', 'vite.js'), 'build'], folder: this.appFolder },
    ]
  }

  private async runStep(step: Step): Promise<void> {
    await this.run(step.command, step.args, step.folder).catch((failure: Error) => {
      throw new UpdateStepFailed(step.name, failure.message)
    })
  }
}
