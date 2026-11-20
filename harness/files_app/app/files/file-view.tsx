import { useEffect, useMemo, useState, type ComponentProps, type MouseEvent } from 'react'

import { FileSourceView } from './file-source-view'
import { opensRendered, renderedFormOf, renderingOf, type RenderedForm, type Rendering } from './file-rendering'

type FileViewProps = ComponentProps<typeof FileSourceView>

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

const isWebLink = (href: string): boolean => /^https?:\/\//i.test(href)

// A link in a rendered page opens a web page in a tab of its own; any other, such as a link to another file, would take
// the Files app's own page away, so it stays put: Source shows where it points.
function keepPage(event: MouseEvent<HTMLElement>): void {
  const link = (event.target as HTMLElement).closest('a')
  if (!link) return
  event.preventDefault()
  const href = link.getAttribute('href') ?? ''
  if (isWebLink(href)) window.open(href, '_blank', 'noopener')
}

// The file drawn as its form draws it: markdown and SVG in the page, cleaned of scripts; an HTML page in a frame whose
// sandbox runs none of its scripts; JSON laid out, or as its text with the reason it is not valid.
function RenderedFileView({ path, rendering }: { path: string; rendering: Rendering }) {
  if (rendering.form === 'html') return <iframe className="file-rendered rendered-html" title={`${path} rendered`} sandbox="" srcDoc={rendering.html} />
  return (
    <div className={`file-rendered rendered-${rendering.form}`} aria-label={`${path} rendered`}>
      {rendering.problem ? <p className="files-note rendered-problem">{rendering.problem}</p> : null}
      {rendering.form === 'json' ? <pre dangerouslySetInnerHTML={{ __html: rendering.html }} /> : <div className="markdown-page" onClick={keepPage} dangerouslySetInnerHTML={{ __html: rendering.html }} />}
    </div>
  )
}

function RenderableFileView({ form, ...props }: FileViewProps & { form: RenderedForm }) {
  const around = props.openAround ?? []
  const [rendered, setRendered] = useState(() => opensRendered(form, around))
  // Lines asked to show once the file is open, such as a node selected in the graph view, show in the source view; the
  // Person can still press Rendered until other lines are asked for.
  const asked = around.map(lines => `${lines.start}-${lines.end}`).join(',')
  useEffect(() => {
    if (asked) setRendered(false)
  }, [asked])
  const rendering = useMemo(() => (rendered ? renderingOf(form, props.file.text) : null), [rendered, form, props.file.text])
  const toggle = <RenderedToggleView rendered={rendered} onChoose={setRendered} />
  if (!rendering) return <FileSourceView {...props} toggle={toggle} />
  return (
    <div className="file-source">
      <div className="file-source-bar">{toggle}</div>
      <RenderedFileView path={props.file.path} rendering={rendering} />
    </div>
  )
}

// An open file: a file with a rendered form (markdown, HTML, SVG, JSON) opens rendered, unless lines of it are asked to
// show, with Rendered and Source to switch between the two; any other file opens in the source view alone.
export function FileView(props: FileViewProps) {
  const form = renderedFormOf(props.file.path)
  if (!form) return <FileSourceView {...props} />
  return <RenderableFileView {...props} form={form} />
}
