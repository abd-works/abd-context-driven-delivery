import { calloutPlace, type CalloutsWithin, type GoToFile, type SourceCallout } from '@source-view/source-callouts'

import { CALLOUT_LINE, RENDERED_CALLOUT_MARK, escaped, markdownPage } from './markdown-page'

// What the rendered view asks for to open callouts in place: the callouts of another file, which a section opened in
// place shows on its own lines; the calls and classes the code of an open callout reaches; and how a link is followed.
export type RenderedReads = { calloutsIn: (path: string) => Promise<SourceCallout[]>; within: CalloutsWithin; goTo: GoToFile }

export const RENDERED_CALLOUT_BLOCK = 'rendered-callout-block'
// The attribute a drawn page, and each section opened in place, names its file by, which its links are read from.
export const FILE_PATH = 'data-file-path'
const OPEN = 'is-open'
// What a callout opens under: its own line of code, or the heading or table its line is in; else it opens where it sits.
const OPENS_AFTER = '.callout-text, h1, h2, h3, h4, h5, h6, table'

const isMarkdown = (path: string): boolean => /\.(md|markdown)$/i.test(path)
const isWebLink = (href: string): boolean => /^[a-z][a-z0-9+.-]*:/i.test(href)
const linesOf = (callouts: SourceCallout[]): number[] => [...new Set(callouts.map(callout => callout.line))]

// The file a link written in the file at from names, from the project's top: `../domain-model.md#cart` in
// `story_tests/cart.md` is `domain-model.md`.
export function fileLinked(from: string, href: string): string {
  const named = (href.split('#')[0] ?? '').split('/')
  const folders = from.split('/').slice(0, -1)
  for (const part of named) {
    if (part === '..') folders.pop()
    else if (part && part !== '.') folders.push(part)
  }
  return folders.join('/')
}

// Code from startLine on, a line to a row, with a mark at the end of each of markedLines.
function codeLines(text: string, startLine: number, markedLines: number[]): string {
  const mark = (line: number) => (markedLines.includes(line) ? `<button type="button" class="${RENDERED_CALLOUT_MARK}" ${CALLOUT_LINE}="${line}"></button>` : '')
  return text.split('\n').map((line, index) => `<div class="callout-text">${escaped(line) || ' '}${mark(startLine + index)}</div>`).join('')
}

// The callouts of a rendered page, opened in place as the source view opens them. A line that holds callouts ends in a
// mark naming them; a press opens them under the line and a second press closes them. An open callout shows what it
// names, shaded once: a markdown section as the page it describes, code as its lines, and a missing one what is not
// there. What it shows carries marks of its own, a section those of its own file and code the calls it reaches, so a
// person goes from a story to its scenario, to what a step observes or invokes, to an operation it calls, without
// leaving the page. Its head opens it in its own file, and so does a press on the link that names it.
export class RenderedCallouts {
  private readonly shownIn = new WeakMap<Element, SourceCallout[]>()
  private readonly opened = new WeakMap<Element, HTMLElement>()

  constructor(private readonly reads: RenderedReads) {}

  // Gives each mark of page, a drawn page or section, its callouts among callouts; stack holds the callouts open around it.
  mark(page: HTMLElement, callouts: SourceCallout[], stack: string[] = []): void {
    this.shownIn.set(page, callouts)
    for (const mark of page.querySelectorAll<HTMLButtonElement>(`.${RENDERED_CALLOUT_MARK}`)) {
      const here = callouts.filter(callout => callout.line === Number(mark.getAttribute(CALLOUT_LINE)))
      mark.textContent = here.map(callout => callout.title).join(', ')
      mark.title = here.map(calloutPlace).join('\n')
      mark.classList.toggle('callout-missing', here.length > 0 && here.every(callout => callout.kind === 'missing'))
      mark.addEventListener('click', event => {
        event.preventDefault()
        event.stopPropagation()
        this.toggle(mark, here, stack)
      })
    }
  }

