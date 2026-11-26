// Open Linked Sections In Place, on a rendered page, as story_tests/review-generated-work-in-file-viewer/
// review-files-in-files-app/review_files_in_files_app_story.test.md writes it (View File In Source View, the rendered
// view's callouts and links). The session answers each file's callouts; the page draws them and opens them in place.
import { describe, expect, it } from 'vitest'

import { linkCalloutAt, type SourceCallout } from '@source-view/source-callouts'

import { markdownPage } from './markdown-page'
import { FILE_PATH, RenderedCallouts, fileLinked, type RenderedReads } from './rendered-callouts'

const STORY_MAP = '.context/story-map.md'
const SCENARIOS = 'story_tests/fill-cart/add_book_to_cart_story.test.md'
const MODEL = '.context/domain-model.md'
const STORY_MAP_TEXT = '# Story Map\n\n### (S) Customer --> [Add Book To Cart](../story_tests/fill-cart/add_book_to_cart_story.test.md)\n'
const SCENARIOS_TEXT = '## Story: Add Book To Cart\n\n*Given* the Bookshop sells ++[Book](../../.context/domain-model.md#book)++\n*When* the Customer adds it\n'

const callout = (given: Partial<SourceCallout>): SourceCallout => ({ id: 'id', kind: 'section', line: 1, title: '', path: '', startLine: 1, endLine: 1, text: '', ...given })
const ADD_BOOK = callout({ id: `${SCENARIOS}:1`, line: 3, title: 'Add Book To Cart', link: '../story_tests/fill-cart/add_book_to_cart_story.test.md', path: SCENARIOS, endLine: 4, text: SCENARIOS_TEXT.trimEnd() })
const BOOK = callout({ id: `${MODEL}:5`, line: 3, title: 'Book', link: '../../.context/domain-model.md#book', path: MODEL, startLine: 5, endLine: 6, text: '#### Book <<Entity>>\n+ reprice(amount: Money): void' })
const TINY_TALES = callout({ id: 'tiny-tales', kind: 'example', line: 3, title: 'Tiny Tales', path: 'catalogue/book_examples.py', startLine: 8, endLine: 9, text: 'TINY_TALES = Book("Tiny Tales")\nTINY_TALES.reprice(5)' })
const REPRICE = callout({ id: 'reprice', kind: 'call', line: 9, title: 'Book.reprice', path: 'catalogue/book.py', startLine: 20, endLine: 21, text: '    def reprice(self, amount):\n        self.price = amount' })
const GONE = callout({ id: 'gone', kind: 'missing', line: 3, title: 'Cart Line', link: '../domain-model.md#cartline-entity', path: MODEL, startLine: 0, endLine: 0, text: `${MODEL} has no heading #cartline-entity` })

// A rendered page of text at path with shown, its callouts, as the file view draws it; what Go to file was asked for.
function drawn(path: string, text: string, shown: SourceCallout[], reads: Partial<RenderedReads> = {}) {
  const went: SourceCallout[] = []
  const page = document.createElement('div')
  page.setAttribute(FILE_PATH, path)
  page.innerHTML = markdownPage(text, [...new Set(shown.map(each => each.line))])
  document.body.replaceChildren(page)
  const rendered = new RenderedCallouts({ calloutsIn: async () => [], within: () => [], goTo: followed => went.push(followed), ...reads })
  rendered.mark(page, shown)
  return { page, rendered, went }
}

const marks = (within: Element): HTMLElement[] => [...within.querySelectorAll<HTMLElement>('.rendered-callout-mark')]
const settled = () => new Promise(resolve => setTimeout(resolve, 0))

