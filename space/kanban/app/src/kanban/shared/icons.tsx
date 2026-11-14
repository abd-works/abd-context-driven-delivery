const STROKE = { stroke: 'currentColor', strokeWidth: 1.5, strokeLinecap: 'round', strokeLinejoin: 'round' } as const

export function BrandMark() {
  return (
    <svg width="18" height="18" viewBox="0 0 256 256" role="img" aria-label="abd.works">
      <path fill="#E5531A" fillRule="evenodd" d="M52.98,20.31l150.04,84.18v46.44S52.98,235.69,52.98,235.69v-54.77s104.7-53.41,104.7-53.41l-104.7-52.83V20.31Z" />
    </svg>
  )
}

export function ExpandIcon({ isExpanded }: { isExpanded: boolean }) {
  const shape = isExpanded ? 'M13.5 2.5L9.5 6.5M9.5 3V6.5H13M2.5 13.5L6.5 9.5M3 9.5H6.5V13' : 'M9.5 2.5H13.5V6.5M13.5 2.5L9 7M6.5 13.5H2.5V9.5M2.5 13.5L7 9'
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
      <path d={shape} {...STROKE} />
    </svg>
  )
}

export function ChevronIcon({ isTurned }: { isTurned: boolean }) {
  return (
    <svg width="14" height="14" viewBox="0 0 16 16" fill="none" aria-hidden="true" style={{ transform: isTurned ? 'rotate(-90deg)' : 'none' }}>
      <path d="M3.5 6L8 10.5L12.5 6" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

export function CheckIcon() {
  return (
    <svg className="tile-check" width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
      <path d="M3 8.5L6.5 12L13 4.5" stroke="var(--done)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

// The three ways the files panel shows a fidelity's files: a list, the folder they sit in, and the files themselves.
const FILE_VIEW_SHAPES: Record<string, string> = {
  folder: 'M2 4.5a1 1 0 0 1 1-1h3l1.5 1.5H13a1 1 0 0 1 1 1V12a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1z',
  files: 'M5 2.5h5l3 3V12a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V3.5a1 1 0 0 1 1-1zM10 2.5V5.5h3M3 5v8.5a1 1 0 0 0 1 1h6',
  // the knowledge graph: three nodes joined
  graph: 'M4 4.5a1.5 1.5 0 1 0 0 .01M12 4.5a1.5 1.5 0 1 0 0 .01M8 12a1.5 1.5 0 1 0 0 .01M5.3 5.3l1.9 5.4M10.7 5.3l-1.9 5.4M5.5 4.5h5',
}

// One line drawing in the board's stroke, at the size of the control it sits on; each icon below names its shape.
function ShapeIcon({ shape, size }: { shape: string; size: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 16 16" fill="none" aria-hidden="true" style={{ display: 'block' }}>
      <path d={shape} {...STROKE} />
    </svg>
  )
}

export function FileViewIcon({ mode }: { mode: string }) {
  return <ShapeIcon shape={FILE_VIEW_SHAPES[mode] ?? ''} size={14} />
}

// What a card does for its session: run the next step, hand off, split into child tickets, open its chat, activate or
// close it, and keep it up to date: edit its text, tag it, or delete it.
const SESSION_ACTION_SHAPES: Record<string, string> = {
  chat: 'M2.5 3.5h11v7h-6l-3 2.5v-2.5h-2z',
  next: 'M4.5 3v10l8-5z',
  handoff: 'M2.5 8h9M8.5 4.5L12 8l-3.5 3.5M13.5 3v10',
  split: 'M2.5 8h4M6.5 8L10 4.5h3.5M6.5 8l3.5 3.5h3.5',
  child: 'M8 3v10M3 8h10',
  activate: 'M8 2.5v5M4.8 4.5a4.5 4.5 0 1 0 6.4 0',
  close: 'M4 4l8 8M12 4l-8 8',
  text: 'M3 13l1-3.5 7-7 2.5 2.5-7 7zM9.5 4l2.5 2.5',
  tag: 'M2.5 2.5h5.5l5.5 5.5-5.5 5.5-5.5-5.5zM5.5 5.5h.01',
  delete: 'M3 4.5h10M6.5 4.5V3h3v1.5M4.5 4.5l.7 8.5h5.6l.7-8.5',
}

export function SessionActionIcon({ action }: { action: string }) {
  return <ShapeIcon shape={SESSION_ACTION_SHAPES[action] ?? ''} size={14} />
}

const FORMAT_SHAPES: Record<string, string> = {
  diagram: 'M2 2.5h4v3H2zM10 10.5h4v3h-4zM4 5.5v3.5a1.5 1.5 0 0 0 1.5 1.5H10',
  markdown: 'M2 3.5h12v9H2zM4.5 10V6l2 2.3L8.5 6v4M11 6v3.5M9.8 8.5L11 10l1.2-1.5',
  code: 'M5.5 4.5L2 8l3.5 3.5M10.5 4.5L14 8l-3.5 3.5M9 3L7 13',
}

export function FormatIcon({ label }: { label: string }) {
  const shape = FORMAT_SHAPES[label]
  if (!shape) return <span className="format-word">{label}</span>
  return <ShapeIcon shape={shape} size={16} />
}
