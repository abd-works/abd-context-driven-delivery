import type { NodeSourceData } from '@cdd/harness/graph/graph'
import type { FileViolationData, SessionFileData } from '@cdd/space/session/session'
import type { SourceRule } from '@source-view/SourceView'
import type { SourceCallout } from '@source-view/source-callouts'
import type { SourceLines } from '@source-view/source-folding'
import type { ViolationFocus } from '@graph-app/graph/graph-selection'
import { MODULE_OWNER, codeOf, withoutCallMarkers } from '@source-view/call-expansion'

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
// story test, each connector of a step, what it invokes and observes, collapsed under the line of the step that uses it,
// so the code it reaches opens where the step reaches it.
export function calloutsOf(file: SessionFileData): SourceCallout[] {
  const sections = file.callouts.map(linkCallout)
  const code = typeof file.text === 'string' ? codeOf(file.text, monacoLanguageOf(file)).split(String.fromCharCode(10)) : []
  const starts = file.steps.map(step => step.line).sort((one, other) => one - other)
  const steps = file.steps.flatMap(step => {
    const using = (target: NodeSourceData) => lineUsing(code, step.line, starts.find(start => start > step.line), target.name)
    return [...step.invokes.map(target => stepCallout(using(target), target, 'call')), ...step.observes.map(target => stepCallout(using(target), target, 'example'))]
  })
  return [...sections, ...steps]
}

// The first line from the step's own line, before the next step starts, whose code names name; the step's own line when
// none does, as for a file read with no text.
function lineUsing(code: string[], stepLine: number, nextStep: number | undefined, name: string): number {
  const named = new RegExp(`\\b${name.replace(/[^A-Za-z0-9_]/g, '')}\\b`)
  const last = Math.min(code.length, (nextStep ?? code.length + 1) - 1)
  for (let line = stepLine; line <= last; line += 1) if (named.test(code[line - 1] ?? '')) return line
  return stepLine
}

function stepCallout(line: number, target: NodeSourceData, kind: SourceCallout['kind']): SourceCallout {
  return { id: target.node_id, kind, line, title: target.owner && target.owner !== MODULE_OWNER ? `${target.owner}.${target.name}` : target.name, path: target.file, startLine: target.start_line, endLine: target.end_line, text: withoutCallMarkers(target.text) }
}

// The lines whose fold-outs open for the nodes expanded, such as one selected in the graph through a connector: each
// line of a callout reaching one of them inside the lines around, the node that holds the connector; anywhere in the file
// when nothing is around.
export function expandedLines(callouts: SourceCallout[], expanded: string[], around: SourceLines[]): number[] {
  const inside = (line: number) => !around.length || around.some(lines => lines.start <= line && line <= lines.end)
  return [...new Set(callouts.filter(callout => expanded.includes(callout.id) && inside(callout.line)).map(callout => callout.line))]
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
