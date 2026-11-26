// @vitest-environment node
import express from 'express'
import { mkdirSync, mkdtempSync, writeFileSync } from 'node:fs'
import type { AddressInfo } from 'node:net'
import type { Server } from 'node:http'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { afterAll, beforeAll, describe, expect, it } from 'vitest'

import { PageFiles } from './page-files'

// Walk a generated UX mockup in its frame (review_files_in_files_app_story.test.md, View File In Source View): what
// the Files server serves the page's frame. The page itself in a real browser is the e2e's
// (open-files-in-files-app.story.ui_e2e_spec.py).

// Seed: a project holding a mockup's story module and a secret beside it, a file outside the project, and the Story
// Demo folder of a CDD install.
const top = mkdtempSync(join(tmpdir(), 'cdd-page-files-'))
const project = join(top, 'project')
const storyDemo = join(top, 'story-demo')
for (const [path, text] of [
  [join(project, 'bookshop', 'stories', 'buy_a_book_stories.js'), 'export const story = 1\n'],
  [join(project, '.env'), 'TOKEN=secret\n'],
  [join(top, 'outside.js'), 'export const outside = 1\n'],
  [join(storyDemo, 'mount-generated-mockup.js'), 'export const mounted = 1\n'],
]) {
  mkdirSync(join(path, '..'), { recursive: true })
  writeFileSync(path, text)
}

describe("the files a page in the Files app's frame asks for", () => {
  const pageFiles = new PageFiles(storyDemo)
  const base = pageFiles.baseOf(project)
  let server: Server
  let origin = ''

  beforeAll(async () => {
    const app = express()
    pageFiles.serveOn(app)
    server = app.listen(0, '127.0.0.1')
    await new Promise(resolve => server.once('listening', resolve))
    origin = `http://127.0.0.1:${(server.address() as AddressInfo).port}`
  })

  afterAll(() => {
    server.close()
  })

  describe("a script of the project, under the project's key", () => {
    it('should be served to a frame of no origin', async () => {
      const response = await fetch(`${origin}${base}bookshop/stories/buy_a_book_stories.js`)
      expect([response.status, response.headers.get('access-control-allow-origin'), await response.text()]).toEqual([200, '*', 'export const story = 1\n'])
    })
  })

  describe('the same project asked for again', () => {
    it('should keep the key it was given first', () => {
      expect(pageFiles.baseOf(project)).toBe(base)
    })
  })

  describe('a Story Demo script of the CDD install', () => {
    it('should be served to a frame of no origin', async () => {
      const response = await fetch(`${origin}/practices/ux/story-demo/mount-generated-mockup.js`)
      expect([response.status, response.headers.get('access-control-allow-origin')]).toEqual([200, '*'])
    })
  })

  describe('a file the page names that is not there', () => {
    it('should be not found, readable as such by the frame', async () => {
      const response = await fetch(`${origin}${base}bookshop/domain/cart.js`)
      expect([response.status, response.headers.get('access-control-allow-origin')]).toEqual([404, '*'])
    })
  })

  describe('a key this server never made', () => {
    it('should find nothing', async () => {
      expect((await fetch(`${origin}/page-files/guessed/bookshop/stories/buy_a_book_stories.js`)).status).toBe(404)
    })
  })

  describe('a path that climbs out of the project', () => {
    it('should not reach the file outside it', async () => {
      const response = await fetch(`${origin}${base}..%2Foutside.js`)
      expect(response.status).not.toBe(200)
    })
  })

  describe("a dotfile of the project, such as its .env", () => {
    it('should not be served', async () => {
      expect((await fetch(`${origin}${base}.env`)).status).toBe(404)
    })
  })
})
