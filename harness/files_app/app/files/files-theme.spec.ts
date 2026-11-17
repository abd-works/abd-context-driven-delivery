import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import type { editor } from 'monaco-editor'

import { ABD_WORKS_ORANGE, keepWrap, storedWrap, wearBrand } from './files-theme'

// The Monaco the page loads, keeping each look it is given by name.
class FakeMonaco {
  readonly looks = new Map<string, editor.IStandaloneThemeData>()
  readonly editor = { defineTheme: (name: string, look: editor.IStandaloneThemeData) => void this.looks.set(name, look) }
}

const tokenColour = (look: editor.IStandaloneThemeData | undefined, token: string) => look?.rules.find(rule => rule.token === token)?.foreground

// The source view in the abd.works look: the brand's executive light look and its engineering dark look, orange its
// accent in both (harness/catalog_generator/templates/commons/site.css).
describe('Source view in the abd.works look', () => {
  let monaco: FakeMonaco

  beforeEach(() => {
    monaco = new FakeMonaco()
    wearBrand(monaco)
  })

  describe('with the dark engineering look', () => {
    it("should draw the source in abd.works' engineering colours, near-black behind light text", () => {
      const look = monaco.looks.get('vs-dark')
      expect([look?.colors['editor.background'], look?.colors['editor.foreground']]).toEqual(['#111113', '#E8E8ED'])
    })

    it('should draw keywords, the cursor and the current line number in abd.works orange', () => {
      const look = monaco.looks.get('vs-dark')
      expect([tokenColour(look, 'keyword'), look?.colors['editorCursor.foreground'], look?.colors['editorLineNumber.activeForeground']]).toEqual([ABD_WORKS_ORANGE.slice(1), ABD_WORKS_ORANGE, ABD_WORKS_ORANGE])
    })
  })

  describe('with the light look', () => {
    it("should draw the source in abd.works' executive colours, white behind near-black text", () => {
      const look = monaco.looks.get('vs')
      expect([look?.colors['editor.background'], look?.colors['editor.foreground']]).toEqual(['#FFFFFF', '#111113'])
    })

    it('should draw keywords, the cursor and the current line number in abd.works orange', () => {
      const look = monaco.looks.get('vs')
      expect([tokenColour(look, 'keyword'), look?.colors['editorCursor.foreground'], look?.colors['editorLineNumber.activeForeground']]).toEqual([ABD_WORKS_ORANGE.slice(1), ABD_WORKS_ORANGE, ABD_WORKS_ORANGE])
    })
  })
})

// Wrap lines: whether the source view wraps long lines, kept in this browser so the next file opens the same way.
describe('Wrap long lines in the source view', () => {
  beforeEach(() => window.localStorage.clear())
  afterEach(() => vi.restoreAllMocks())

  it('should leave long lines unwrapped for a Person who never chose', () => {
    expect(storedWrap(() => undefined)).toBe(false)
  })

  describe('with Wrap lines turned on', () => {
    beforeEach(() => keepWrap(true, () => undefined))

    it('should keep Wrap lines on for the next file the Person opens', () => {
      expect(storedWrap(() => undefined)).toBe(true)
    })

    it('should unwrap the next file once the Person turns Wrap lines off', () => {
      keepWrap(false, () => undefined)
      expect(storedWrap(() => undefined)).toBe(false)
    })
  })

  describe('that the browser refuses to keep', () => {
    beforeEach(() => {
      vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => {
        throw new DOMException('storage is full', 'QuotaExceededError')
      })
    })

    it('should tell the page the next file opens unwrapped, and why', () => {
      const failures: string[] = []
      keepWrap(true, failure => failures.push(failure))
      expect(failures).toEqual(['Wrap lines was not kept in this browser, so the next file opens unwrapped: QuotaExceededError: storage is full'])
    })
  })

  describe('that the browser refuses to read', () => {
    beforeEach(() => {
      vi.spyOn(Storage.prototype, 'getItem').mockImplementation(() => {
        throw new DOMException('storage is blocked', 'SecurityError')
      })
    })

    it('should tell the page it could not read the choice, and leave long lines unwrapped', () => {
      const failures: string[] = []
      const wrap = storedWrap(failure => failures.push(failure))
      expect([wrap, failures]).toEqual([false, ["The Files app could not read from this browser's storage whether to wrap long lines: SecurityError: storage is blocked"]])
    })
  })
})