describe('Rendered Callouts', () => {
  describe("with the story map rendered, its story Add Book To Cart linked to its scenario file", () => {
    it('should end the story\'s line in a mark naming Add Book To Cart', () => {
      const { page } = drawn(STORY_MAP, STORY_MAP_TEXT, [ADD_BOOK])
      expect(marks(page).map(mark => [mark.textContent, mark.closest('h3') !== null])).toEqual([['Add Book To Cart', true]])
    })

    it('should show no scenario until the mark is pressed', () => {
      const { page } = drawn(STORY_MAP, STORY_MAP_TEXT, [ADD_BOOK])
      expect(page.querySelector('.callout-section')).toBeNull()
    })

    describe('that has the mark pressed', () => {
      it('should open the scenario file under the story\'s heading, rendered as a page', () => {
        const { page } = drawn(STORY_MAP, STORY_MAP_TEXT, [ADD_BOOK])
        marks(page)[0]?.click()
        expect([page.querySelector('h3 + .rendered-callout-block .callout-section h2')?.textContent, page.querySelector('.callout-section u a')?.textContent]).toEqual(['Story: Add Book To Cart', 'Book'])
      })

      it('should head it with its file and lines, which a press opens in its own file', () => {
        const { page, went } = drawn(STORY_MAP, STORY_MAP_TEXT, [ADD_BOOK])
        marks(page)[0]?.click()
        const head = page.querySelector<HTMLElement>('.callout-go-to')
        head?.click()
        expect([head?.textContent, went]).toEqual([`${SCENARIOS} lines 1 to 4`, [ADD_BOOK]])
      })

      it('should close it again on a second press', () => {
        const { page } = drawn(STORY_MAP, STORY_MAP_TEXT, [ADD_BOOK])
        marks(page)[0]?.click()
        marks(page)[0]?.click()
        expect(page.querySelector('.callout-section')).toBeNull()
      })

      it("should mark the scenario's own lines with the callouts its file holds, the domain term Book and the example a step observes", async () => {
        const { page } = drawn(STORY_MAP, STORY_MAP_TEXT, [ADD_BOOK], { calloutsIn: async path => (path === SCENARIOS ? [BOOK, TINY_TALES] : []) })
        marks(page)[0]?.click()
        await settled()
        expect(marks(page.querySelector('.callout-section')!).map(mark => mark.textContent)).toEqual(['Book, Tiny Tales'])
      })

      it('should open, from the scenario in place, the class Book and the example, and from the example the operation it calls', async () => {
        const { page } = drawn(STORY_MAP, STORY_MAP_TEXT, [ADD_BOOK], { calloutsIn: async path => (path === SCENARIOS ? [BOOK, TINY_TALES] : []), within: inside => (inside.id === TINY_TALES.id ? [REPRICE] : []) })
        marks(page)[0]?.click()
        await settled()
        marks(page.querySelector('.callout-section')!)[0]?.click()
        const example = page.querySelector('.callout-section .callout-example')!
        marks(example)[0]?.click()
        expect([page.querySelector('.callout-section .callout-section h4')?.textContent, example.querySelector('.callout-call .callout-text')?.textContent]).toEqual(['Book <<Entity>>', '    def reprice(self, amount):'])
      })

      it("should say so inside the scenario when the session does not answer its file's callouts", async () => {
        const { page } = drawn(STORY_MAP, STORY_MAP_TEXT, [ADD_BOOK], { calloutsIn: async () => Promise.reject(new Error('session.file answered no file')) })
        marks(page)[0]?.click()
        await settled()
        expect(page.querySelector('.callout-section .callout-unread')?.textContent).toEqual(`The callouts of ${SCENARIOS} did not read: session.file answered no file`)
      })

      it('should not open the story map again inside its own scenario', async () => {
        const back = callout({ id: ADD_BOOK.id, line: 1, title: 'again', path: SCENARIOS })
        const { page } = drawn(STORY_MAP, STORY_MAP_TEXT, [ADD_BOOK], { calloutsIn: async () => [back] })
        marks(page)[0]?.click()
        await settled()
        expect(marks(page.querySelector('.callout-section')!)).toEqual([])
      })
    })

    describe('that has the link Add Book To Cart pressed', () => {
      it('should open the scenario file at the lines its callout holds', () => {
        const { page, rendered, went } = drawn(STORY_MAP, STORY_MAP_TEXT, [ADD_BOOK])
        const isLink = rendered.follow(page.querySelector('h3 a')!)
        expect([isLink, went]).toEqual([true, [ADD_BOOK]])
      })
    })
  })

  describe('with a page whose link has no callout, such as one a practice turned off leaves out', () => {
    it('should open the file the link names, read from the folder of the page', () => {
      const { page, rendered, went } = drawn(STORY_MAP, STORY_MAP_TEXT, [])
      rendered.follow(page.querySelector('h3 a')!)
      expect(went.map(followed => [followed.kind, followed.path, followed.startLine])).toEqual([['section', SCENARIOS, 1]])
    })

    it('should name a file from the linking file\'s folder', () => {
      expect([fileLinked(SCENARIOS, '../../.context/domain-model.md#book'), fileLinked(MODEL, 'story-map.md'), fileLinked('README.md', './docs/setup.md')]).toEqual([MODEL, '.context/story-map.md', 'docs/setup.md'])
    })

    it('should follow nothing for text that is no link', () => {
      const { page, rendered, went } = drawn(STORY_MAP, STORY_MAP_TEXT, [])
      expect([rendered.follow(page.querySelector('h1')!), went]).toEqual([false, []])
    })
  })

  describe('with a link to a heading that is not there', () => {
    const text = '- ++[Cart Line](../domain-model.md#cartline-entity)++ - one Book in the Cart\n'

    it('should mark the line as missing and, opened, say what is not there', () => {
      const { page } = drawn(SCENARIOS, `\n\n${text}`, [GONE])
      const mark = marks(page)[0]
      mark?.click()
      expect([mark?.classList.contains('callout-missing'), page.querySelector('.callout-section.callout-missing')?.textContent]).toEqual([true, `${MODEL} has no heading #cartline-entity`])
    })

    it('should open no file when the link is pressed', () => {
      const { page, rendered, went } = drawn(SCENARIOS, `\n\n${text}`, [GONE])
      rendered.follow(page.querySelector('a')!)
      expect(went).toEqual([])
    })
  })
})

describe('Follow A Link In The Source View', () => {
  const line = '*Given* the Bookshop sells ++[Book](../../.context/domain-model.md#book)++ ++Tiny Tales++'

  it('should find the callout of the link the pointer is on', () => {
    expect(linkCalloutAt([BOOK, TINY_TALES], line, line.indexOf('Book]') + 2)).toBe(BOOK)
  })

  it('should find none beside the link, or for a link to something not there', () => {
    expect([linkCalloutAt([BOOK], line, 3), linkCalloutAt([GONE], '[Cart Line](../domain-model.md#cartline-entity)', 4)]).toEqual([undefined, undefined])
  })
})
