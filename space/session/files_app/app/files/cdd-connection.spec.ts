import { afterEach, describe, expect, it, vi } from 'vitest'

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

describe('cdd connection', () => {
  afterEach(() => vi.unstubAllGlobals())

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
        const text = asks.length === 1 ? 'session.file is still running after 10 seconds; it was not started again.' : '{"text":"the file"}'
        return Response.json({ jsonrpc: '2.0', id, result: { content: [{ text }] } })
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
})
