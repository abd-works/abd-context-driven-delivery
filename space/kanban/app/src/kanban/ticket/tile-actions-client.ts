import { ACTION_STANDINGS, countOf, STEP_FAILED } from '../board/board-brand'
import type { BoardPage } from '../board/board-page'
import type { Tile } from '../board/board-store'
import type { TicketClient } from './ticket-client'
import { slugsOf } from './tile-client'
import { chipDoneCount, chipOfferedCount, chipsOf, chosenFormats } from './tile-formats'
import type { FormatChip } from './tile-formats'

const ACTIONS_WITH_FORMATS = ['generate', 'render']

const namedIn = (tile: Tile): string => slugsOf(tile.fidelities).join(' ')

export type ChipFace = FormatChip & { hint: string; isOn: boolean; isDone: boolean; count: string }
export type StepFace = { mark: string; color: string; hint: string; text: string }
export type TileBar = {
  chips: ChipFace[]
  isLocked: boolean
  runOff: boolean
  validateOff: boolean
  reviewOff: boolean
  validate: StepFace
  review: StepFace
  reportSlug: string | undefined
  hasViolations: boolean
}

// A tile can hold several fidelities: its link opens the report of the one left with violations, else the first report.
function reportSlugOf(ticket: TicketClient, tile: Tile): string | undefined {
  const reported = slugsOf(tile.fidelities).filter(slug => ticket.progressNamed(slug)?.report_file)
  return reported.find(slug => ticket.stateOf(slug).key === 'violations') ?? reported[0]
}

function chipFaceOf(tile: Tile, chip: FormatChip): ChipFace {
  const done = chipDoneCount(tile.files, tile.fidelities, chip)
  const offered = chipOfferedCount(tile.fidelities, chip)
  const isOn = tile.picked.includes(chip.label)
  const standing = done === 0 ? 'not done' : done === offered ? 'done' : `${done} of ${offered} done`
  const count = done > 0 && done < offered ? `${done} of ${offered}` : ''
  return { ...chip, isOn, isDone: done > 0, count, hint: `${chip.label}: ${standing}${isOn ? ', selected' : ''}` }
}

const stepFaceOf = (standing: string, name: string): StepFace => {
  const { mark, color, label } = ACTION_STANDINGS[standing]!
  return { mark, color, hint: `${name}: ${label}`, text: '' }
}

function validateFaceOf(ticket: TicketClient, tile: Tile): StepFace {
  const slugs = slugsOf(tile.fidelities)
  if (!slugs.some(slug => ticket.stateOf(slug).key === 'violations')) return stepFaceOf(ticket.standingOf(slugs, 'validate'), 'Validate')
  const count = ticket.violationCountOf(slugs)
  const text = count ? countOf(count, 'violation') : 'violations'
  return { mark: STEP_FAILED, color: 'var(--violations)', hint: text, text }
}

const allowsAll = (ticket: TicketClient, tile: Tile, action: string): boolean => tile.fidelities.length > 0 && tile.fidelities.every(fidelity => ticket.allows(fidelity.slug, action))

// What an open action bar offers, and what its controls send to the chat.
export class TileActionsClient {
  constructor(private readonly page: BoardPage) {}

  private get chat(): BoardPage['chat'] {
    return this.page.chat
  }

  private save(tile: Tile, change: Partial<Tile>): void {
    this.page.tiles.change(tile.ticket.name, tile.place, open => ({ ...open, ...change, isPinned: true }))
  }

  chooseAction(tile: Tile, action: string): void {
    this.save(tile, { action })
  }

  toggleFormat(tile: Tile, chip: string): void {
    this.save(tile, { picked: tile.picked.includes(chip) ? tile.picked.filter(entry => entry !== chip) : [...tile.picked, chip] })
  }

  private canRun(ticket: TicketClient, tile: Tile): boolean {
    if (ticket.isLocked || !this.chat.canSend || !tile.fidelities.length) return false
    if (!chosenFormats(tile.fidelities, tile.picked).length) return false
    return tile.action !== 'render' || chipsOf(tile.fidelities).some(chip => chipDoneCount(tile.files, tile.fidelities, chip) > 0)
  }

  // The ticket says when Validate and Review have something to look at: an action it recorded, or a declared file there.
  private hasSomethingToCheck(ticket: TicketClient, tile: Tile, action: string): boolean {
    return !ticket.isLocked && allowsAll(ticket, tile, action)
  }

  barOf(ticket: TicketClient, tile: Tile): TileBar {
    const validate = validateFaceOf(ticket, tile)
    return {
      chips: chipsOf(tile.fidelities).map(chip => chipFaceOf(tile, chip)),
      isLocked: ticket.isLocked,
      runOff: !this.canRun(ticket, tile),
      // Validate runs in the chat; a review is the person's own approval, so it needs no chat.
      validateOff: !this.chat.canSend || !this.hasSomethingToCheck(ticket, tile, 'validate'),
      reviewOff: !this.hasSomethingToCheck(ticket, tile, 'review'),
      validate,
      review: stepFaceOf(ticket.standingOf(slugsOf(tile.fidelities), 'review'), 'Review'),
      reportSlug: reportSlugOf(ticket, tile),
      hasViolations: validate.text !== '',
    }
  }

  // One command names every fidelity the bar acts on, so a stage's work stays a single turn.
  async run(tile: Tile): Promise<void> {
    if (!ACTIONS_WITH_FORMATS.includes(tile.action)) return this.sendFor(tile, `/actions-${tile.action} ${namedIn(tile)}`)
    const formats = chosenFormats(tile.fidelities, tile.picked)
    this.save(tile, { picked: [] })
    await this.sendFor(tile, `/actions-${tile.action} ${namedIn(tile)} format=${formats.join(',')}`)
  }

  validate(tile: Tile): Promise<void> {
    return this.sendFor(tile, `/actions-validate ${namedIn(tile)}`)
  }

  // The tile's ticket names its own session in the command, which goes to that ticket's chat.
  private sendFor(tile: Tile, command: string): Promise<void> {
    return tile.ticket.chat.command(tile.ticket.actionCommand(command))
  }

  // The ticket writes the review to its session log, and the board read after it shows the fidelity done.
  async review(tile: Tile): Promise<void> {
    await Promise.all(tile.fidelities.map(fidelity => tile.ticket.progressClient(fidelity.slug).finishReview()))
    await this.page.reader.refresh()
  }
}
