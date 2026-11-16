import type { NodeSourceData } from '@cdd/harness/graph/graph'
import type { FileViolationData, SessionFileData } from '@cdd/space/session/session'
import type { SourceRule } from '@source-view/SourceView'
import type { SourceCallout } from '@source-view/source-callouts'
import type { ViolationFocus } from '@graph-app/graph/graph-selection'

// The node type the source view is handed for a whole file, which it opens with every fold open.
const FILE_NODE = 'File'
const VIOLATING = 'violating'

const fileNameOf = (path: string): string => path.split('/').at(-1) ?? path

// The file session.file answered, as the page draws it: none is no file, a file missing a list it holds, as a cdd server
// lane older than the page answers it (one without callouts, say), holds none of that list, and anything that is not a
// file, such as the text or error a lane answers for a call it cannot run, is that call's failure, so the page shows it
// rather than drawing it as a file.
export function fileAnswered(answer: unknown): SessionFileData | null {
  if (answer === null || answer === undefined) return null
  const file = answer as Record<string, unknown>
  if (typeof answer !== 'object' || typeof file.path !== 'string' || typeof file.text !== 'string') throw new Error(`session.file answered no file: ${saidBy(answer)}`)
  const steps = listOf<Record<string, unknown>>(file.steps).map(step => ({ ...step, invokes: listOf(step.invokes), observes: listOf(step.observes) }))
  return {
    ...(file as SessionFileData),
    language: typeof file.language === 'string' ? file.language : '',
    comments: listOf(file.comments),
    changes: listOf(file.changes),
    folds: listOf(file.folds),
    steps: steps as SessionFileData['steps'],
    callouts: listOf(file.callouts),
    violations: listOf(file.violations),
  }
}

const listOf = <Item>(list: unknown): Item[] => (Array.isArray(list) ? (list as Item[]) : [])

const saidBy = (answer: unknown): string => {
  if (typeof answer === 'string') return answer
  const error = (answer as { error?: unknown } | null)?.error
  return error !== undefined ? String(error) : JSON.stringify(answer)
}

// How the graph explorer's source view reads a session's file: the whole file as one source, from its first line, so
// each line the editor shows is that line of the file, with the members of the session's graph, from which a call opens
// in place, in this file or another; none until the graph view read them.
export function sourceOf(file: SessionFileData, members: NodeSourceData[] = []): NodeSourceData {
  const lines = file.text.split('\n').length
  return { node_id: file.path, name: fileNameOf(file.path), type: FILE_NODE, owner: '', file: file.path, text: file.text, start_line: 1, end_line: lines, members }
}

// What the file opens in place itself: each link to a heading in another file, that heading's section under its line;
// and in a story test, what each step invokes and observes, under the step's first line.
export function calloutsOf(file: SessionFileData): SourceCallout[] {
  const sections = file.callouts.map((callout): SourceCallout => ({ id: `${callout.section.path}:${callout.section.start_line}`, kind: 'section', line: callout.line, title: callout.title, path: callout.section.path, startLine: callout.section.start_line, endLine: callout.section.end_line, text: callout.section.content }))
  const steps = file.steps.flatMap(step => [...step.invokes.map(target => stepCallout(step.line, target, 'call')), ...step.observes.map(target => stepCallout(step.line, target, 'example'))])
  return [...sections, ...steps]
}

function stepCallout(line: number, target: NodeSourceData, kind: SourceCallout['kind']): SourceCallout {
  return { id: target.node_id, kind, line, title: target.owner ? `${target.owner}.${target.name}` : target.name, path: target.file, startLine: target.start_line, endLine: target.end_line, text: target.text }
}

// Whether the file is a story test whose steps reach code: its callouts are its steps' own, so a class it names, in a
// docstring or a step's code, opens nothing of its own.
export function isStoryTest(file: SessionFileData): boolean {
  return file.steps.length > 0
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
