import { execFile } from 'node:child_process'
import { statSync } from 'node:fs'
import { homedir } from 'node:os'
import { join, resolve } from 'node:path'

import { PROJECT_HEADER, type CddProgress } from './cdd-shared'

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

// The project folder a connection was made for is not there, such as a ticket's worktree removed while its page stays
// open. The connect script runs in that folder, and Node words a missing working folder as the program not found
// (`spawn python.exe ENOENT`), which sends the person to repair a Python and a cdd server that are both fine.
export class ProjectFolderMissingError extends Error {
  constructor(readonly folder: string) {
    super(`The project folder ${folder} is not there: it was moved or removed, such as a ticket's worktree closed since this page opened.`)
    this.name = 'ProjectFolderMissingError'
  }
}

// The server answered that it no longer knows this connection's session: it ran nothing.
class SessionGoneError extends CddNotConnectedError {}

// Nothing answered on the server's port, as for the seconds a repin restarts it: the call never reached a server.
class ServerNotAnsweringError extends CddNotConnectedError {}

// The connection refusals of Node's fetch: nothing was listening, so the request was never sent.
const REFUSED = 'ECONNREFUSED'
const isRefused = (failure: unknown): boolean => (failure as { cause?: { code?: string } } | null)?.cause?.code === REFUSED

export class CddAnswerUnreadableError extends Error {
  constructor(request: number, detail: string) {
    super(`The cdd server's answer to request ${request} could not be read: ${detail}`)
    this.name = 'CddAnswerUnreadableError'
  }
}

// The events of a stream the server writes, each ended by a blank line, read piece by piece as they arrive.
const EVENT_END = /\r?\n\r?\n/g
// The longest end of an event, \r\n\r\n, less one: how far back into the text already read a new piece's end can begin.
const EVENT_END_REACH = 3

class EventStream {
  // The pieces of the event not ended yet, kept apart and joined once its end arrives: searching all the text read so
  // far again for every piece takes hours on an answer of 300 MB.
  private readonly pieces: string[] = []
  private tail = ''

  // The events piece completes, oldest first; what follows the last one waits for the next piece. Only the new piece,
  // and the few characters before it where an end could begin, are searched.
  read(piece: string): string[] {
    const searched = this.tail + piece
    EVENT_END.lastIndex = 0
    if (!EVENT_END.test(searched)) {
      this.keep(piece)
      return []
    }
    const text = [...this.pieces, piece].join('')
    this.pieces.length = 0
    this.tail = ''
    const events = text.split(EVENT_END)
    this.keep(events.pop() ?? '')
    return events
  }

  private keep(piece: string): void {
    if (!piece) return
    this.pieces.push(piece)
    this.tail = (this.tail + piece).slice(-EVENT_END_REACH)
  }
}

type Session = { url: string; headers: Record<string, string> }
type Message = { id?: number; method?: string; params?: { progressToken?: number; message?: string }; result?: unknown; error?: { message?: string } }
type ToolResult = { content?: { text?: string }[]; isError?: boolean; structuredContent?: { still_running?: { tool: string; seconds: number } } }
// How often a connection asks again for a call the cdd server answers is still running at its time limit
// (harness/mcp/tool_calls.py), each ask waiting up to the server's own limit, before it gives up.
const STILL_RUNNING_ASKS = 60

const cddHome = (): string => process.env.CDD_HOME ?? join(homedir(), '.cdd')

// Talks to the one cdd server every chat shares, over MCP's Streamable HTTP, as the project it was made for. The server's
// own connect script starts the server when none answers and names the project for every request.
// Each object's adapter names its own tools, so this class names none.
export class CddConnection {
  private session: Promise<Session> | null = null
  private readonly running = new Map<number, { label: string; step?: string }>()
  private nextId = 1

  constructor(readonly project: string = SOURCE_ROOT) {}

  // A server restarted since this connection opened no longer knows its session and runs nothing for it, so the call
  // is sent once more on a new session rather than failing the page that made it.
  async call<Result>(tool: string, args: Record<string, unknown>): Promise<Result> {
    for (let asked = 1; ; asked += 1) {
      const result = await this.answered(tool, args)
      const text = result.content?.[0]?.text ?? ''
      if (!result.structuredContent?.still_running) return this.parsed<Result>(text)
      if (asked >= STILL_RUNNING_ASKS) throw new CddToolError(tool, text)
    }
  }

  // A call that outlives the server's wait is still running there and answers so; asking again with the same arguments
  // waits for that same run, so the page gets the call's result, never the notice. A server that no longer knows this
  // connection's session (restarted), or that did not answer at all (restarting), ran nothing, so the call is sent once
  // more on a new session, whose connect script starts the server when none answers. A call cut off while it was
  // answered may already have run, so it is never sent again.
  private async answered(tool: string, args: Record<string, unknown>): Promise<ToolResult> {
    const result = (await this.calledOnce(tool, args).catch(failure => {
      if (failure instanceof SessionGoneError || failure instanceof ServerNotAnsweringError) return this.calledOnce(tool, args)
      throw failure
    })) as ToolResult
    const text = result.content?.[0]?.text
    if (result.isError || text === undefined) throw new CddToolError(tool, text ?? 'no result')
    return result
  }

