import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { BoardPage } from './board-page'

// A cdd server that has not answered yet: every request the page sends stays pending, and each one is counted.
function slowServer() {
  const asked: string[] = []
  const send = (path: string) => {
    asked.push(path)
    return new Promise<Response>(() => undefined)
  }
  return { asked, send }
}

describe('Board Page', () => {
  beforeEach(() => vi.useFakeTimers())
  afterEach(() => vi.useRealTimers())

  // Each pending poll holds a connection on the cdd server, so a slow server must not collect one per tick.
  describe('that polls the chats while the cdd server answers slowly', () => {
    it('should ask for the build again only once the last answer came back', () => {
      const server = slowServer()
      const stop = new BoardPage(server.send).start()
      vi.advanceTimersByTime(20_000)
      stop()
      expect(server.asked.filter(path => path.endsWith('/build')).length).toBe(1)
    })
  })
})
