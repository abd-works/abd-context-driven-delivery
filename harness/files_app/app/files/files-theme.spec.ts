import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'

import { keepWrap, storedWrap } from './files-theme'

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
