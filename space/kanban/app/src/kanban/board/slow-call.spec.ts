import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { BoardApi } from './board-api'
import { BoardStore } from './board-store'

// A call the cdd server is too busy to answer says so, so a dialog that waits on it does not look as if nothing happened.
describe('Show A Slow Call', () => {
  beforeEach(() => vi.useFakeTimers())
  afterEach(() => vi.useRealTimers())

  const hanging = () => new Promise<Response>(() => undefined)

  describe('with a ticket call still running after eight seconds', () => {
    it('should say what it is still waiting on', async () => {
      const store = new BoardStore()
      void new BoardApi(store, hanging).post('/ticket/checkout-flow/branch')
      await vi.advanceTimersByTimeAsync(8_000)
      expect(store.state.toasts.map(toast => toast.text)).toEqual(['Still waiting on ticket/checkout-flow/branch: the cdd server is busy, so it can take a while.'])
    })
  })

  describe("with the board's own read still running", () => {
    it('should say nothing, since it reads again every two seconds', async () => {
      const store = new BoardStore()
      void new BoardApi(store, hanging).post('/board/show')
      await vi.advanceTimersByTimeAsync(8_000)
      expect(store.state.toasts).toEqual([])
    })
  })
})
