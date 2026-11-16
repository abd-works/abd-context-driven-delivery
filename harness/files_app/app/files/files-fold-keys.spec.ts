// Fold With Keyboard Shortcuts, as story_tests/review-generated-work-in-file-viewer/review-files-in-files-app/
// review_files_in_files_app_story.test.md writes it. Only the page binds keys: the session only reads the project's
// keybindings file, as it reads any file.
import { beforeEach, describe, expect, it } from 'vitest'

import type { Monaco } from '@monaco-editor/react'
import type { CddApi } from '@cdd/cdd-shared'
import type { FileTextData, SessionClientGenerated } from '@cdd/space/session/session'

import { FilesFoldKeys, KEYBINDINGS_FILE } from './files-fold-keys'
import { FilesNotices } from './files-notices'
import { FilesStore } from './files-state'

const CTRL = 2048
const KEY_K = 41
const KEY_M = 43
const DIGIT_0 = 21
const chord = (first: number, second: number) => first * 65536 + second

// The Monaco a source view loads, keeping the rules it is given; its key codes are plain numbers.
class FakeMonaco {
  readonly rules: { keybinding: number; command: string }[] = []
  readonly KeyMod = { CtrlCmd: CTRL, Shift: 1024, Alt: 512, WinCtrl: 256, chord }
  readonly KeyCode = { KeyK: KEY_K, KeyJ: 40, KeyL: 42, KeyM: KEY_M, Digit0: DIGIT_0, Digit1: 22, Digit2: 23, Digit3: 24, Digit4: 25, Digit5: 26, Digit6: 27, Digit7: 28, BracketLeft: 92, BracketRight: 94 }
  readonly editor = { addKeybindingRules: (rules: { keybinding: number; command: string }[]) => this.rules.push(...rules) }
}

// The session reading the project's files: the keybindings file reads as written, or as no text when it is not there.
const sessionReading = (written: string): Pick<SessionClientGenerated, 'readFile'> => ({
  readFile: async (path?: string) => ({ path: path ?? '', text: path === KEYBINDINGS_FILE ? written : '', language: 'json' }) as FileTextData,
})

const noChat: CddApi = { post: async () => null }

describe('Files Fold Keys', () => {
  let store: FilesStore
  let monaco: FakeMonaco

  beforeEach(() => {
    store = new FilesStore()
    monaco = new FakeMonaco()
  })

  const keysReading = async (written: string) => {
    const keys = new FilesFoldKeys(sessionReading(written), new FilesNotices(store, noChat, ''))
    keys.bindIn(monaco as unknown as Monaco)
    await keys.read()
    return monaco.rules.filter(rule => rule.command === 'editor.toggleFold' || rule.command === 'editor.foldAll').slice(-2)
  }

  describe('with no keybindings file in the project', () => {
    it("should bind VS Code's Ctrl+K Ctrl+0 to fold all, telling the Person nothing", async () => {
      const bound = await keysReading('')
      expect([bound.find(rule => rule.command === 'editor.foldAll')?.keybinding, store.state.toasts]).toEqual([chord(CTRL | KEY_K, CTRL | DIGIT_0), []])
    })
  })

  describe('with a keybindings file giving Ctrl+M Ctrl+M to toggle a fold', () => {
    it('should bind Ctrl+M Ctrl+M to toggle a fold once the file is read', async () => {
      const bound = await keysReading('[{ "key": "ctrl+m ctrl+m", "command": "editor.toggleFold" }]')
      expect(bound.find(rule => rule.command === 'editor.toggleFold')?.keybinding).toBe(chord(CTRL | KEY_M, CTRL | KEY_M))
    })
  })

  describe('with a keybindings file that is not a list of fold commands', () => {
    it("should keep VS Code's keys and say on the page that the file is not used, and why", async () => {
      await keysReading('{ "editor.foldAll": "ctrl+m" }')
      expect(store.state.toasts).toEqual([`${KEYBINDINGS_FILE} is not used, VS Code's fold keys are: it is not a list of { "key", "command" }`])
    })
  })
})
