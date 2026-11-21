import { afterEach, describe, expect, it, vi } from 'vitest'
import { tmpdir } from 'node:os'
import { join } from 'node:path'

import { CddConnection } from '@cdd/cdd-connection'

// The cdd server as fetch reaches it: it knows only the session it opened last, and answers 404 for any other.
function serverKnowing(session: string): string[] {
  const sessionsCalled: string[] = []
  vi.stubGlobal('fetch', async (_url: string, init: { headers: Record<string, string>; body: string }) => {
    const called = init.headers['mcp-session-id'] ?? ''
    sessionsCalled.push(called)
    if (called !== session) return new Response('{"error":{"message":"Session not found"}}', { status: 404 })
    const { id } = JSON.parse(init.body) as { id: number }
    return Response.json({ jsonrpc: '2.0', id, result: { content: [{ text: '"answered"' }] } })
  })
  return sessionsCalled
}

// A connection opened before the server restarted: it holds a session the server no longer knows, and opens the
// server's new one when asked to start again.
function connectionFromBeforeRestart(): CddConnection {
  const connection = new CddConnection('C:/project')
  const opened = connection as unknown as { session: Promise<unknown>; start: () => Promise<unknown> }
  opened.session = Promise.resolve({ url: 'http://127.0.0.1:1/mcp', headers: { 'mcp-session-id': 'before-restart' } })
  opened.start = async () => ({ url: 'http://127.0.0.1:1/mcp', headers: { 'mcp-session-id': 'after-restart' } })
  return connection
}

// Seed: a project folder that is not there, such as a ticket's worktree removed while its page stays open.
const REMOVED_PROJECT = join(tmpdir(), 'cdd-connection-project-removed')

describe('cdd connection', () => {
  afterEach(() => vi.unstubAllGlobals())

  describe('that is made for a project folder that is not there', () => {
    const calling = () => new CddConnection(REMOVED_PROJECT).call('session.show', {})

    it('should refuse the call, naming the folder as not there', async () => {
      await expect(calling()).rejects.toThrow(`The project folder ${REMOVED_PROJECT} is not there`)
    })

    it('should say nothing of the Python program, which is where it was', async () => {
      await expect(calling().catch(failure => String(failure.message).toLowerCase().includes('python'))).resolves.toBe(false)
    })
  })

  describe('that opened its session before the cdd server restarted', () => {
    it('should answer the next call on a new session rather than fail it', async () => {
      serverKnowing('after-restart')
      expect(await connectionFromBeforeRestart().call('session.show', {})).toBe('answered')
    })

    it('should send the call once on the old session and once on the new', async () => {
      const sessionsCalled = serverKnowing('after-restart')
      await connectionFromBeforeRestart().call('session.show', {})
      expect(sessionsCalled).toEqual(['before-restart', 'after-restart'])
    })
  })

  // A slow call, such as session.file reading the whole working copy, outlives the server's wait; the server says it is
  // still running, and the same call asked again waits for that run.
  describe("that makes a call still running at the server's time limit", () => {
    function serverStillRunningOnce(): number[] {
      const asks: number[] = []
      vi.stubGlobal('fetch', async (_url: string, init: { body: string }) => {
        const { id } = JSON.parse(init.body) as { id: number }
        asks.push(id)
        const stillRunning = asks.length === 1
        const text = stillRunning ? 'session.file is still running after 10 seconds; it was not started again.' : '{"text":"the file"}'
        const structuredContent = stillRunning ? { still_running: { tool: 'session.file', seconds: 10 } } : undefined
        return Response.json({ jsonrpc: '2.0', id, result: { content: [{ text }], structuredContent } })
      })
      return asks
    }

    it("should answer the call's result, never the notice", async () => {
      serverStillRunningOnce()
      expect(await connectionFromBeforeRestart().call('session.file', {})).toEqual({ text: 'the file' })
    })

    it('should ask the server again for the same call', async () => {
      const asks = serverStillRunningOnce()
      await connectionFromBeforeRestart().call('session.file', {})
      expect(asks.length).toBe(2)
    })
  })

  // A repin restarts the cdd server: for a few seconds nothing answers on its port, and a call already running is cut off.
  describe('that makes a call while the cdd server restarts', () => {
    function refused(): TypeError {
      return new TypeError('fetch failed', { cause: Object.assign(new Error('connect ECONNREFUSED 127.0.0.1:47800'), { code: 'ECONNREFUSED' }) })
    }

    function serverDownOnce(failure: () => Error): number[] {
      const asks: number[] = []
      vi.stubGlobal('fetch', async (_url: string, init: { body: string }) => {
        const { id } = JSON.parse(init.body) as { id: number }
        asks.push(id)
        if (asks.length === 1) throw failure()
        return Response.json({ jsonrpc: '2.0', id, result: { content: [{ text: '"answered"' }] } })
      })
      return asks
    }

    describe('with nothing answering on its port', () => {
      it('should answer the call once the server is back', async () => {
        serverDownOnce(refused)
        expect(await connectionFromBeforeRestart().call('graph.practice_names', {})).toBe('answered')
      })

      it('should send the call a second time', async () => {
        const asks = serverDownOnce(refused)
        await connectionFromBeforeRestart().call('graph.practice_names', {})
        expect(asks.length).toBe(2)
      })
    })

    describe('with the call cut off while it was answered', () => {
      it('should fail the call saying the server stopped while answering it', async () => {
        serverDownOnce(() => new TypeError('terminated'))
        await expect(connectionFromBeforeRestart().call('ticket.move_next', {})).rejects.toThrow('stopped')
      })

      it('should send the call only once, since it may already have run', async () => {
        const asks = serverDownOnce(() => new TypeError('terminated'))
        await connectionFromBeforeRestart().call('ticket.move_next', {}).catch(() => null)
        expect(asks.length).toBe(1)
      })
    })
  })

  // The server sends a call's answer as a stream of events, and a large answer arrives in many small pieces.
  describe('that is answered as a stream of events', () => {
    const PIECE_CHARACTERS = 4_096

    function serverStreaming(event: (id: number) => string): void {
      vi.stubGlobal('fetch', async (_url: string, init: { body: string }) => {
        const { id } = JSON.parse(init.body) as { id: number }
        const text = event(id)
        let sent = 0
        const body = new ReadableStream<Uint8Array>({
          pull(controller) {
            if (sent >= text.length) return controller.close()
            controller.enqueue(new TextEncoder().encode(text.slice(sent, sent + PIECE_CHARACTERS)))
            sent += PIECE_CHARACTERS
          },
        })
        return new Response(body, { headers: { 'content-type': 'text/event-stream' } })
      })
    }

    describe('with an answer of four million characters', () => {
      const LARGE = 'x'.repeat(4_000_000)

      it('should read the answer within three hundred milliseconds', { timeout: 300 }, async () => {
        serverStreaming(id => `event: message\r\ndata: ${JSON.stringify({ jsonrpc: '2.0', id, result: { content: [{ text: JSON.stringify(LARGE) }] } })}\r\n\r\n`)
        expect((await connectionFromBeforeRestart().call<string>('graph.inventory', {})).length).toBe(LARGE.length)
      })
    })

    describe('with an event whose data is not JSON', () => {
      it('should fail the call saying the answer could not be read', async () => {
        serverStreaming(() => 'event: message\r\ndata: {"jsonrpc": "2.0", "id": \r\n\r\n')
        await expect(connectionFromBeforeRestart().call('graph.inventory', {})).rejects.toThrow('could not be read')
      })
    })
  })
})