  // Follows the link pressed in a drawn page: a web address in a tab of its own; a link to another file opens that file
  // beside the page, at the section the link names when its callout holds one. Answers whether it was a link.
  follow(pressed: Element): boolean {
    const link = pressed.closest('a')
    const href = link?.getAttribute('href') ?? ''
    if (!link || !href) return false
    if (isWebLink(href)) window.open(href, '_blank', 'noopener')
    else if (!href.startsWith('#')) this.open(link, href)
    return true
  }

  private open(link: Element, href: string): void {
    const within = link.closest(`[${FILE_PATH}]`)
    const named = (within ? this.shownIn.get(within) : undefined)?.find(callout => callout.link === href)
    if (named?.kind === 'missing') return
    const path = fileLinked(within?.getAttribute(FILE_PATH) ?? '', href)
    this.reads.goTo(named ?? { id: path, kind: 'section', line: 0, title: link.textContent ?? path, link: href, path, startLine: 1, endLine: 1, text: '' })
  }

  private toggle(mark: HTMLElement, callouts: SourceCallout[], stack: string[]): void {
    const shown = this.opened.get(mark)
    this.opened.delete(mark)
    mark.classList.toggle(OPEN, !shown)
    mark.setAttribute('aria-expanded', String(!shown))
    if (shown) return shown.remove()
    const block = document.createElement('div')
    block.className = `callout-block ${RENDERED_CALLOUT_BLOCK}`
    block.append(...callouts.map(callout => this.section(callout, [...stack, callout.id])))
    this.opened.set(mark, block)
    ;(mark.closest(OPENS_AFTER) ?? mark).after(block)
  }

  private section(callout: SourceCallout, stack: string[]): HTMLElement {
    const section = document.createElement('div')
    section.className = `callout-section callout-${callout.kind}`
    if (callout.kind === 'missing') {
      section.textContent = callout.text
      return section
    }
    section.append(this.head(callout), this.body(callout, stack))
    return section
  }

  private head(callout: SourceCallout): HTMLElement {
    const head = document.createElement('button')
    head.type = 'button'
    head.className = 'callout-go-to'
    head.textContent = `${callout.path} lines ${callout.startLine} to ${callout.endLine}`
    head.title = `Open ${callout.title} in its own file`
    head.addEventListener('click', () => this.reads.goTo(callout))
    return head
  }

  // What the callout shows, with the marks of the callouts on its own lines: for a section, those its file holds there,
  // once the session answers them; for code, the calls and classes it reaches.
  private body(callout: SourceCallout, stack: string[]): HTMLElement {
    const body = document.createElement('div')
    body.setAttribute(FILE_PATH, callout.path)
    body.className = isMarkdown(callout.path) ? 'markdown-page' : 'callout-code'
    const draw = (inner: SourceCallout[]) => {
      body.innerHTML = isMarkdown(callout.path) ? markdownPage(callout.text, linesOf(inner), callout.startLine) : codeLines(callout.text, callout.startLine, linesOf(inner))
      this.mark(body, inner, stack)
    }
    draw(callout.kind === 'section' ? [] : this.reads.within(callout, stack))
    if (callout.kind !== 'section') return body
    const onItsLines = (held: SourceCallout[]) => held.filter(inner => callout.startLine <= inner.line && inner.line <= callout.endLine && !stack.includes(inner.id))
    this.reads.calloutsIn(callout.path).then(held => draw(onItsLines(held)), failure => body.prepend(this.unread(callout, failure)))
    return body
  }

  // What an open section says when the session did not answer its file's callouts: the section stays, without marks.
  private unread(callout: SourceCallout, failure: unknown): HTMLElement {
    const note = document.createElement('p')
    note.className = 'files-note callout-unread'
    note.textContent = `The callouts of ${callout.path} did not read: ${failure instanceof Error ? failure.message : String(failure)}`
    return note
  }
}
