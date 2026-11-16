import { loader } from '@monaco-editor/react'

// The Files app's look: the dark engineering look by default, the light one when the person turns it off. Kept in this
// browser only, as the Graph app keeps its own; the source view reads it from the page's data-theme.
export type FilesTheme = 'engineering' | 'light'

// Where a failure to read, keep or show the look goes: the page's fail, which shows it and sends it to the opening chat.
export type ThemeFailure = (failure: string) => void

const STORED_THEME = 'files-theme'

const reasonOf = (failure: unknown): string => (failure instanceof Error ? failure.message : String(failure))

// The look kept in this browser. A browser whose storage refuses to be read is told to the page's fail, and the page
// shows the dark engineering look, the one a person who never chose sees.
export function storedTheme(fail: ThemeFailure): FilesTheme {
  try {
    return window.localStorage.getItem(STORED_THEME) === 'light' ? 'light' : 'engineering'
  } catch (failure) {
    fail(`The Files app could not read its look from this browser's storage: ${reasonOf(failure)}`)
    return 'engineering'
  }
}

// Sets the page's look, and the source view's editor with it, which reads the theme only as it opens a file. A look the
// browser does not keep still shows until the page reloads, and the failure says why it will not last.
export function applyTheme(theme: FilesTheme, fail: ThemeFailure): void {
  if (theme === 'engineering') document.documentElement.dataset.theme = 'engineering'
  else delete document.documentElement.dataset.theme
  try {
    window.localStorage.setItem(STORED_THEME, theme)
  } catch (failure) {
    fail(`The Files app's look was not kept in this browser, so it shows only until the page reloads: ${reasonOf(failure)}`)
  }
  loader
    .init()
    .then(monaco => monaco.editor.setTheme(theme === 'engineering' ? 'vs-dark' : 'vs'))
    .catch(failure => fail(`The source view did not change its look: ${reasonOf(failure)}`))
}
