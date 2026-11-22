import { useEffect, useMemo, useRef, useState, type ComponentProps, type MouseEvent } from 'react'

import type { NodeSourceData } from '@cdd/harness/graph/graph'
import { calloutsWithin } from '@source-view/SourceView'
import { CallCatalog } from '@source-view/call-expansion'
import type { SourceCallout } from '@source-view/source-callouts'

import type { FileCallouts } from './file-callouts'
import { FileSourceView } from './file-source-view'
import { opensRendered, renderedFormOf, renderingOf, type RenderedForm, type Rendering } from './file-rendering'
import { FILE_PATH, RenderedCallouts } from './rendered-callouts'
import { calloutsOf } from './source-of-file'

const NO_CALLOUTS: SourceCallout[] = []
const NO_MEMBERS: NodeSourceData[] = []

// What the source view takes, and callouts, which reads another file's callouts for a section opened in place.
type FileViewProps = ComponentProps<typeof FileSourceView> & { callouts: FileCallouts }

// Rendered and Source, the two ways a file with a rendered form shows; the one showing is pressed.
function RenderedToggleView({ rendered, onChoose }: { rendered: boolean; onChoose: (rendered: boolean) => void }) {
  return (
    <div className="file-render-toggle" role="group" aria-label="Show the file">
      <button type="button" className={rendered ? 'is-on' : ''} aria-pressed={rendered} title="Show the file as the page it describes" onClick={() => onChoose(true)}>
        Rendered
      </button>
      <button type="button" className={rendered ? '' : 'is-on'} aria-pressed={!rendered} title="Show the file's text in the source view" onClick={() => onChoose(false)}>
        Source
      </button>
    </div>
  )
}

// A markdown file drawn as the page it describes, with its callouts and links: a line that holds callouts ends in a
// mark that opens them in place, and a press on a link follows it, to another file of the session or, for a web
// address, to a tab of its own. The page is drawn again only when the file's text or the callouts shown change, so a
// file read again as it was, as while a comment on it is sent, keeps the callouts a person opened.
function MarkdownPageView({ path, html, shown, rendered }: { path: string; html: string; shown: SourceCallout[]; rendered: RenderedCallouts }) {
  const page = useRef<HTMLDivElement>(null)
  const held = useRef(shown)
  held.current = shown
  const drawn = shown.map(callout => `${callout.line} ${callout.id} ${callout.endLine}`).join('\n')
  useEffect(() => {
    if (!page.current) return
    page.current.innerHTML = html
    rendered.mark(page.current, held.current)
  }, [html, drawn, rendered])
  const follow = (event: MouseEvent<HTMLElement>) => {
    if (rendered.follow(event.target as Element)) event.preventDefault()
  }
  return <div ref={page} className="markdown-page" {...{ [FILE_PATH]: path }} onClick={follow} />
}

// The file drawn as its form draws it: markdown and SVG in the page, cleaned of scripts; an HTML page in a frame whose
// sandbox runs none of its scripts; JSON laid out, or as its text with the reason it is not valid.
function RenderedFileView({ path, rendering, shown, rendered }: { path: string; rendering: Rendering; shown: SourceCallout[]; rendered: RenderedCallouts }) {
  if (rendering.form === 'html') return <iframe className="file-rendered rendered-html" title={`${path} rendered`} sandbox="" srcDoc={rendering.html} />
  return (
    <div className={`file-rendered rendered-${rendering.form}`} aria-label={`${path} rendered`}>
      {rendering.problem ? <p className="files-note rendered-problem">{rendering.problem}</p> : null}
      {rendering.form === 'json' ? <pre dangerouslySetInnerHTML={{ __html: rendering.html }} /> : null}
      {rendering.form === 'svg' ? <div className="markdown-page" dangerouslySetInnerHTML={{ __html: rendering.html }} /> : null}
      {rendering.form === 'markdown' ? <MarkdownPageView path={path} html={rendering.html} shown={shown} rendered={rendered} /> : null}
    </div>
  )
}

// What opens the callouts of a rendered page in place: the callouts of another file as the session answers them for the
// file view's filters, the calls the graph's members let an open callout reach, and Go to file. Made once for the open file and asking
// what the page holds now, so the graph's members arriving close no callout a person opened.
function useRenderedCallouts({ callouts, members = NO_MEMBERS, onGoToFile }: Pick<FileViewProps, 'callouts' | 'members' | 'onGoToFile'>): RenderedCallouts {
  const within = useMemo(() => calloutsWithin(new CallCatalog(members)), [members])
  const now = useRef({ callouts, within, onGoToFile })
  now.current = { callouts, within, onGoToFile }
  return useMemo(() => new RenderedCallouts({ calloutsIn: path => now.current.callouts.in(path), within: (callout, stack) => now.current.within(callout, stack), goTo: callout => now.current.onGoToFile?.(callout) }), [])
}

function RenderableFileView({ form, callouts, ...props }: FileViewProps & { form: RenderedForm }) {
  const around = props.openAround ?? []
  const [isRendered, setRendered] = useState(() => opensRendered(form, around))
  // Lines asked to show once the file is open, such as a node selected in the graph view, show in the source view; the
  // Person can still press Rendered until other lines are asked for.
  const asked = around.map(lines => `${lines.start}-${lines.end}`).join(',')
  useEffect(() => {
    if (asked) setRendered(false)
  }, [asked])
  const { file } = props
  // The callouts the session answered for the file view's filters, on the rendered page as in the source view.
  const shown = useMemo(() => (isRendered && form === 'markdown' ? calloutsOf(file) : NO_CALLOUTS), [isRendered, form, file])
  const rendering = useMemo(() => (isRendered ? renderingOf(form, file.text, [...new Set(shown.map(callout => callout.line))]) : null), [isRendered, form, file.text, shown])
  const rendered = useRenderedCallouts({ callouts, members: props.members, onGoToFile: props.onGoToFile })
  const toggle = <RenderedToggleView rendered={isRendered} onChoose={setRendered} />
  if (!rendering) return <FileSourceView {...props} toggle={toggle} />
  return (
    <div className="file-source">
      <div className="file-source-bar">{toggle}</div>
      <RenderedFileView path={file.path} rendering={rendering} shown={shown} rendered={rendered} />
    </div>
  )
}

// An open file: a file with a rendered form (markdown, HTML, SVG, JSON) opens rendered, unless lines of it are asked to
// show, with Rendered and Source to switch between the two; any other file opens in the source view alone. Both views
// show the file's callouts and follow its links.
export function FileView({ callouts, ...props }: FileViewProps) {
  const form = renderedFormOf(props.file.path)
  if (!form) return <FileSourceView {...props} />
  return <RenderableFileView {...props} callouts={callouts} form={form} />
}
