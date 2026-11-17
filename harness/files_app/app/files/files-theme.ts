import { loader } from '@monaco-editor/react'
import type { editor } from 'monaco-editor'

// The Files app's look: the dark engineering look by default, the light one when the person turns it off. Kept in this
// browser only, as the Graph app keeps its own; the source view reads it from the page's data-theme.
export type FilesTheme = 'engineering' | 'light'

// Where a failure to read, keep or show the look goes: the page's fail, which shows it and sends it to the opening chat.
export type ThemeFailure = (failure: string) => void

const STORED_THEME = 'files-theme'
const STORED_WRAP = 'files-wrap-lines'

// The abd.works brand's accent, the bundled brand's (harness/catalog_generator/templates/commons/site.css): the
// cursor and the current line number, beside the orange line a selected node's lines carry (files.css).
export const ABD_WORKS_ORANGE = '#E5531A'

// One of Cursor's default looks as the source view draws code, with Cursor's own values (Cursor's theme-cursor
// extension, themes/cursor-dark-color-theme.json and cursor-light-color-theme.json): the page behind the text, the
// text, line numbers, selection, and the colours its comments, keywords, strings, numbers, types and functions take.
// Folded lines take no tint, as in Cursor.
type CursorColours = {
  surface: string
  text: string
  lineNumbers: string
  selection: string
  inactiveSelection: string
  lineHighlight: string
  indentGuide: string
  comments: string
  keywords: string
  strings: string
  numbers: string
  types: string
  functions: string
}

const CURSOR_LIGHT: CursorColours = {
  surface: '#FCFCFC',
  text: '#141414',
  lineNumbers: '#1414145C',
  selection: '#14141414',
  inactiveSelection: '#14141414',
  lineHighlight: '#EAEAEA',
  indentGuide: '#14141414',
  comments: '#14141499',
  keywords: '#A30034',
  strings: '#7565CC',
  numbers: '#92156A',
  types: '#005293',
  functions: '#CD4500',
}
const CURSOR_DARK: CursorColours = {
  surface: '#181818',
  text: '#F0F0F0',
  lineNumbers: '#F0F0F05C',
  selection: '#40404099',
  inactiveSelection: '#40404077',
  lineHighlight: '#262626',
  indentGuide: '#F0F0F013',
  comments: '#F0F0F099',
  keywords: '#82D2CE',
  strings: '#E394DC',
  numbers: '#EBC88D',
  types: '#EFB080',
  functions: '#EFB080',
}
// No tint behind a folded line.
const UNTINTED = '#00000000'

const hexOf = (colour: string) => colour.slice(1)

function cursorLook(base: 'vs' | 'vs-dark', colours: CursorColours): editor.IStandaloneThemeData {
  return {
    base,
    inherit: true,
    rules: [
      { token: 'comment', foreground: hexOf(colours.comments), fontStyle: 'italic' },
      { token: 'keyword', foreground: hexOf(colours.keywords) },
      { token: 'string', foreground: hexOf(colours.strings) },
      { token: 'number', foreground: hexOf(colours.numbers) },
      { token: 'type', foreground: hexOf(colours.types) },
      { token: 'function', foreground: hexOf(colours.functions) },
    ],
    colors: {
      'editor.background': colours.surface,
      'editor.foreground': colours.text,
      'editorGutter.background': colours.surface,
      'editorLineNumber.foreground': colours.lineNumbers,
      'editorLineNumber.activeForeground': ABD_WORKS_ORANGE,
      'editorCursor.foreground': ABD_WORKS_ORANGE,
      'editor.selectionBackground': colours.selection,
      'editor.inactiveSelectionBackground': colours.inactiveSelection,
      'editor.lineHighlightBackground': colours.lineHighlight,
      'editor.foldBackground': UNTINTED,
      'editorIndentGuide.background1': colours.indentGuide,
    },
  }
}

// Gives the source view Cursor's default looks. The source view names Monaco's own looks, vs and vs-dark, so Cursor
// Light and Cursor Dark take those names in the Monaco this page loads, which Monaco allows for its built-in looks.
export function wearCursorLooks(monacoApi: { editor: Pick<typeof editor, 'defineTheme'> }): void {
  monacoApi.editor.defineTheme('vs', cursorLook('vs', CURSOR_LIGHT))
  monacoApi.editor.defineTheme('vs-dark', cursorLook('vs-dark', CURSOR_DARK))
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
      wearCursorLooks(monaco)
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
