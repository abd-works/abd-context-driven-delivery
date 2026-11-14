import type { NodeSourceData } from '@cdd/harness/graph/graph'
import type { FileViolationData, SessionFileData } from '@cdd/space/session/session'
import type { SourceFold, SourceRule } from '@source-view/SourceView'
import type { ViolationFocus } from '@source-view/violation-prompt'

// The node type the source view is handed for a whole file, which it opens with every fold open.
const FILE_NODE = 'File'
const VIOLATING = 'violating'

const fileNameOf = (path: string): string => path.split('/').at(-1) ?? path

// How the graph explorer's source view reads a session's file: the whole file as one source, from its first line, with
// no members, so each line the editor shows is that line of the file.
export function sourceOf(file: SessionFileData): NodeSourceData {
  const lines = file.text.split('\n').length
  return { node_id: file.path, name: fileNameOf(file.path), type: FILE_NODE, owner: '', file: file.path, text: file.text, start_line: 1, end_line: lines, members: [] }
}

// The folds the session's graph places in the file: a class whole, each operation and property as a block.
export function foldsOf(file: SessionFileData): SourceFold[] {
  return file.folds.map(fold => ({ start: fold.range.start_line, end: fold.range.end_line, kind: fold.kind }))
}

// Each rule broken in the file once, with every message it gives there.
export function rulesOf(file: SessionFileData): SourceRule[] {
  const names = [...new Set(file.violations.map(found => found.violation.rule))]
  return names.map(name => ({ name, status: VIOLATING, messages: file.violations.filter(found => found.violation.rule === name).map(found => found.violation.message) }))
}

// The first place the chosen rule is broken, which the source view marks and offers a Correct prompt for.
export function violationFocusOf(file: SessionFileData, rule: string): ViolationFocus | null {
  const found: FileViolationData | undefined = file.violations.find(each => each.violation.rule === rule)
  if (!found) return null
  return { rule: found.violation.rule, message: found.violation.message, startLine: found.range.start_line, endLine: found.range.end_line }
}

// The language Monaco colours the file as, from the session's answer.
export function monacoLanguageOf(file: SessionFileData): string {
  return file.language || 'plaintext'
}
