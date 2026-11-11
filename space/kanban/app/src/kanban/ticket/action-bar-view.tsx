import { useBoard } from '../shared/board-context'
import type { Tile } from '../shared/board-store'
import { FormatIcon } from '../shared/icons'
import { FileViewsView } from './file-views-view'
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
  if (isDone) return { color: 'var(--done)', borderColor: 'var(--done)', background: 'transparent' }
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

// The stage the bar is on says which actions write a fidelity's files.
function ActionChoiceView({ tile, isOff }: { tile: Tile; isOff: boolean }) {
  const { page } = useBoard()
  const actions = tile.stage.producingActions
  return (
    <select className="step-control action-choice" aria-label="Action" disabled={isOff} value={tile.action} onChange={event => page.tileActions.chooseAction(tile, event.target.value)}>
      {actions.map(action => (
        <option key={action} value={action}>
          {action}
        </option>
      ))}
    </select>
  )
}

function RunLineView({ tile, bar }: { tile: Tile; bar: TileBar }) {
  const { page } = useBoard()
  return (
    <div className="bar-line">
      <ActionChoiceView tile={tile} isOff={bar.isLocked} />
      {bar.chips.map(chip => (
        <FormatChipView key={chip.label} tile={tile} chip={chip} isOff={bar.isLocked} />
      ))}
      <span className="bar-run">
        <button className="action primary step-control small" disabled={bar.runOff} onClick={() => void page.tileActions.run(tile)}>
          Run
        </button>
      </span>
    </div>
  )
}

function ValidateLineView({ ticket, tile, bar }: { ticket: TicketClient; tile: Tile; bar: TileBar }) {
  const { page } = useBoard()
  const { report } = bar
  return (
    <div className="bar-line wide-gap">
      <button className="action step-control small" disabled={bar.validateOff} onClick={() => void page.tileActions.validate(tile)}>
        validate
      </button>
      <StepMarkView step={bar.validate} />
      {report ? (
        <button className={bar.hasViolations ? 'violations-link' : 'report-link'} onClick={() => void page.panels.openReport(ticket, report)}>
          {bar.hasViolations ? `${bar.validate.text} found` : 'report'}
        </button>
      ) : bar.validate.text ? (
        <span className="step-text">{bar.validate.text}</span>
      ) : null}
    </div>
  )
}

type ActionBarProps = { ticket: TicketClient; tile: Tile; onMouseEnter?: () => void; onMouseLeave?: () => void }

// What a person does on an open tile: look at its files, pick an action and formats, run it, and validate.
export function ActionBarView({ ticket, tile, onMouseEnter, onMouseLeave }: ActionBarProps) {
  const { page } = useBoard()
  const bar = page.tileActions.barOf(ticket, tile)
  return (
    <div className="expansion" data-bar={tile.place} onClick={() => page.tiles.pin(tile.ticket.name, tile.place)} onMouseEnter={onMouseEnter} onMouseLeave={onMouseLeave}>
      <div className="bar-line bar-files">
        <FileViewsView ticket={ticket} progress={ticket.progressOn(tile.fidelities)} />
      </div>
      <RunLineView tile={tile} bar={bar} />
      <ValidateLineView ticket={ticket} tile={tile} bar={bar} />
    </div>
  )
}
