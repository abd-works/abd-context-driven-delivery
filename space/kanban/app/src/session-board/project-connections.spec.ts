import type { Request } from 'express'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

import { ProjectConnections, type CddConnection } from '@cdd/cdd-connection'
import { PROJECT_HEADER } from '@cdd/cdd-shared'


// A connection that says which folder it was made for and whether it was closed.
type Recorded = CddConnection & { folder: string; isClosed: boolean }
const recorded = (folder: string): Recorded => ({ folder, isClosed: false, close: async function (this: Recorded) { this.isClosed = true } }) as unknown as Recorded

const requestNaming = (project?: string): Request => ({ get: (name: string) => (name === PROJECT_HEADER ? project : undefined) }) as unknown as Request

// One board server serves every repository, so /board from any chat shows that chat's own tickets.
describe('Serve Each Repository Its Own Board', () => {
  const started = recorded('started')
  const made: Recorded[] = []
  const projects = () => new ProjectConnections(started, folder => { const connection = recorded(folder); made.push(connection); return connection })

  describe('with a call that names no project', () => {
    it('should run on the project the server was started with', () => {
      expect(projects().of(requestNaming())).toBe(started)
    })
  })

  describe('with calls that name a repository', () => {
    it('should run on a connection made for that repository', () => {
      const connection = projects().of(requestNaming('C:/dev/sandbox')) as Recorded
      expect(connection.folder).toBe(resolve('C:/dev/sandbox'))
    })

    it('should keep one connection for each repository', () => {
      const shared = projects()
      expect(shared.of(requestNaming('C:/dev/sandbox'))).toBe(shared.of(requestNaming('C:/dev/sandbox')))
      expect(shared.of(requestNaming('C:/dev/sandbox'))).not.toBe(shared.of(requestNaming('C:/dev/other')))
    })
  })

  describe('with the server stopping', () => {
    it('should close every connection it made', async () => {
      made.length = 0
      const shared = projects()
      shared.of(requestNaming('C:/dev/sandbox'))
      await shared.close()
      expect([started, ...made].map(connection => connection.isClosed)).toEqual([true, true])
    })
  })
})
