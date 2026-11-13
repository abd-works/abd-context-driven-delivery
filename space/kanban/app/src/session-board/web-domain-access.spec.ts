import { readdirSync, readFileSync, statSync } from 'node:fs'
import { join, relative, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import type { Express } from 'express'
import { describe, expect, it } from 'vitest'

import { CddConnection, ProjectConnections } from '@cdd/cdd-connection'

import { createApp } from '../../packages/session-board/app'
import { BoardUpdate } from './board-update'
import { API_ROOT, BOARD_SERVER_PATHS } from './board-server-paths'

// Refactor Kanban Board To Web Domain Access: the page reaches the CDD domain only through the generated clients, and the
// board's server mounts only the generated routes for it. No request is sent here, so the connection never starts.
const APP_FOLDER = resolve(fileURLToPath(new URL('.', import.meta.url)), '..', '..')
const KANBAN = join(APP_FOLDER, 'src', 'kanban')
// The domain objects whose routes the installer generates, as a route names them.
const DOMAIN_ROUTE = /['`]\/(board|stage|ticket|fidelity-progress|backlog-item|session|practice-session-output|fidelity-session-output|chat|app|file-manager|story-model)\//
// A post whose path the page spells out itself.
const HAND_WRITTEN_POST = /\.post(<[^>]*>)?\(\s*['`]/

type Layer = { route?: { path: string }; name: string; handle: { stack?: Layer[] } }

function pageSources(folder: string): string[] {
  return readdirSync(folder).flatMap(name => {
    const path = join(folder, name)
    if (statSync(path).isDirectory()) return pageSources(path)
    return /\.tsx?$/.test(name) && !name.endsWith('.spec.ts') ? [path] : []
  })
}

const sourcesMatching = (pattern: RegExp): string[] => pageSources(KANBAN).filter(path => pattern.test(readFileSync(path, 'utf-8'))).map(path => relative(KANBAN, path))

function boardServer(): Express {
  const projects = new ProjectConnections(new CddConnection(APP_FOLDER))
  return createApp(projects, 0, join(APP_FOLDER, 'dist'), new BoardUpdate(APP_FOLDER))
}

const stackOf = (app: Express): Layer[] => (app as unknown as { _router: { stack: Layer[] } })._router.stack

describe('Refactor Kanban Board To Web Domain Access', () => {
  describe('Every board call reaches the domain through its generated adapter', () => {
    it('should name no domain route in the page, which reaches each through its generated client', () => {
      expect(sourcesMatching(DOMAIN_ROUTE)).toEqual([])
    })

    it('should post to no path the page spells out itself', () => {
      expect(sourcesMatching(HAND_WRITTEN_POST)).toEqual([])
    })

    it('should send through fetch in one place only, the api every generated client posts through', () => {
      expect(sourcesMatching(/\bfetch\(/)).toEqual([join('board', 'board-api.ts')])
    })

    it("should mount no route of the server's own under /api but Update and claude/open, which reach no domain tool", () => {
      const own = stackOf(boardServer()).flatMap(layer => (layer.route?.path.startsWith(API_ROOT) ? [layer.route.path] : []))
      expect(own).toEqual(BOARD_SERVER_PATHS.map(path => `${API_ROOT}${path}`))
    })

    it('should mount the generated routes as one router under /api', () => {
      const routers = stackOf(boardServer()).filter(layer => layer.name === 'router')
      expect(routers.map(router => router.handle.stack?.every(layer => layer.route !== undefined))).toEqual([true])
    })
  })
})
