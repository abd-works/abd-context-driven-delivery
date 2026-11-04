import { execFile } from 'node:child_process'
import { readFileSync } from 'node:fs'
import { homedir } from 'node:os'
import { join } from 'node:path'

import type { CddProgress } from './cdd-shared'

// Written by the installer from the checkout and the Python it ran with.
const SOURCE_ROOT = __SOURCE_ROOT__
const PYTHON = __PYTHON__
const PROTOCOL_VERSION = '2025-06-18'
const LONGEST_TOOL_MILLISECONDS = 600_000
const SESSION_HEADER = 'mcp-session-id'

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

type Session = { url: string; headers: Record<string, string> }
type Message = { id?: number; method?: string; params?: { progressToken?: number; message?: string }; result?: unknown; error?: { message?: string } }
type ToolResult = { content?: { text?: string }[]; isError?: boolean }

const cddHome = (): string => process.env.CDD_HOME ?? join(homedir(), '.cdd')

// Talks to the one cdd server every chat shares, over MCP's Streamable HTTP, as the project it was made for. The server's
// own connect script starts the server when none answers and names the project for every request.
// Each object's adapter names its own tools, so this class names none.
export class CddConnection {
  private session: Promise<Session> | null = null
  private readonly running = new Map<number, { label: string; step?: string }>()
  private nextId = 1

  constructor(private readonly project: string = SOURCE_ROOT) {}

  async call<Result>(tool: string, args: Record<string, unknown>): Promise<Result> {
    const session = await this.connected()
    const result = (await this.request(session, 'tools/call', { name: tool, arguments: args }, tool)) as ToolResult
    const text = result.content?.[0]?.text
    if (result.isError || text === undefined) throw new CddToolError(tool, text ?? 'no result')
    return this.parsed<Result>(tool, text)
  }

  // The newest step each running call has reported, for a page waiting on one; a finished call reports nothing.
  progress(): CddProgress[] {
    return [...this.running.values()].flatMap(call => (call.step ? [{ tool: call.label, message: call.step }] : []))
  }

  // Ends this connection's session. The server keeps running for every other chat and connection.
  async close(): Promise<void> {
    const open = this.session
    this.session = null
    const session = await open?.catch(() => null)
    if (session) await fetch(session.url, { method: 'DELETE', headers: session.headers }).catch(() => null)
  }

  private connected(): Promise<Session> {
    this.session ??= this.start().catch(failure => {
      this.session = null
      if (failure instanceof CddNotConnectedError) throw failure
      throw new CddNotConnectedError(failure instanceof Error ? failure.message : String(failure))
    })
    return this.session
  }

  private async start(): Promise<Session> {
    const projectHeaders = JSON.parse(await this.connectScriptOutput()) as Record<string, string>
    const { url } = JSON.parse(readFileSync(join(cddHome(), 'server.json'), 'utf-8')) as { url: string }
    const opening: Session = { url, headers: { ...projectHeaders, 'mcp-protocol-version': PROTOCOL_VERSION } }
    const opened = await this.post(opening, { jsonrpc: '2.0', id: this.nextId++, method: 'initialize', params: { protocolVersion: PROTOCOL_VERSION, capabilities: {}, clientInfo: { name: 'cdd-language-adapter', version: '1' } } })
    const sessionId = opened.headers.get(SESSION_HEADER)
    await opened.text()
    const session: Session = { url, headers: { ...opening.headers, ...(sessionId ? { [SESSION_HEADER]: sessionId } : {}) } }
    await (await this.post(session, { jsonrpc: '2.0', method: 'notifications/initialized' })).text()
    return session
  }

  // The connect script runs in the project's own folder, so the header it prints names that project.
  private connectScriptOutput(): Promise<string> {
    const script = join(cddHome(), 'connect.py')
    return new Promise((resolve, reject) => {
      execFile(process.env.CDD_PYTHON ?? PYTHON, [script], { cwd: this.project, timeout: LONGEST_TOOL_MILLISECONDS }, (failure, stdout, stderr) =>
        failure ? reject(new CddNotConnectedError(`${script} failed: ${stderr.trim() || failure.message}`)) : resolve(stdout.trim()),
      )
    })
  }

  private async request(session: Session, method: string, params: Record<string, unknown>, label = method): Promise<unknown> {
    const id = this.nextId++
    this.running.set(id, { label })
    try {
      // Every tool call asks for progress under its own id, so a report finds the call it belongs to.
      const sent = method === 'tools/call' ? { ...params, _meta: { progressToken: id } } : params
      const response = await this.post(session, { jsonrpc: '2.0', id, method, params: sent })
      const reply = await this.replyTo(id, response)
      if (reply.error) throw new CddToolError(label, reply.error.message ?? 'no message')
      return reply.result
    } finally {
      this.running.delete(id)
    }
  }

  private async post(session: Session, message: Record<string, unknown>): Promise<Response> {
    let response: Response
    try {
      response = await fetch(session.url, {
        method: 'POST',
        headers: { ...session.headers, 'content-type': 'application/json', accept: 'application/json, text/event-stream' },
        body: JSON.stringify(message),
        signal: AbortSignal.timeout(LONGEST_TOOL_MILLISECONDS),
      })
    } catch (failure) {
      this.session = null
      throw new CddNotConnectedError(failure instanceof Error ? failure.message : String(failure))
    }
    // A restarted server no longer knows this session, so the next call opens a new one.
    if (response.status === 404) this.session = null
    if (!response.ok) throw new CddNotConnectedError(`${response.status} ${await response.text()}`)
    return response
  }

  // The server answers a request as plain JSON or as a stream of events: progress reports first, the reply last.
  private async replyTo(id: number, response: Response): Promise<Message> {
    if (!(response.headers.get('content-type') ?? '').includes('text/event-stream')) return (await response.json()) as Message
    const reader = response.body!.pipeThrough(new TextDecoderStream()).getReader()
    let buffered = ''
    for (;;) {
      const { value, done } = await reader.read()
      if (done) throw new CddNotConnectedError(`the server closed the stream before answering request ${id}`)
      buffered += value
      const events = buffered.split(/\r?\n\r?\n/)
      buffered = events.pop() ?? ''
      for (const message of events.map(event => this.messageIn(event))) {
        if (message?.method === 'notifications/progress') this.reported(message)
        else if (message?.id === id) return message
      }
    }
  }

  private messageIn(event: string): Message | null {
    const data = event
      .split(/\r?\n/)
      .filter(line => line.startsWith('data:'))
      .map(line => line.slice(5).trimStart())
      .join('\n')
    try {
      return data ? (JSON.parse(data) as Message) : null
    } catch {
      return null
    }
  }

  private reported(notification: Message): void {
    const call = this.running.get(notification.params?.progressToken ?? -1)
    if (call && notification.params?.message) call.step = notification.params.message
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
