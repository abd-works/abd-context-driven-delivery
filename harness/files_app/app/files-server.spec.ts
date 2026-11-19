// Which project a request to the Files server is about, as the story Open Files In Files App asks of a page opened on
// another project (review_files_in_files_app_story.test.md): the folder its header names, refused when it is not there.
import { describe, expect, it } from 'vitest'
import { tmpdir } from 'node:os'
import { join } from 'node:path'

import { CddConnection, ProjectConnections } from '@cdd/cdd-connection'
import { PROJECT_HEADER } from '@cdd/cdd-shared'

import { ProjectFolderMissingError, connectionOf } from './files-server'

// Seed: a folder that is there, and one that is not, such as a ticket's worktree removed while its Files tab stays open.
const THERE = tmpdir()
const GONE = join(tmpdir(), 'cdd-files-project-removed')

const started = new CddConnection(THERE)
const naming = (project: string) => ({ get: (name: string) => (name === PROJECT_HEADER ? project : undefined) })

describe('a request to the Files server', () => {
  describe('that names a project folder that is there', () => {
    it("should be answered through that project's own connection", () => {
      expect(connectionOf(new ProjectConnections(started), naming(THERE))).not.toBe(started)
    })
  })

  describe('that names no project', () => {
    it('should be answered through the connection the server started with', () => {
      expect(connectionOf(new ProjectConnections(started), naming(''))).toBe(started)
    })
  })

  describe('that names a project folder that is not there', () => {
    it('should be refused, naming the folder as not there', () => {
      expect(() => connectionOf(new ProjectConnections(started), naming(GONE))).toThrow(new ProjectFolderMissingError(GONE))
    })

    it('should say so in words a person reads', () => {
      expect(new ProjectFolderMissingError(GONE).message).toBe(`The project folder ${GONE} is not there: it was moved or removed, such as a ticket's worktree closed since this page opened.`)
    })
  })
})
