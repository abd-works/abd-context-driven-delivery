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
      <path d="M3 8.5L6.5 12L13 4.5" stroke="var(--reviewed)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

// The three ways the files panel shows a fidelity's files: a list, the folder they sit in, and the files themselves.
const FILE_VIEW_SHAPES: Record<string, string> = {
  list: 'M5.5 4h8M5.5 8h8M5.5 12h8M2.5 4h.01M2.5 8h.01M2.5 12h.01',
  folder: 'M2 4.5a1 1 0 0 1 1-1h3l1.5 1.5H13a1 1 0 0 1 1 1V12a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1z',
  files: 'M5 2.5h5l3 3V12a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V3.5a1 1 0 0 1 1-1zM10 2.5V5.5h3M3 5v8.5a1 1 0 0 0 1 1h6',
}

export function FileViewIcon({ mode }: { mode: string }) {
  return (
    <svg width="14" height="14" viewBox="0 0 16 16" fill="none" aria-hidden="true" style={{ display: 'block' }}>
      <path d={FILE_VIEW_SHAPES[mode] ?? ''} {...STROKE} />
    </svg>
  )
}

const FORMAT_SHAPES: Record<string, string> = {
  diagram: 'M2 2.5h4v3H2zM10 10.5h4v3h-4zM4 5.5v3.5a1.5 1.5 0 0 0 1.5 1.5H10',
  markdown: 'M2 3.5h12v9H2zM4.5 10V6l2 2.3L8.5 6v4M11 6v3.5M9.8 8.5L11 10l1.2-1.5',
  code: 'M5.5 4.5L2 8l3.5 3.5M10.5 4.5L14 8l-3.5 3.5M9 3L7 13',
}

export function FormatIcon({ label }: { label: string }) {
  const shape = FORMAT_SHAPES[label]
  if (!shape) return <span className="format-word">{label}</span>
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true" style={{ display: 'block' }}>
      <path d={shape} {...STROKE} />
    </svg>
  )
}
