// Collapse Open Files, as story_tests/review-generated-work-in-file-viewer/switch-files-app-between-files-and-graph/
// switch_files_app_between_files_and_graph_story.test.md writes it (Open Several Files From Graph Nodes). Only the page
// shows it: the session answers the same files whether they show whole or collapsed.
import { beforeEach, describe, expect, it } from 'vitest'

import type { SessionFileData } from '@cdd/space/session/session'

import { FilesStore } from './files-state'
import { OpenFiles } from './open-files'

const TICKET = 'space/kanban/ticket.py'
const BOARD = 'space/kanban/board.py'
const STORY_MAP = '.context/story-map.md'

const opened = (path: string) => ({ path }) as SessionFileData

describe('Open Files', () => {
  let store: FilesStore
  let files: OpenFiles

  beforeEach(() => {
    store = new FilesStore()
    store.change(() => ({ openPath: TICKET, moreFiles: [opened(BOARD), opened(STORY_MAP)] }))
    files = new OpenFiles(store)
  })

  describe('with ticket.py open and board.py and story-map.md below it', () => {
    it('should show every open file whole', () => {
      expect(files.paths.map(path => files.isCollapsed(path))).toEqual([false, false, false])
    })

    describe('that the Person collapses board.py', () => {
      beforeEach(() => files.toggle(BOARD))

      it('should collapse board.py alone to its name', () => {
        expect(files.paths.map(path => files.isCollapsed(path))).toEqual([false, true, false])
      })

      it('should show board.py whole again once the Person expands it', () => {
        files.toggle(BOARD)
        expect(files.isCollapsed(BOARD)).toBe(false)
      })
    })

    describe('that the Person collapses all', () => {
      beforeEach(() => files.collapseAll())

      it('should collapse every open file to its name', () => {
        expect(files.paths.map(path => files.isCollapsed(path))).toEqual([true, true, true])
      })

      it('should show every open file whole once the Person expands all', () => {
        files.expandAll()
        expect(files.paths.map(path => files.isCollapsed(path))).toEqual([false, false, false])
      })
    })
  })
})
