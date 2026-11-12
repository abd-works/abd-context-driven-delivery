import { describe, expect, it } from 'vitest'

import { BoardApi, projectOfPage, type Send } from './board-api'
import { BoardStore } from '../shared/board-store'

// The page opened from a chat's /board link names that chat's repository, and every call it makes names it too, so the
// server reads that repository's board.
describe('Show The Board Of The Linked Repository', () => {
  const sent: Headers[] = []
  const recording: Send = (_path, init) => {
    sent.push(new Headers(init?.headers))
    return Promise.resolve(Response.json({}))
  }

  describe('with a page opened at ?project=C:/dev/sandbox', () => {
    it('should read the project from the link', () => {
      expect(projectOfPage('?project=C%3A%2Fdev%2Fsandbox&report=main')).toBe('C:/dev/sandbox')
    })

    it('should name the project on every call', async () => {
      sent.length = 0
      const api = new BoardApi(new BoardStore(), recording, 'C:/dev/sandbox')
      await api.post('/board/show')
      await api.get('/build')
      expect(sent.map(headers => headers.get('X-CDD-Project'))).toEqual(['C:/dev/sandbox', 'C:/dev/sandbox'])
    })
  })

  describe('with a page opened without a project', () => {
    it('should name no project, so the server shows its own', async () => {
      sent.length = 0
      await new BoardApi(new BoardStore(), recording, '').post('/board/show')
      expect(sent[0]?.has('X-CDD-Project')).toBe(false)
    })
  })
})
