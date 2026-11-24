import DOMPurify from 'dompurify'

import { escaped, markdownPage } from './markdown-page'

// The forms a file renders in beside its source: markdown as the page it describes (markdown-page.ts), an HTML page in
// a frame that runs no script, an SVG as its drawing, and JSON laid out. marked and DOMPurify are the versions Monaco
// loads for its own hovers. Each line of a paragraph keeps a line of its own, as a scenario's steps do. Which form a
// file renders in is the session's answer (session.file rendered_form).
export type RenderedForm = 'markdown' | 'html' | 'svg' | 'json'

// What the rendered view draws: html is the markup it shows (for an HTML page, the frame's document; for JSON, its
// laid-out text, escaped), and problem says why it could not render the file as its form, such as JSON that is not valid.
export interface Rendering {
  form: RenderedForm
  html: string
  problem: string
}

const JSON_INDENT = 2

function laidOut(text: string): Rendering {
  try {
    return { form: 'json', html: escaped(JSON.stringify(JSON.parse(text), null, JSON_INDENT)), problem: '' }
  } catch (error) {
    return { form: 'json', html: escaped(text), problem: `Not valid JSON: ${(error as Error).message}` }
  }
}

// The file's text as its form draws it. Markdown and SVG go through DOMPurify, so no script or event handler the file
// holds runs in the page; an HTML page is handed as it is to a sandboxed frame, which runs none of its scripts. A
// markdown page carries a mark at the end of each of calloutLines, the lines that hold callouts.
export function renderingOf(form: RenderedForm, text: string, calloutLines: number[] = []): Rendering {
  if (form === 'markdown') return { form, html: markdownPage(text, calloutLines), problem: '' }
  if (form === 'svg') return { form, html: DOMPurify.sanitize(text, { USE_PROFILES: { svg: true, svgFilters: true } }), problem: '' }
  if (form === 'json') return laidOut(text)
  return { form, html: text, problem: '' }
}
