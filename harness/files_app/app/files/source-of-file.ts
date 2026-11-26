import type { NodeSourceData } from '@cdd/harness/graph/graph'
import type { FileViolationData, SessionFileData } from '@cdd/space/session/session'
import type { SourceRule } from '@source-view/SourceView'
import type { SourceCallout } from '@source-view/source-callouts'
import type { ViolationFocus } from '@graph-app/graph/graph-selection'
import { withoutCallMarkers } from '@source-view/call-expansion'
import { saidBy } from './reason'

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
  const steps = listOf<Record<string, unknown>>(file.steps).map(step => ({ ...step, callouts: listOf(step.callouts) }))
  return {
    ...(file as SessionFileData),
    language: typeof file.language === 'string' ? file.language : '',
    rendered_form: typeof file.rendered_form === 'string' ? file.rendered_form : '',
    comments: listOf(file.comments),
    changes: listOf(file.changes),
    folds: listOf(file.folds),
    steps: steps as SessionFileData['steps'],
    callouts: listOf(file.callouts),
    violations: listOf(file.violations),
  }
}

const listOf = <Item>(list: unknown): Item[] => (Array.isArray(list) ? (list as Item[]) : [])

// How the graph explorer's source view reads a session's file: the whole file as one source, from its first line, so
// each line the editor shows is that line of the file, with the members of the session's graph, from which a call opens
// in place, in this file or another; none until the graph view read them.
export function sourceOf(file: SessionFileData, members: NodeSourceData[] = []): NodeSourceData {
  const lines = file.text.split('\n').length
  return { node_id: file.path, name: fileNameOf(file.path), type: FILE_NODE, owner: '', file: file.path, text: file.text, start_line: 1, end_line: lines, members }
}

// A callout as session.file answers it since links to whole files and missing targets carry one; a cdd server lane
// older than the page answers neither link nor missing.
type LinkCallout = SessionFileData['callouts'][number] & { link?: string; missing?: string }

// What a link opens in place: the section or file it names, or, when that is not there, what is missing.
function linkCallout(callout: LinkCallout): SourceCallout {
  const { path, start_line: startLine, end_line: endLine, content } = callout.section
  const linked = { line: callout.line, title: callout.title, link: callout.link ?? '', path, startLine, endLine }
  return callout.missing ? { ...linked, id: `${path}:missing:${callout.link}`, kind: 'missing', text: callout.missing } : { ...linked, id: `${path}:${startLine}`, kind: 'section', text: content }
}

// What the file opens in place itself: each link to another file, the section or file it names under its line; and in a
// story test, what each step invokes and observes, on the line and under the title the session answered for it, so the
// code it reaches opens where the step reaches it.
export function calloutsOf(file: SessionFileData): SourceCallout[] {
  const sections = file.callouts.map(linkCallout)
  const steps = file.steps.flatMap(step => step.callouts.map(stepCallout))
  return [...sections, ...steps]
}

function stepCallout({ kind, line, title, target }: SessionFileData['steps'][number]['callouts'][number]): SourceCallout {
  return { id: target.node_id, kind, line, title, path: target.file, startLine: target.start_line, endLine: target.end_line, text: withoutCallMarkers(target.text) }
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

// Every place the chosen rule is broken in the file, which the source view marks and offers Fix this one for, each with
// the comment Python wrote for it.
export function violationFocusOf(file: SessionFileData, rule: string): ViolationFocus | null {
  const found: FileViolationData[] = file.violations.filter(each => each.violation.rule === rule)
  if (!found.length) return null
  return { rule, places: found.map(each => ({ message: each.violation.message, startLine: each.range.start_line, endLine: each.range.end_line, correctionComment: each.correction_comment })) }
}

// The language Monaco colours the file as, from the session's answer.
export function monacoLanguageOf(file: SessionFileData): string {
  return file.language || 'plaintext'
}
