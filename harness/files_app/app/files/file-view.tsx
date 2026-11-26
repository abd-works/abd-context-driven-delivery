import { useEffect, useMemo, useRef, useState, type ComponentProps, type MouseEvent } from 'react'

import type { NodeSourceData } from '@cdd/harness/graph/graph'
import { calloutsWithin } from '@source-view/SourceView'
import { CallCatalog } from '@source-view/call-expansion'
import type { SourceCallout } from '@source-view/source-callouts'

import type { FileCallouts } from './file-callouts'
import { FileSourceView } from './file-source-view'
import { renderingOf, type RenderedForm, type Rendering } from './file-rendering'
import { FILE_PATH, RenderedCallouts } from './rendered-callouts'
import type { PageFrames } from './page-frames'
import { calloutsOf } from './source-of-file'

const NO_CALLOUTS: SourceCallout[] = []
const NO_MEMBERS: NodeSourceData[] = []

// What the source view takes; callouts, which reads another file's callouts for a section opened in place; and frames,
// which shows an HTML page running its own scripts.
type FileViewProps = ComponentProps<typeof FileSourceView> & { callouts: FileCallouts; frames: PageFrames }

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

// An HTML page in a frame whose sandbox runs the page's own scripts but gives it no origin, so nothing it runs reaches the
// Files app, its storage or its server's routes; the page finds the scripts, styles and images it names through the
// Files server, from its own folder of the project and, for a UX mockup, the Story Demo scripts. The frame waits for that
// address, so the page's scripts run once; a page whose address could not be read shows without it, and says so.
function FramedPageView({ path, html, frames }: { path: string; html: string; frames: PageFrames }) {
  const [page, setPage] = useState<{ html: string; problem: string } | null>(null)
  useEffect(() => {
    let shown = true
    frames.pageOf(path, html).then(
      framed => shown && setPage({ html: framed, problem: '' }),
      failure => shown && setPage({ html, problem: `The page's own scripts, styles and images could not be reached: ${(failure as Error).message}` }),
    )
    return () => {
      shown = false
    }
  }, [frames, path, html])
  if (!page) return null
  return (
    <>
      {page.problem ? <p className="files-note rendered-problem">{page.problem}</p> : null}
      <iframe className="file-rendered rendered-html" title={`${path} rendered`} sandbox="allow-scripts" srcDoc={page.html} />
    </>
  )
}

// The file drawn as its form draws it: markdown and SVG in the page, cleaned of scripts; an HTML page in a frame of its
// own, running its scripts apart from the Files app; JSON laid out, or as its text with the reason it is not valid.
function RenderedFileView({ path, rendering, shown, rendered, frames }: { path: string; rendering: Rendering; shown: SourceCallout[]; rendered: RenderedCallouts; frames: PageFrames }) {
  if (rendering.form === 'html') return <FramedPageView path={path} html={rendering.html} frames={frames} />
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

function RenderableFileView({ form, callouts, frames, ...props }: FileViewProps & { form: RenderedForm }) {
  const around = props.openAround ?? []
  // It opens rendered unless lines of it are asked to show, such as a node selected in the graph view, whose lines,
  // comments and broken rules only the source view marks.
  const [isRendered, setRendered] = useState(() => around.length === 0)
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
      <RenderedFileView path={file.path} rendering={rendering} shown={shown} rendered={rendered} frames={frames} />
    </div>
  )
}

// An open file: a file the session answers a rendered form for (markdown, HTML, SVG, JSON) opens rendered, unless lines of it are asked to
// show, with Rendered and Source to switch between the two; any other file opens in the source view alone. Both views
// show the file's callouts and follow its links.
export function FileView({ callouts, ...props }: FileViewProps) {
  const form = props.file.rendered_form as RenderedForm | ''
  if (!form) return <FileSourceView {...props} />
  return <RenderableFileView {...props} callouts={callouts} form={form} />
}
