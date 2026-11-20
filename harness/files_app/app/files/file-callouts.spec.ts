// Which callouts a file view shows, as story_tests/review-generated-work-in-file-viewer/review-files-in-files-app/
// review_files_in_files_app_story.test.md writes it (View File In Source View, Show the callouts the file view's filters
// select): those the session answers for the file, narrowed by the practices chosen and the graph's connectors.
import { describe, expect, it } from 'vitest'

import type { NodeSourceData } from '@cdd/harness/graph/graph'
import type { FileEntryData, SessionClientGenerated, SessionFileData } from '@cdd/space/session/session'

import { FileCallouts } from './file-callouts'
import { FilesStore, NO_GRAPH } from './files-state'

const SCENARIOS = 'story_tests/fill-cart/add_book_to_cart_story.test.md'
const MODEL = '.context/domain-model.md'
const EXAMPLES = 'catalogue/book_examples.py'
const BOOK_CODE = 'catalogue/book.py'

const entry = (path: string, fidelities: string[]): FileEntryData => ({ path, exists: true, is_changed: false, link: '', format: '', fidelities })
const ROOT_FILES = [entry(SCENARIOS, ['stories-scenarios']), entry(MODEL, ['ddd-model']), entry(BOOK_CODE, ['clean-engineering-code']), entry('notes/plain.md', [])]
const node = (node_id: string, name: string, file: string): NodeSourceData => ({ node_id, name, type: 'Operation', owner: '', file, start_line: 1, end_line: 1, text: name, members: [] }) as NodeSourceData
const section = (line: number, title: string, path: string, more: object = {}) => ({ line, title, link: path, section: { path, start_line: 1, end_line: 2, content: title, anchor: '' }, missing: '', ...more })

// The scenario file as session.file answers it: its Given links the domain model and a plain note, a link names a
// heading the model does not have, and its step observes an example and invokes Book.reprice.
const scenarios = {
  path: SCENARIOS,
  text: '',
  language: 'markdown',
  comments: [],
  changes: [],
  folds: [],
  violations: [],
  callouts: [section(3, 'Book', MODEL), section(3, 'note', 'notes/plain.md'), section(4, 'Cart Line', MODEL, { missing: `${MODEL} has no heading #cartline-entity` })],
  steps: [{ line: 5, invokes: [node('reprice', 'reprice', BOOK_CODE)], observes: [node('tiny-tales', 'Tiny Tales', EXAMPLES)] }],
} as unknown as SessionFileData

// The callouts shown with entries, the files the stages, practices and formats select, and the connectors chosen.
function shown(entries: FileEntryData[], relationships: string[] = [], rootFiles: FileEntryData[] | null = ROOT_FILES): string[] {
  const store = new FilesStore()
  store.change(() => ({ rootFiles, entries, graph: { ...NO_GRAPH, filter: { ...NO_GRAPH.filter, relationships } } }))
  const callouts = new FileCallouts(store, {} as SessionClientGenerated)
  return callouts.shownOf(scenarios).map(callout => callout.title)
}

describe('File Callouts', () => {
  describe('with every practice chosen and no connector filtered', () => {
    it("should show each link's callout, the missing one too, and what the step invokes and observes", () => {
      expect(shown(ROOT_FILES)).toEqual(['Book', 'note', 'Cart Line', 'reprice', 'Tiny Tales'])
    })
  })

  describe('with DDD turned off, so the bar lists no file of the domain model', () => {
    it('should leave out the callouts into the domain model, the missing one too, and keep the rest', () => {
      expect(shown(ROOT_FILES.filter(listed => listed.path !== MODEL))).toEqual(['note', 'reprice', 'Tiny Tales'])
    })

    it('should keep a callout into a file no practice declares, such as a note', () => {
      expect(shown([])).toContain('note')
    })
  })

  describe("with the graph's node filter leaving out a connector", () => {
    it('should leave out what a step invokes while invokes is not chosen', () => {
      expect(shown(ROOT_FILES, ['observes'])).toEqual(['Book', 'note', 'Cart Line', 'Tiny Tales'])
    })

    it('should leave out what a step observes while observes is not chosen', () => {
      expect(shown(ROOT_FILES, ['invokes'])).toEqual(['Book', 'note', 'Cart Line', 'reprice'])
    })
  })

  describe("with the session's files not read yet", () => {
    it('should show every callout the session answers', () => {
      expect(shown([], [], null)).toEqual(['Book', 'note', 'Cart Line', 'reprice', 'Tiny Tales'])
    })
  })
})
