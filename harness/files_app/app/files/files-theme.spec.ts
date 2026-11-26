import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import type { editor } from 'monaco-editor'

import { ABD_WORKS_ORANGE, keepWrap, storedWrap, wearCursorLooks } from './files-theme'

// The Monaco the page loads, keeping each look it is given by name.
class FakeMonaco {
  readonly looks = new Map<string, editor.IStandaloneThemeData>()
  readonly editor = { defineTheme: (name: string, look: editor.IStandaloneThemeData) => void this.looks.set(name, look) }
}

const tokenColour = (look: editor.IStandaloneThemeData | undefined, token: string) => look?.rules.find(rule => rule.token === token)?.foreground

// The source view in Cursor's default looks, Cursor Dark and Cursor Light (Cursor's theme-cursor extension), so code
// reads here as it does in Cursor; the only orange is the line beside a selected node's lines (file-marks.spec.ts).
describe("Source view in Cursor's default looks", () => {
  let monaco: FakeMonaco

  beforeEach(() => {
    monaco = new FakeMonaco()
    wearCursorLooks(monaco)
  })

  describe('with the dark look', () => {
    it("should draw the source in Cursor Dark's colours, #181818 behind #F0F0F0 text", () => {
      const look = monaco.looks.get('vs-dark')
      expect([look?.colors['editor.background'], look?.colors['editor.foreground']]).toEqual(['#181818', '#F0F0F0'])
    })

    it('should draw the cursor and the current line number in abd.works orange', () => {
      const look = monaco.looks.get('vs-dark')
      expect([look?.colors['editorCursor.foreground'], look?.colors['editorLineNumber.activeForeground']]).toEqual([ABD_WORKS_ORANGE, ABD_WORKS_ORANGE])
    })

    it("should draw keywords, strings and numbers in Cursor Dark's token colours", () => {
      const look = monaco.looks.get('vs-dark')
      expect([tokenColour(look, 'keyword'), tokenColour(look, 'string'), tokenColour(look, 'number')]).toEqual(['82D2CE', 'E394DC', 'EBC88D'])
    })

    it("should draw selected text on Cursor Dark's grey and folded lines untinted, no brown band behind the text", () => {
      const look = monaco.looks.get('vs-dark')
      expect([look?.colors['editor.selectionBackground'], look?.colors['editor.foldBackground']]).toEqual(['#40404099', '#00000000'])
    })
  })

  describe('with the light look', () => {
    it("should draw the source in Cursor Light's colours, #FCFCFC behind #141414 text", () => {
      const look = monaco.looks.get('vs')
      expect([look?.colors['editor.background'], look?.colors['editor.foreground']]).toEqual(['#FCFCFC', '#141414'])
    })

    it('should draw the cursor and the current line number in abd.works orange', () => {
      const look = monaco.looks.get('vs')
      expect([look?.colors['editorCursor.foreground'], look?.colors['editorLineNumber.activeForeground']]).toEqual([ABD_WORKS_ORANGE, ABD_WORKS_ORANGE])
    })

    it("should draw keywords, strings and numbers in Cursor Light's token colours", () => {
      const look = monaco.looks.get('vs')
      expect([tokenColour(look, 'keyword'), tokenColour(look, 'string'), tokenColour(look, 'number')]).toEqual(['A30034', '7565CC', '92156A'])
    })

    it("should draw selected text on Cursor Light's grey and folded lines untinted", () => {
      const look = monaco.looks.get('vs')
      expect([look?.colors['editor.selectionBackground'], look?.colors['editor.foldBackground']]).toEqual(['#14141414', '#00000000'])
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
