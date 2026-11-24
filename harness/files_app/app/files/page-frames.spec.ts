import { describe, expect, it } from 'vitest'

import type { CddApi } from '@cdd/cdd-shared'

import { FilesCallFailure } from './files-api'
import { PageFrames, pageWithBase } from './page-frames'

// Walk a generated UX mockup in its frame (review_files_in_files_app_story.test.md, View File In Source View): the page
// finds the scripts it names from its own folder of the project through the Files server, under the project's key.
// The real frame and server are the e2e's (open-files-in-files-app.story.ui_e2e_spec.py); here the server's answer is
// a fake.
const KEYED = '/page-files/a1b2/'

// Seed: the Files server's answer to the page's ask for its project's address, counting the asks.
class AnsweringServer implements CddApi {
  asks = 0
  constructor(private readonly answer: { base: string } | null) {}

  async post<Result>(): Promise<Result | null> {
    this.asks += 1
    return this.answer as Result | null
  }
}

describe('an HTML page shown in the Files app', () => {
  describe('with a head', () => {
    it('should find what it loads from the base address put first in its head', () => {
      expect(pageWithBase('<html><head lang="en"><script src="stories/x.js"></script></head></html>', 'http://127.0.0.1:8783/page-files/a1b2/')).toBe(
        '<html><head lang="en"><base href="http://127.0.0.1:8783/page-files/a1b2/"><script src="stories/x.js"></script></head></html>',
      )
    })
  })

  describe('with no head', () => {
    it('should find what it loads from the base address put before everything it holds', () => {
      expect(pageWithBase('<h1>Checkout</h1>', 'http://127.0.0.1:8783/page-files/a1b2/')).toBe('<base href="http://127.0.0.1:8783/page-files/a1b2/"><h1>Checkout</h1>')
    })
  })

  describe("in its project's subfolder", () => {
    it("should find what it loads from that folder, under the project's key", async () => {
      const page = await new PageFrames(new AnsweringServer({ base: KEYED })).pageOf('bookshop/my mockups/buy-a-book.html', '<h1>Buy</h1>')
      expect(page).toBe(`<base href="${new URL(`${KEYED}bookshop/my%20mockups/`, window.location.href).href}"><h1>Buy</h1>`)
    })
  })

  describe('that is the second page shown', () => {
    it("should ask the Files server for the project's address once", async () => {
      const server = new AnsweringServer({ base: KEYED })
      const frames = new PageFrames(server)
      await frames.pageOf('a.html', '<p>a</p>')
      await frames.pageOf('b.html', '<p>b</p>')
      expect(server.asks).toBe(1)
    })
  })

  describe("whose project's address the Files server did not answer", () => {
    it('should fail, saying no address was answered', async () => {
      await expect(new PageFrames(new AnsweringServer(null)).pageOf('a.html', '<p>a</p>')).rejects.toThrow(FilesCallFailure)
    })
  })
})
