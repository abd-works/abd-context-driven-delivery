import { useMemo, useSyncExternalStore } from 'react'

import { FormatAlignmentClientGenerated, type AlignedFileData, type AlignmentFailureData, type AlignmentGapData } from '@cdd/align/format-alignment'

import type { FilesPage } from './files-page'
import { FormatAlignment } from './format-alignment'
import './format-alignment.css'

const STEP_LABELS = { idle: 'Diagnose', diagnosing: 'Diagnosing…', diagnosed: 'Diagnose again', aligning: 'Diagnose again', aligned: 'Diagnose again' } as const

// Diagnose and Align under the page's head: Diagnose goes through the session's selected stages, practices and chosen
// formats and its graph, and lists each gap in the session's words; Align renders the files a render brings in step.
// A gap a render does not close, and each failure an alignment met, carries Fix, which puts it on the band of failures
// above, whose own Fix sends it to the chat.
export function FormatAlignmentView({ page }: { page: FilesPage }) {
  const formats = useMemo(() => new FormatAlignment(FormatAlignmentClientGenerated.named(page.api, page.link.sessionFile), page.notices.fixes), [page])
  const state = useSyncExternalStore(formats.subscribe, () => formats.state)
  const isShown = state.step !== 'idle' && state.step !== 'diagnosing'
  return (
    <section className="format-alignment" aria-label="Diagnose and align formats">
      <div className="format-alignment-bar">
        <button type="button" className="format-alignment-button" disabled={formats.isBusy} title="Goes through the selected stages, practices and chosen formats and the session's graph, and lists each gap between the formats" onClick={() => void formats.diagnose()}>
          {STEP_LABELS[state.step]}
        </button>
        {isShown ? (
          <button type="button" className="format-alignment-button is-align" disabled={!formats.canAlign} title="Renders each missing file, and each file that lacks what another format holds, from the format that holds more" onClick={() => void formats.align()}>
            {state.step === 'aligning' ? 'Aligning…' : 'Align'}
          </button>
        ) : null}
        {isShown ? <span className="format-alignment-summary" role="status">{summaryOf(state.gaps.length, state.fidelities.length)}</span> : null}
        {isShown ? (
          <button type="button" className="format-alignment-close" aria-label="Close the diagnosis" title="Close the diagnosis" onClick={() => formats.close()}>
            ✕
          </button>
        ) : null}
      </div>
      {state.problem ? <p className="format-alignment-problem" role="alert">{state.problem}</p> : null}
      {state.aligned.length ? <AlignedFilesView aligned={state.aligned} /> : null}
      {state.failures.length ? <AlignmentFailuresView formats={formats} failures={state.failures} /> : null}
      {isShown && state.gaps.length ? <AlignmentGapsView formats={formats} gaps={state.gaps} /> : null}
    </section>
  )
}

const counted = (count: number, one: string, many: string): string => `${count} ${count === 1 ? one : many}`
const summaryOf = (gaps: number, fidelities: number): string => `${gaps ? counted(gaps, 'gap', 'gaps') : 'No gap'} in ${counted(fidelities, 'fidelity', 'fidelities')} checked`

function AlignedFilesView({ aligned }: { aligned: AlignedFileData[] }) {
  return (
    <ul className="format-alignment-list" aria-label="Files aligned">
      {aligned.map(done => (
        <li key={done.file} className="format-alignment-item is-aligned">
          <span className="format-alignment-said">
            Rendered {done.file} from {done.source}.{done.follow_up ? ` ${done.follow_up}` : ''}
          </span>
        </li>
      ))}
    </ul>
  )
}

function AlignmentFailuresView({ formats, failures }: { formats: FormatAlignment; failures: AlignmentFailureData[] }) {
  return (
    <ul className="format-alignment-list" aria-label="Failures of the alignment">
      {failures.map(failure => (
        <li key={`${failure.file}:${failure.message}`} className="format-alignment-item is-failure">
          <span className="format-alignment-said">{failure.message}</span>
          <button type="button" className="format-alignment-fix" title="Puts this failure on the band above, whose Fix sends it to the chat" onClick={() => formats.fixFailure(failure)}>
            Fix
          </button>
        </li>
      ))}
    </ul>
  )
}

function AlignmentGapsView({ formats, gaps }: { formats: FormatAlignment; gaps: AlignmentGapData[] }) {
  return (
    <ul className="format-alignment-list" aria-label="Gaps between the formats">
      {gaps.map(gap => (
        <li key={`${gap.kind}:${gap.file}:${gap.message}`} className={`format-alignment-item ${gap.is_alignable ? 'is-alignable' : 'is-person'}`}>
          <span className="format-alignment-said">{gap.message}</span>
          {gap.is_alignable ? (
            <span className="format-alignment-note">Align closes this</span>
          ) : (
            <button type="button" className="format-alignment-fix" title="Puts this gap on the band above, whose Fix sends it to the chat" onClick={() => formats.fixGap(gap)}>
              Fix
            </button>
          )}
        </li>
      ))}
    </ul>
  )
}
