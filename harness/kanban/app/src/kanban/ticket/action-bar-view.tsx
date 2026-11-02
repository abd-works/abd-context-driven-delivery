import { TILE_ACTIONS } from '../board/board-brand'
import { useBoard } from '../board/board-context'
import type { Tile } from '../board/board-store'
import type { ColumnClient } from '../board/column-client'
import { FormatIcon } from '../board/icons'
import type { TicketClient } from './ticket-client'
import type { ChipFace, StepFace, TileBar } from './tile-actions-client'

function StepMarkView({ step }: { step: StepFace }) {
  return (
    <span className="step-mark" role="img" aria-label={step.hint} title={step.hint} style={{ color: step.color }}>
      {step.mark}
    </span>
  )
}

function chipLook({ isOn, isDone }: ChipFace) {
  if (isOn) return { color: 'var(--on-accent)', borderColor: 'var(--accent)', background: 'var(--accent)' }
  if (isDone) return { color: 'var(--reviewed)', borderColor: 'var(--reviewed)', background: 'transparent' }
  return { color: 'var(--muted)', borderColor: 'var(--border)', background: 'transparent' }
}

function FormatChipView({ tile, chip, isOff }: { tile: Tile; chip: ChipFace; isOff: boolean }) {
  const { page } = useBoard()
  return (
    <button className="format-icon" disabled={isOff} title={chip.hint} aria-label={chip.hint} aria-pressed={chip.isOn} style={chipLook(chip)} onClick={() => page.tileActions.toggleFormat(tile, chip.label)}>
      <FormatIcon label={chip.label} />
      {chip.count ? <span className="format-count">{chip.count}</span> : null}
    </button>
  )
}

function ActionChoiceView({ tile, isOff }: { tile: Tile; isOff: boolean }) {
  const { page } = useBoard()
  return (
    <select className="step-control action-choice" aria-label="Action" disabled={isOff} value={tile.action} onChange={event => page.tileActions.chooseAction(tile, event.target.value)}>
      {TILE_ACTIONS.map(action => (
        <option key={action} value={action}>
          {action}
        </option>
      ))}
    </select>
  )
}

function RunLineView({ tile, stage, bar }: { tile: Tile; stage: ColumnClient; bar: TileBar }) {
  const { page } = useBoard()
  return (
    <div className="bar-line">
      <ActionChoiceView tile={tile} isOff={bar.isLocked} />
      {bar.chips.map(chip => (
        <FormatChipView key={chip.label} tile={tile} chip={chip} isOff={bar.isLocked} />
      ))}
      <span className="bar-run">
        <StepMarkView step={bar.generate} />
        <button className="action primary step-control small" disabled={bar.runOff} onClick={() => void page.tileActions.run(tile, stage)}>
          Run
        </button>
      </span>
    </div>
  )
}

function ValidateLineView({ ticket, tile, bar }: { ticket: TicketClient; tile: Tile; bar: TileBar }) {
  const { page } = useBoard()
  const { reportSlug } = bar
  return (
    <div className="bar-line wide-gap">
      <button className="action step-control small" disabled={bar.validateOff} onClick={() => void page.tileActions.validate(tile)}>
        validate
      </button>
      <StepMarkView step={bar.validate} />
      {bar.validate.text ? <span className="step-text">{bar.validate.text}</span> : null}
      {reportSlug ? (
        <button className={bar.hasViolations ? 'violations-link' : 'report-link'} onClick={() => void page.panels.openReport(ticket.name, reportSlug)}>
          report
        </button>
      ) : null}
    </div>
  )
}

function ReviewLineView({ ticket, tile, bar, hasFileLinks }: { ticket: TicketClient; tile: Tile; bar: TileBar; hasFileLinks: boolean }) {
  const { page } = useBoard()
  return (
    <div className="bar-line wide-gap">
      <button className="action step-control small" disabled={bar.reviewOff} onClick={() => void page.tileActions.review(tile)}>
        review
      </button>
      <StepMarkView step={bar.review} />
      {hasFileLinks ? (
        <span className="bar-files">
          {['list', 'folder', 'files'].map(mode => (
            <button key={mode} className="extra-action" onClick={() => void page.files.openFiles(ticket.name, tile.slugs, mode)}>
              {mode}
            </button>
          ))}
        </span>
      ) : null}
    </div>
  )
}

type ActionBarProps = { ticket: TicketClient; stage: ColumnClient; tile: Tile; hasFileLinks: boolean; onMouseEnter?: () => void; onMouseLeave?: () => void }

// What a person does on an open tile: pick an action and formats, run it, validate, review, and look at the files.
export function ActionBarView({ ticket, stage, tile, hasFileLinks, onMouseEnter, onMouseLeave }: ActionBarProps) {
  const { page } = useBoard()
  const bar = page.tileActions.barOf(ticket, stage, tile)
  return (
    <div className="expansion" data-bar={tile.place} onClick={() => page.tiles.pin()} onMouseEnter={onMouseEnter} onMouseLeave={onMouseLeave}>
      <RunLineView tile={tile} stage={stage} bar={bar} />
      <ValidateLineView ticket={ticket} tile={tile} bar={bar} />
      <ReviewLineView ticket={ticket} tile={tile} bar={bar} hasFileLinks={hasFileLinks} />
    </div>
  )
}
