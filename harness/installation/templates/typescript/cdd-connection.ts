import { spawn, type ChildProcessByStdio } from 'node:child_process'
import { delimiter, join } from 'node:path'
import { createInterface } from 'node:readline'
import type { Readable, Writable } from 'node:stream'

// Written by the installer from the checkout and the Python it ran with.
const SOURCE_ROOT = __SOURCE_ROOT__
const PYTHON = __PYTHON__
const GUIDANCE_FOLDERS = ['practices', 'actions', 'patterns', 'builders']
const PROTOCOL_VERSION = '2025-06-18'
const LONGEST_TOOL_MILLISECONDS = 600_000

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

type Server = ChildProcessByStdio<Writable, Readable, null>
type Reply = { id?: number; method?: string; result?: unknown; error?: { message?: string } }
type Waiting = { label: string; resolve: (result: unknown) => void; reject: (failure: Error) => void; timer: ReturnType<typeof setTimeout> }
type ToolResult = { content?: { text?: string }[]; isError?: boolean }

const pythonPathOf = (root: string): string =>
  [root, join(root, 'tools'), ...GUIDANCE_FOLDERS.map(folder => join(root, 'cdd_guidance', folder))].join(delimiter)

// Starts one cdd server, the same tools the agent calls, and carries calls to it over MCP on its standard input and output.
// Each object's adapter names its own tools, so this class names none.
export class CddConnection {
  private server: Promise<Server> | null = null
  private readonly waiting = new Map<number, Waiting>()
  private nextId = 1

  constructor(private readonly project: string = SOURCE_ROOT) {}

  async call<Result>(tool: string, args: Record<string, unknown>): Promise<Result> {
    const server = await this.connected()
    const result = (await this.request(server, 'tools/call', { name: tool, arguments: args }, tool)) as ToolResult
    const text = result.content?.[0]?.text
    if (result.isError || text === undefined) throw new CddToolError(tool, text ?? 'no result')
    return this.parsed<Result>(tool, text)
  }

  async close(): Promise<void> {
    const open = this.server
    this.server = null
    const server = await open?.catch(() => null)
    server?.stdin.end()
    server?.kill()
  }

  private connected(): Promise<Server> {
    this.server ??= this.start().catch(failure => {
      this.server = null
      if (failure instanceof CddNotConnectedError) throw failure
      throw new CddNotConnectedError(failure instanceof Error ? failure.message : String(failure))
    })
    return this.server
  }

  private async start(): Promise<Server> {
    const env = { ...process.env, PYTHONPATH: pythonPathOf(SOURCE_ROOT), PYTHONIOENCODING: 'utf-8', CDD_PROJECT: this.project }
    const script = join(SOURCE_ROOT, 'harness', 'mcp', 'scripts', 'start_host.py')
    const server = spawn(process.env.CDD_PYTHON ?? PYTHON, ['-u', script], { cwd: this.project, env, stdio: ['pipe', 'pipe', 'ignore'] })
    createInterface({ input: server.stdout }).on('line', line => this.received(line))
    server.once('error', failure => this.stopped(server, failure.message))
    server.once('exit', code => this.stopped(server, `the server exited with ${code}`))
    await this.request(server, 'initialize', { protocolVersion: PROTOCOL_VERSION, capabilities: {}, clientInfo: { name: 'cdd-language-adapter', version: '1' } })
    this.send(server, { jsonrpc: '2.0', method: 'notifications/initialized' })
    return server
  }

  private request(server: Server, method: string, params: Record<string, unknown>, label = method): Promise<unknown> {
    const id = this.nextId++
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => this.settled(id)?.reject(new CddToolError(label, 'timed out')), LONGEST_TOOL_MILLISECONDS)
      this.waiting.set(id, { label, resolve, reject, timer })
      this.send(server, { jsonrpc: '2.0', id, method, params })
    })
  }

  private send(server: Server, message: Record<string, unknown>): void {
    server.stdin.write(`${JSON.stringify(message)}\n`)
  }

  // The server's own requests and notifications carry a method, and only replies settle a call.
  private received(line: string): void {
    const reply = this.replyIn(line)
    if (!reply || reply.method !== undefined || reply.id === undefined) return
    const waiting = this.settled(reply.id)
    if (!waiting) return
    if (reply.error) waiting.reject(new CddToolError(waiting.label, reply.error.message ?? 'no message'))
    else waiting.resolve(reply.result)
  }

  private replyIn(line: string): Reply | null {
    try {
      return JSON.parse(line) as Reply
    } catch {
      return null
    }
  }

  private settled(id: number): Waiting | undefined {
    const waiting = this.waiting.get(id)
    this.waiting.delete(id)
    if (waiting) clearTimeout(waiting.timer)
    return waiting
  }

  private stopped(server: Server, detail: string): void {
    void this.server?.then(current => (current === server ? (this.server = null) : null), () => null)
    for (const id of [...this.waiting.keys()]) this.settled(id)?.reject(new CddNotConnectedError(detail))
  }

  // The server sends a failed operation's error as plain text, and every successful operation as JSON.
  private parsed<Result>(tool: string, text: string): Result {
    try {
      return JSON.parse(text) as Result
    } catch {
      throw new CddToolError(tool, text)
    }
  }
}
