import { existsSync } from 'node:fs'
import { delimiter, dirname, join } from 'node:path'
import { Client } from '@modelcontextprotocol/sdk/client/index.js'
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js'

import type { CddConnection } from '@cdd/cdd-connection'

const LONGEST_TOOL_MILLISECONDS = 600_000
const VENV_PYTHON = join('.venv', 'Scripts', 'python.exe')
const PRIMARY_CLONE = 'abd-context-driven-delivery'
const GUIDANCE_FOLDERS = ['practices', 'actions', 'patterns', 'builders']

export class CddToolError extends Error {
  constructor(tool: string, detail: string) {
    super(`cdd ${tool} failed: ${detail}`)
    this.name = 'CddToolError'
  }
}

export class CddNotConnectedError extends Error {
  constructor(detail: string) {
    super(`The cdd server is not connected: ${detail}`)
    this.name = 'CddNotConnectedError'
  }
}

export type CddLocation = { sourceRoot: string; project: string; python: string }

// A linked worktree has no .venv of its own, so the clone beside it that does is searched for.
export function locateCdd(sourceRoot: string, env: NodeJS.ProcessEnv): CddLocation {
  const candidates = [join(sourceRoot, VENV_PYTHON), join(dirname(sourceRoot), PRIMARY_CLONE, VENV_PYTHON)]
  const python = env.CDD_PYTHON ?? candidates.find(existsSync)
  if (!python) throw new CddNotConnectedError(`no Python found; set CDD_PYTHON or create ${candidates[0]}`)
  return { sourceRoot, project: env.BOARD_PROJECT ?? sourceRoot, python }
}

const pythonPathOf = (root: string): string =>
  [root, join(root, 'tools'), ...GUIDANCE_FOLDERS.map(folder => join(root, 'cdd_guidance', folder))].join(delimiter)

// Starts one cdd server, the same tools the chat calls, and carries calls to it. Each object's adapter class names its own tools.
export class CddConnectionNode implements CddConnection {
  private client: Promise<Client> | null = null

  constructor(private readonly location: CddLocation) {}

  private connect(): Promise<Client> {
    const { sourceRoot, project, python } = this.location
    const env = { ...process.env, PYTHONPATH: pythonPathOf(sourceRoot), PYTHONIOENCODING: 'utf-8', CDD_PROJECT: project } as Record<string, string>
    const transport = new StdioClientTransport({ command: python, args: ['-u', join(sourceRoot, 'harness', 'mcp', 'scripts', 'start_host.py')], env, cwd: project, stderr: 'ignore' })
    const client = new Client({ name: 'cdd-session-board', version: '0.1.0' })
    transport.onclose = () => {
      this.client = null
    }
    return client.connect(transport).then(() => client)
  }

  private connected(): Promise<Client> {
    this.client ??= this.connect().catch(failure => {
      this.client = null
      throw new CddNotConnectedError(String(failure))
    })
    return this.client
  }

  async call<Result>(tool: string, args: Record<string, unknown>): Promise<Result> {
    const client = await this.connected()
    const result = await client.callTool({ name: tool, arguments: args }, undefined, { timeout: LONGEST_TOOL_MILLISECONDS })
    const text = (result.content as { text?: string }[])[0]?.text
    if (result.isError || text === undefined) throw new CddToolError(tool, text ?? 'no result')
    return this.parsed<Result>(tool, text)
  }

  // The server sends a failed operation's error as plain text, and every successful operation as JSON.
  private parsed<Result>(tool: string, text: string): Result {
    try {
      return JSON.parse(text) as Result
    } catch {
      throw new CddToolError(tool, text)
    }
  }

  async close(): Promise<void> {
    const open = this.client
    this.client = null
    if (open) await (await open).close()
  }
}
