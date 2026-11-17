// How a code file opens with no node selected: its classes open and their members folded, so the file reads as an
// outline of its classes, as the person asked on 2026-11-16. A member is a line directly inside a class whose body
// folds under it, its next written line indented deeper, as Monaco folds it.

const PYTHON = 'python'
const SCRIPTS = new Set(['typescript', 'javascript', 'typescriptreact', 'javascriptreact'])

const PYTHON_CLASS = /^\s*class\s+\w/
const PYTHON_MEMBER = /^\s*(async\s+)?def\s/
const SCRIPT_CLASS = /^\s*(export\s+)?(default\s+)?(abstract\s+)?class\s+[\w$]/
// A comment or decorator line inside a class, which opens no member of its own.
const SCRIPT_NOT_MEMBER = /^\s*(\/\/|\/\*|\*|@|\})/

type Grammar = { isClass: RegExp; isMember: (line: string) => boolean }

const GRAMMARS: Record<string, Grammar> = {
  python: { isClass: PYTHON_CLASS, isMember: line => PYTHON_MEMBER.test(line) },
  script: { isClass: SCRIPT_CLASS, isMember: line => !SCRIPT_NOT_MEMBER.test(line) && !SCRIPT_CLASS.test(line) },
}

const grammarOf = (language: string): Grammar | undefined => (language === PYTHON ? GRAMMARS.python : SCRIPTS.has(language) ? GRAMMARS.script : undefined)

const indentOf = (line: string): number => line.length - line.trimStart().length
const isWritten = (line: string): boolean => line.trim().length > 0

// The lines, numbered from 1, of each member of each class in the text: the folds to close as the file opens. Any
// other language, markdown among them, folds nothing.
export function memberLines(text: string, language: string): number[] {
  const grammar = grammarOf(language)
  if (!grammar) return []
  const lines = text.split('\n')
  const classes: { indent: number; memberIndent: number }[] = []
  const members: number[] = []
  lines.forEach((line, index) => {
    if (!isWritten(line)) return
    const indent = indentOf(line)
    while (classes.length && indent <= classes[classes.length - 1].indent) classes.pop()
    const inside = classes[classes.length - 1]
    if (inside && inside.memberIndent < 0) inside.memberIndent = indent
    if (inside && indent === inside.memberIndent && grammar.isMember(line) && opensFold(lines, index)) members.push(index + 1)
    if (grammar.isClass.test(line)) classes.push({ indent, memberIndent: -1 })
  })
  return members
}

// Whether the line at index heads a fold: the next written line sits deeper.
function opensFold(lines: string[], index: number): boolean {
  const next = lines.slice(index + 1).find(isWritten)
  return next !== undefined && indentOf(next) > indentOf(lines[index])
}