  private async calledOnce(tool: string, args: Record<string, unknown>): Promise<unknown> {
    return this.request(await this.connected(), 'tools/call', { name: tool, arguments: args }, tool)
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
      if (failure instanceof CddNotConnectedError || failure instanceof ProjectFolderMissingError) throw failure
      throw new CddNotConnectedError(failure instanceof Error ? failure.message : String(failure))
    })
    return this.session
  }

  private async start(): Promise<Session> {
    const { url, headers } = JSON.parse(await this.connectScriptOutput()) as Session
    const opening: Session = { url, headers: { ...headers, 'mcp-protocol-version': PROTOCOL_VERSION } }
    const opened = await this.post(opening, { jsonrpc: '2.0', id: this.nextId++, method: 'initialize', params: { protocolVersion: PROTOCOL_VERSION, capabilities: {}, clientInfo: { name: 'cdd-language-adapter', version: '1' } } })
    const sessionId = opened.headers.get(SESSION_HEADER)
    await opened.text()
    const session: Session = { url, headers: { ...opening.headers, ...(sessionId ? { [SESSION_HEADER]: sessionId } : {}) } }
    await (await this.post(session, { jsonrpc: '2.0', method: 'notifications/initialized' })).text()
    return session
  }

  // The connect script runs in the project's own folder, so the header it prints names that project. Asked for the
  // address, it prints the server's address too, so this connection never reads the file the server publishes it in.
  private connectScriptOutput(): Promise<string> {
    const script = join(cddHome(), 'connect.py')
    if (!statSync(this.project, { throwIfNoEntry: false })?.isDirectory()) return Promise.reject(new ProjectFolderMissingError(this.project))
    return new Promise((resolve, reject) => {
      execFile(process.env.CDD_PYTHON ?? PYTHON, [script, '--address'], { cwd: this.project, timeout: LONGEST_TOOL_MILLISECONDS }, (failure, stdout, stderr) =>
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
      if (isRefused(failure)) throw new ServerNotAnsweringError(`nothing answered at ${session.url}`)
      throw this.stopped(failure)
    }
    // A restarted server no longer knows this session, so the next call opens a new one.
    if (response.status === 404 && session.headers[SESSION_HEADER]) {
      this.session = null
      throw new SessionGoneError(`${response.status} ${await response.text()}`)
    }
    if (!response.ok) throw new CddNotConnectedError(`${response.status} ${await response.text()}`)
    return response
  }

  // A request the server took and then stopped answering: cut off, as when a repin restarts the server, or past the
  // ten-minute limit. It may already have run, so the failure says so and the call is not sent again.
  private stopped(failure: unknown): CddNotConnectedError {
    const reason = failure instanceof Error ? failure.message : String(failure)
    if (failure instanceof Error && failure.name === 'TimeoutError') return new CddNotConnectedError(`no answer within ${LONGEST_TOOL_MILLISECONDS / 60_000} minutes (${reason})`)
    return new CddNotConnectedError(`the cdd server stopped while answering, as when a repin restarts it; the call may have run, so it was not sent again (${reason})`)
  }

  // The server answers a request as plain JSON or as a stream of events: progress reports first, the reply last.
  private async replyTo(id: number, response: Response): Promise<Message> {
    if (!(response.headers.get('content-type') ?? '').includes('text/event-stream')) return (await response.json()) as Message
    const reader = response.body!.pipeThrough(new TextDecoderStream()).getReader()
    const events = new EventStream()
    for (;;) {
      const { value, done } = await reader.read().catch(failure => {
        this.session = null
        throw this.stopped(failure)
      })
      if (done) throw new CddNotConnectedError(`the server closed the stream before answering request ${id}`)
      for (const message of events.read(value).map(event => this.messageIn(id, event))) {
        if (message?.method === 'notifications/progress') this.reported(message)
        else if (message?.id === id) return message
      }
    }
  }

  // An event whose data is not JSON fails the call: dropped, it would leave the call waiting for a reply already sent.
  private messageIn(id: number, event: string): Message | null {
    const data = event
      .split(/\r?\n/)
      .filter(line => line.startsWith('data:'))
      .map(line => line.slice(5).trimStart())
      .join('\n')
    if (!data) return null
    try {
      return JSON.parse(data) as Message
    } catch (failure) {
      throw new CddAnswerUnreadableError(id, `${failure instanceof Error ? failure.message : String(failure)}; it began ${JSON.stringify(data.slice(0, 200))}`)
    }
  }

  private reported(notification: Message): void {
    const call = this.running.get(notification.params?.progressToken ?? -1)
    if (call && notification.params?.message) call.step = notification.params.message
  }

  // The server marks a failed operation's answer as an error, read before this. A successful one is JSON, except an
  // operation that answers a string, such as chats.open's link: the server sends that as the text itself.
  private parsed<Result>(text: string): Result {
    try {
      return JSON.parse(text) as Result
    } catch {
      return text as Result
    }
  }
}

// A request as any server framework hands it: what it names in a header.
type NamingRequest = { get(name: string): string | undefined }

// One app server serves every repository on this machine, each through a cdd connection of its own, so a page opened
// for a chat's repository shows that repository, in the session open there, rather than the one the server started in.
export class ProjectConnections {
  private readonly connections = new Map<string, CddConnection>()

  constructor(
    private readonly started: CddConnection,
    private readonly connect: (folder: string) => CddConnection = folder => new CddConnection(folder),
  ) {}

  // The connection of the repository the request names in its project header; the started one for a request naming none.
  of(request: NamingRequest): CddConnection {
    const named = request.get(PROJECT_HEADER)?.trim()
    if (!named) return this.started
    const folder = resolve(named)
    let connection = this.connections.get(folder)
    if (!connection) {
      connection = this.connect(folder)
      this.connections.set(folder, connection)
    }
    return connection
  }

  async close(): Promise<void> {
    await Promise.all([this.started, ...this.connections.values()].map(connection => connection.close()))
  }
}
