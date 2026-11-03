import type { ReactNode } from 'react'

import { STAGE_SCOPES } from './board-brand'

function ScopeView({ stage }: { stage: string }) {
  const scope = STAGE_SCOPES[stage]
  if (!scope) return null
  return (
    <span className="scope-wrap" tabIndex={0} aria-label={`${scope.name}. ${scope.reach}. ${scope.covers}`}>
      <span className="scope-shape" style={{ width: scope.width, height: scope.height }} />
      <span className="scope-tip" role="tooltip">
        <span className="scope-tip-name">{scope.name}</span>
        <span className="scope-tip-line scope-tip-reach">{scope.reach}</span>
        <span className="scope-tip-line">{scope.covers}</span>
      </span>
    </span>
  )
}

type StageHeadProps = { stage: string; isOverLimit?: boolean; onMouseEnter?: () => void; onMouseLeave?: () => void; children: ReactNode }

// The raised head a stage has on the board and in the details: its scope, its name, and what the place adds at the end.
export function StageHeadView({ stage, isOverLimit = false, onMouseEnter, onMouseLeave, children }: StageHeadProps) {
  return (
    <div className={isOverLimit ? 'stage-head is-over-limit' : 'stage-head'} onMouseEnter={onMouseEnter} onMouseLeave={onMouseLeave}>
      <ScopeView stage={stage} />
      {/* Plain text: a link to an example of a stage read as a link to this ticket's own work. */}
      <span className="stage-title">{stage}</span>
      {children}
    </div>
  )
}
