// What the page sends with each read of a file so the session decides which callouts it holds, as
// story_tests/review-generated-work-in-file-viewer/review-files-in-files-app/review_files_in_files_app_story.test.md
// writes it (View File In Source View, Show the callouts the file view's filters select). Which callouts the filters
// keep is the session's answer, proved in Python: story_tests/review-generated-work-in-file-viewer/
// switch-files-app-between-files-and-graph/ (Filter Callouts Like The Graph).
import { describe, expect, it } from 'vitest'

import type { FileEntryData, SessionClientGenerated, SessionFileData } from '@cdd/space/session/session'

import { FileCallouts } from './file-callouts'
import { FilesStore, NO_GRAPH } from './files-state'

const SCENARIOS = 'story_tests/fill-cart/add_book_to_cart_story.test.md'
const MODEL = '.context/domain-model.md'

const entry = (path: string, fidelities: string[]): FileEntryData => ({ path, exists: true, is_changed: false, link: '', published_kind: '', published_name: '', format: '', fidelities, is_listed: true, is_session_work: false, hidden_by_formats: [] })
const ROOT_FILES = [entry(SCENARIOS, ['stories-scenarios']), entry(MODEL, ['ddd-model'])]
const section = (line: number, title: string, path: string) => ({ line, title, link: path, section: { path, start_line: 1, end_line: 2, content: title, anchor: '' }, missing: '' })

// The scenario file as the session answers it for the filters sent: its Given links the domain model.
const scenarios = { path: SCENARIOS, text: '', language: 'markdown', comments: [], changes: [], folds: [], violations: [], callouts: [section(3, 'Book', MODEL)], steps: [] } as unknown as SessionFileData

// A session that keeps what each read of a file was sent, and answers the scenario file.
class ReadSession {
  readonly reads: unknown[][] = []

  async file(...sent: unknown[]): Promise<SessionFileData> {
    this.reads.push(sent)
    return scenarios
  }
}

// The page's callouts with entries listed, the session's files read or not, and the connectors chosen in the graph view.
function callouts(entries: FileEntryData[], relationships: string[] = [], rootFiles: FileEntryData[] | null = ROOT_FILES): { callouts: FileCallouts; session: ReadSession; store: FilesStore } {
  const store = new FilesStore()
  store.change(() => ({ rootFiles, entries, graph: { ...NO_GRAPH, filter: { ...NO_GRAPH.filter, relationships } } }))
  const session = new ReadSession()
  return { callouts: new FileCallouts(store, session as unknown as SessionClientGenerated), session, store }
}

describe('File Callouts', () => {
  describe('with the files of both practices listed', () => {
    it('should send the session the files listed and the node filter with the read of a file', async () => {
      const { callouts: page, session } = callouts(ROOT_FILES, ['observes'])
      await page.file(SCENARIOS, true, false)
      expect(session.reads).toEqual([[SCENARIOS, true, false, false, [SCENARIOS, MODEL], { relationships: ['observes'] }]])
    })

    it('should draw the callouts the session answers, keeping none back', async () => {
      const { callouts: page } = callouts(ROOT_FILES)
      expect((await page.in(SCENARIOS)).map(callout => callout.title)).toEqual(['Book'])
    })
  })

  describe('with DDD turned off, so the bar lists no file of the domain model', () => {
    it('should send the session the files still listed', async () => {
      const { callouts: page, session } = callouts([ROOT_FILES[0]!])
      await page.in(SCENARIOS)
      expect(session.reads[0]?.[4]).toEqual([SCENARIOS])
    })

    it('should name another read than the one made with DDD on, so the page reads its open files again', () => {
      const { callouts: page, store } = callouts(ROOT_FILES)
      const before = page.readFor
      store.change(() => ({ entries: [ROOT_FILES[0]!] }))
      expect(page.readFor).not.toBe(before)
    })
  })

  describe("with the graph's node filter leaving out a connector", () => {
    it('should name another read than the one made with every connector, so the page reads its open files again', () => {
      const { callouts: page, store } = callouts(ROOT_FILES)
      const before = page.readFor
      store.change(({ graph }) => ({ graph: { ...graph, filter: { ...graph.filter, relationships: ['invokes'] } } }))
      expect(page.readFor).not.toBe(before)
    })
  })

  describe("with the session's files not read yet", () => {
    it('should send no list of files, so the session answers every callout', async () => {
      const { callouts: page, session } = callouts([], [], null)
      await page.file(SCENARIOS, false, false)
      expect(session.reads[0]?.[4]).toBeNull()
    })
  })
})
