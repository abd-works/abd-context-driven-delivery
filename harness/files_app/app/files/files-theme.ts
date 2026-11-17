import { loader } from '@monaco-editor/react'
import type { editor } from 'monaco-editor'

// The Files app's look: the dark engineering look by default, the light one when the person turns it off. Kept in this
// browser only, as the Graph app keeps its own; the source view reads it from the page's data-theme.
export type FilesTheme = 'engineering' | 'light'

// Where a failure to read, keep or show the look goes: the page's fail, which shows it and sends it to the opening chat.
export type ThemeFailure = (failure: string) => void

const STORED_THEME = 'files-theme'
const STORED_WRAP = 'files-wrap-lines'

// The abd.works brand's accent, the bundled brand's (harness/catalog_generator/templates/commons/site.css).
export const ABD_WORKS_ORANGE = '#E5531A'

// One look of the abd.works brand as the source view draws code: the page behind the text, the text, the quiet
// colours of line numbers and comments, and the colours its strings, numbers and types take beside the orange.
type BrandColours = { surface: string; text: string; muted: string; border: string; strings: string; numbers: string; types: string }

const EXECUTIVE: BrandColours = { surface: '#FFFFFF', text: '#111113', muted: '#595A61', border: '#DDD8CF', strings: '#0B6E99', numbers: '#B45309', types: '#C64514' }
const ENGINEERING: BrandColours = { surface: '#111113', text: '#E8E8ED', muted: '#9B9BA8', border: '#2A2A2A', strings: '#4FC3F7', numbers: '#F59E0B', types: '#F2A07A' }

const hexOf = (colour: string) => colour.slice(1)

function brandLook(base: 'vs' | 'vs-dark', colours: BrandColours): editor.IStandaloneThemeData {
  return {
    base,
    inherit: true,
    rules: [
      { token: 'comment', foreground: hexOf(colours.muted), fontStyle: 'italic' },
      { token: 'keyword', foreground: hexOf(ABD_WORKS_ORANGE) },
      { token: 'string', foreground: hexOf(colours.strings) },
      { token: 'number', foreground: hexOf(colours.numbers) },
      { token: 'type', foreground: hexOf(colours.types) },
    ],
    colors: {
      'editor.background': colours.surface,
      'editor.foreground': colours.text,
      'editorGutter.background': colours.surface,
      'editorLineNumber.foreground': colours.muted,
      'editorLineNumber.activeForeground': ABD_WORKS_ORANGE,
      'editorCursor.foreground': ABD_WORKS_ORANGE,
      'editor.selectionBackground': `${ABD_WORKS_ORANGE}2E`,
      'editor.inactiveSelectionBackground': `${ABD_WORKS_ORANGE}1A`,
      'editor.lineHighlightBorder': colours.border,
      'editor.foldBackground': `${ABD_WORKS_ORANGE}14`,
      'editorIndentGuide.background1': colours.border,
      'editorBracketMatch.border': ABD_WORKS_ORANGE,
    },
  }
}

// Gives the source view the abd.works look. The source view names Monaco's own looks, vs and vs-dark, so the brand's
// light and dark looks take those names in the Monaco this page loads, which Monaco allows for its built-in looks.
export function wearBrand(monacoApi: { editor: Pick<typeof editor, 'defineTheme'> }): void {
  monacoApi.editor.defineTheme('vs', brandLook('vs', EXECUTIVE))
  monacoApi.editor.defineTheme('vs-dark', brandLook('vs-dark', ENGINEERING))
}

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
    .then(monaco => {
      wearBrand(monaco)
      monaco.editor.setTheme(theme === 'engineering' ? 'vs-dark' : 'vs')
    })
    .catch(failure => fail(`The source view did not change its look: ${reasonOf(failure)}`))
}

// Whether the source view wraps long lines, kept in this browser like the look, so the next file opens the same way.
// Unwrapped, the one a person who never chose sees, when the browser's storage refuses to be read.
export function storedWrap(fail: ThemeFailure): boolean {
  try {
    return window.localStorage.getItem(STORED_WRAP) === 'on'
  } catch (failure) {
    fail(`The Files app could not read from this browser's storage whether to wrap long lines: ${reasonOf(failure)}`)
    return false
  }
}

// Keeps whether to wrap long lines; a choice the browser does not keep still holds for the file open now.
export function keepWrap(wrap: boolean, fail: ThemeFailure): void {
  try {
    window.localStorage.setItem(STORED_WRAP, wrap ? 'on' : 'off')
  } catch (failure) {
    fail(`Wrap lines was not kept in this browser, so the next file opens unwrapped: ${reasonOf(failure)}`)
  }
}
