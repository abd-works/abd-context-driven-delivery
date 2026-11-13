import { readFileSync } from 'node:fs'
import { createServer, type Server } from 'node:http'
import type { AddressInfo } from 'node:net'
import { join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { afterAll, beforeAll, describe, expect, it } from 'vitest'

import { CddConnection, ProjectConnections } from '@cdd/cdd-connection'

import { STORY_MAP_PAGE } from '../../../../../cdd_guidance/practices/stories/app/story-map-page'
import { storyMapBuild } from '../../../../../cdd_guidance/practices/stories/app/story-map-routes'
import { createApp } from '../../packages/session-board/app'
import { BoardUpdate } from './board-update'

// Deploy Story UI App With Board State: the board's server serves the Story UI editor's built page at /story-map, on its
// own port, beside the board's page. The page is the one `npm run build` writes in the Stories practice's app folder,
// which App.install of the Story UI app runs. No request here reaches cdd, so the connection never starts.
const LOCAL = '127.0.0.1'
const APP_FOLDER = resolve(fileURLToPath(new URL('.', import.meta.url)), '..', '..')
const FILE_LINK = '?file=harness/.context/stories/story-map.md'
const storyMapIndex = (): string => readFileSync(join(storyMapBuild, 'index.html'), 'utf-8')

const freePort = (): Promise<number> =>
  new Promise(done => {
    const probe = createServer().listen(0, LOCAL, () => {
      const { port } = probe.address() as AddressInfo
      probe.close(() => done(port))
    })
  })

describe('Deploy Story UI App With Board State', () => {
  let server: Server
  let origin = ''

  beforeAll(async () => {
    const port = await freePort()
    const projects = new ProjectConnections(new CddConnection(APP_FOLDER))
    server = await new Promise<Server>(done => {
      const listening = createApp(projects, port, join(APP_FOLDER, 'dist'), new BoardUpdate(APP_FOLDER)).listen(port, LOCAL, () => done(listening))
    })
    origin = `http://${LOCAL}:${port}`
  })

  afterAll(() => new Promise<void>(done => server.close(() => done())))

  it("should answer the Story UI editor's page at /story-map on the board's own port", async () => {
    const page = await fetch(`${origin}${STORY_MAP_PAGE}/`)
    expect(await page.text()).toBe(storyMapIndex())
  })

  it("should answer the Story UI editor's page for a file link under /story-map", async () => {
    const page = await fetch(`${origin}${STORY_MAP_PAGE}/${FILE_LINK}`)
    expect(await page.text()).toBe(storyMapIndex())
  })

  it("should serve the Story UI editor's built script under /story-map", async () => {
    const script = storyMapIndex().match(/src="(\/story-map\/assets\/[^"]+\.js)"/)?.[1] ?? ''
    const answered = await fetch(`${origin}${script}`)
    expect(answered.headers.get('content-type')).toContain('javascript')
  })
})
