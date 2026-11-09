import { describe, expect, it } from 'vitest'

import { headlineOf } from './board-page-view'

// A server that is down answers with whatever its process printed, often a whole Python traceback; the band shows one line.
describe('Display Board Server Health', () => {
  describe('with the server answering with a Python traceback', () => {
    const failure = 'Traceback (most recent call last):\n  File "server.py", line 3, in <module>\n    serve()\nConnectionResetError: [WinError 10054] An existing connection was forcibly closed\n'

    it('should show the exception line alone', () => {
      expect(headlineOf(failure)).toBe('ConnectionResetError: [WinError 10054] An existing connection was forcibly closed')
    })
  })

  describe('with a one-line failure', () => {
    it('should show it as it is', () => {
      expect(headlineOf('fetch failed')).toBe('fetch failed')
    })
  })
})
