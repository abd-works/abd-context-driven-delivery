import DOMPurify from 'dompurify'
import { Marked, type TokenizerAndRendererExtension, type Tokens } from 'marked'

// A markdown file as the page it describes: its front matter small above it, its text in angle brackets that is no HTML
// tag kept as text, its ++underlined++ terms underlined, the levels of an indented tree kept, and a mark at the end of
// each line that holds callouts, which the rendered view opens in place.

export const escaped = (text: string): string => text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;')

// The attribute a callout mark names its line by, counted from 1 in the file the text is of.
export const CALLOUT_LINE = 'data-callout-line'
export const RENDERED_CALLOUT_MARK = 'rendered-callout-mark'
// The attribute an indented block of a tree, such as a call graph under its state, names its depth in spaces by.
export const INDENT = 'data-indent'

// A mark's place in the text until the page is drawn: characters of Unicode's private use area, which no file's text
// and no markup holds, around the line's number.
const MARK_OPEN = ''
const MARK_CLOSE = ''
const MARKED_LINE = new RegExp(`${MARK_OPEN}(\\d+)${MARK_CLOSE}`, 'g')

const TAG = /<\/?([A-Za-z][\w:-]*)[^<>]*>/g
const FRONT_MATTER_RULE = '---'
const FENCE = /^( *)(`{3,}|~{3,})/
const LIST_ITEM = /^ *(?:[-*+]|\d+[.)])\s/
// What a line starts with when its indentation belongs to markdown itself: a table, a heading, a quote, HTML, or a rule.
const KEEPS_ITS_INDENT = /^(?:[|#>< ]|(?:-{3,}|\*{3,}|_{3,})\s*$)/
const NON_BREAKING_SPACE = '&nbsp;'

// Whether name is a tag HTML written in markdown uses: lower case, as HTML is written, and an element browsers know. A
// class in angle brackets, such as <Cart> or <Address>, is the file's text.
function isHtmlTag(name: string): boolean {
  return name === name.toLowerCase() && !(document.createElement(name) instanceof HTMLUnknownElement)
}

const withTextInAngleBrackets = (html: string): string => html.replace(TAG, (tag, name: string) => (isHtmlTag(name) ? tag : escaped(tag)))

// ++Book++, as a scenario marks a domain term or an example: underlined, whatever it holds, such as a link.
const underline: TokenizerAndRendererExtension = {
  name: 'underline',
  level: 'inline',
  start: (source: string) => source.indexOf('++'),
  tokenizer(source: string) {
    const found = /^\+\+(?=\S)([^\n]*?\S)\+\+/.exec(source)
    return found ? { type: 'underline', raw: found[0], tokens: this.lexer.inlineTokens(found[1] ?? '') } : undefined
  },
  renderer(token) {
    return `<u>${this.parser.parseInline(token.tokens ?? [])}</u>`
  },
}

// The page's own marked, so the one Monaco loads for its hovers keeps its own rules.
const pages = new Marked({ gfm: true, breaks: true, async: false, extensions: [underline], renderer: { html: (token: Tokens.HTML | Tokens.Tag) => withTextInAngleBrackets(token.text) } })

// The lines of a file's front matter, the facts between its first two --- rules, and the line its page starts on.
function frontMatterOf(lines: string[]): { facts: string[]; pageStarts: number } {
  const end = lines[0]?.trim() === FRONT_MATTER_RULE ? lines.findIndex((line, index) => index > 0 && line.trim() === FRONT_MATTER_RULE) : -1
  return end < 0 ? { facts: [], pageStarts: 0 } : { facts: lines.slice(1, end), pageStarts: end + 1 }
}

const factsShown = (facts: string[]): string => (facts.length ? `<div class="front-matter">${facts.map(fact => `<div>${escaped(fact)}</div>`).join('')}</div>` : '')

// A line with its mark, before the spaces that end it and, in a table, before the bar that closes its last cell.
function withMark(line: string, number: number): string {
  const text = line.trimEnd()
  const cut = text.endsWith('|') ? text.length - 1 : text.length
  return `${line.slice(0, cut)}${MARK_OPEN}${number}${MARK_CLOSE}${line.slice(cut)}`
}

// The page's lines as markdown reads a tree's levels: outside a list, a line of text keeps its indentation as spaces
// that do not collapse, and a fenced block indented under a state, which markdown would run into the state's own line,
// is a block of its own, as deep as the file writes it. marks names the lines that carry a callout mark, by number.
class PageLines {
  private readonly shown: string[] = []
  private inList = false
  private closes = ''
  private indented = 0

  constructor(private readonly first: number, private readonly marks: ReadonlySet<number>) {}

  read(lines: string[]): string {
    lines.forEach((line, index) => this.take(line, this.first + index))
    if (this.closes && this.indented) this.shown.push('', '</div>')
    return this.shown.join('\n')
  }

  private take(line: string, number: number): void {
    const fence = FENCE.exec(line)
    if (this.closes) return this.takeFenced(line, fence)
    if (fence) return this.openFence(line, fence)
    const text = this.marks.has(number) ? withMark(line, number) : line
    if (LIST_ITEM.test(line)) this.inList = true
    else if (line.trim() && !line.startsWith(' ')) this.inList = false
    this.shown.push(this.inList ? text : withLevel(text))
  }

  private openFence(line: string, fence: RegExpExecArray): void {
    this.closes = fence[2] ?? ''
    this.indented = this.inList ? 0 : (fence[1] ?? '').length
    if (this.indented) this.shown.push('', `<div class="indented" ${INDENT}="${this.indented}">`, '')
    this.shown.push(line.slice(this.indented))
  }

  private takeFenced(line: string, fence: RegExpExecArray | null): void {
    this.shown.push(line.slice(Math.min(this.indented, line.length - line.trimStart().length)))
    if (!fence || !(fence[2] ?? '').startsWith(this.closes) || line.trim() !== fence[2]) return
    if (this.indented) this.shown.push('', '</div>', '')
    this.closes = ''
    this.indented = 0
  }
}

// A line of text with its indentation kept: each leading space one that does not collapse.
function withLevel(line: string): string {
  const depth = line.length - line.trimStart().length
  const text = line.slice(depth)
  return depth && text && !KEEPS_ITS_INDENT.test(text) && !/\t/.test(line.slice(0, depth)) ? `${NON_BREAKING_SPACE.repeat(depth)}${text}` : line
}

const markShown = (_found: string, line: string): string => `<button type="button" class="${RENDERED_CALLOUT_MARK}" ${CALLOUT_LINE}="${line}"></button>`

// The markup of text, a markdown file's or the lines of one from firstLine on, cleaned by DOMPurify so no script or
// event handler it holds runs in the page, with a mark at the end of each of markedLines, numbered as the file's are.
export function markdownPage(text: string, markedLines: number[] = [], firstLine: number = 1): string {
  const lines = text.split(/\r?\n/)
  const { facts, pageStarts } = firstLine === 1 ? frontMatterOf(lines) : { facts: [], pageStarts: 0 }
  const page = new PageLines(firstLine + pageStarts, new Set(markedLines)).read(lines.slice(pageStarts))
  const drawn = DOMPurify.sanitize(pages.parse(page) as string)
  return `${factsShown(facts)}${drawn.replace(MARKED_LINE, markShown)}`
}
