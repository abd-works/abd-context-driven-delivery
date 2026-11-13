import { afterAll, beforeAll, beforeEach, describe, expect, it } from 'vitest'

import { BoardOnProject } from 'test-utils/board-page-support'

let board: BoardOnProject

beforeAll(async () => {
  board = await BoardOnProject.start()
})

beforeEach(() => board.reset())

afterAll(() => board.close())

describe('Reload Page On New Build', () => {
  it('should keep the page while the server serves the build it loaded', async () => {
    const { page } = await board.page()
    await page.build.check()
    await page.build.check()
    expect(page.store.state.isNewBuild).toBe(false)
  })

  // A page left open across a rebuild runs the old code, and shows none of what the rebuild changed.
  describe('with a new build deployed after the page loaded', () => {
    it('should ask for the page to be loaded again', async () => {
      let served = 'index-first.js'
      const { page } = board.unreadPage(send => (path, init) => (path === '/' ? Promise.resolve(new Response(`<script src="${served}">`)) : send(path, init)))
      await page.build.check()
      served = 'index-second.js'
      await page.build.check()
      expect(page.store.state.isNewBuild).toBe(true)
    })
  })

  // The board server serves its page itself, so its answer says nothing about whether cdd is back.
  describe('with cdd not connected', () => {
    it('should keep saying so after checking the build', async () => {
      const { page } = board.unreadPage()
      page.store.change({ serverFailure: 'The cdd server is not connected' })
      await page.build.check()
      expect(page.store.state.serverFailure).toBe('The cdd server is not connected')
    })
  })
})
