import { loader } from '@monaco-editor/react'

// The Files app's look: the dark engineering look by default, the light one when the person turns it off. Kept in this
// browser only, as the Graph app keeps its own; the source view reads it from the page's data-theme.
export type FilesTheme = 'engineering' | 'light'

const STORED_THEME = 'files-theme'

export function storedTheme(): FilesTheme {
  try {
    return window.localStorage.getItem(STORED_THEME) === 'light' ? 'light' : 'engineering'
  } catch {
    return 'engineering'
  }
}

// Sets the page's look, and the source view's editor with it, which reads the theme only as it opens a file.
export function applyTheme(theme: FilesTheme): void {
  if (theme === 'engineering') document.documentElement.dataset.theme = 'engineering'
  else delete document.documentElement.dataset.theme
  try {
    window.localStorage.setItem(STORED_THEME, theme)
  } catch {
    // A browser that keeps nothing still shows the look chosen until the page reloads.
  }
  void loader.init().then(monaco => monaco.editor.setTheme(theme === 'engineering' ? 'vs-dark' : 'vs'))
}
