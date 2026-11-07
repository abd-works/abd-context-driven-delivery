import { ACTION_STANDINGS, countOf, STEP_FAILED } from '../board/board-brand'
import type { BoardPage } from '../board/board-page'
import type { Tile } from '../board/board-store'
import type { FidelityProgressClient } from './fidelity-progress-client'
import type { TicketClient } from './ticket-client'
import { slugsOf } from './tile-client'
import { chipDoneCount, chipOfferedCount, chipsOf, chosenFormats } from './tile-formats'
import type { FormatChip } from './tile-formats'

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
  report: FidelityProgressClient | undefined
  hasViolations: boolean
}

// A tile can hold several fidelities: its link opens the report of the one left with violations, else the first report.
function reportOf(progress: FidelityProgressClient[]): FidelityProgressClient | undefined {
  const reported = progress.filter(entry => entry.reportFile)
  return reported.find(entry => entry.state === 'violations') ?? reported[0]
}

// How far one action has got across a tile's fidelities: done only when it is done on all of them.
function standingOf(progress: FidelityProgressClient[], action: 'validate' | 'review'): string {
  const states = progress.map(entry => entry.actions[action])
  if (states.length && states.every(state => state === 'done')) return 'done'
  return states.some(state => state !== 'to_do') ? 'in_progress' : 'to_do'
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

function validateFaceOf(progress: FidelityProgressClient[]): StepFace {
  if (!progress.some(entry => entry.state === 'violations')) return stepFaceOf(standingOf(progress, 'validate'), 'Validate')
  const count = progress.reduce((total, entry) => total + entry.violationCount, 0)
  const text = count ? countOf(count, 'violation') : 'violations'
  return { mark: STEP_FAILED, color: 'var(--violations)', hint: text, text }
}

const allowsAll = (progress: FidelityProgressClient[], action: string): boolean => progress.length > 0 && progress.every(entry => entry.allows(action))

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
  private hasSomethingToCheck(ticket: TicketClient, progress: FidelityProgressClient[], action: string): boolean {
    return !ticket.isLocked && allowsAll(progress, action)
  }

  // ticket is the tile's ticket as the board shows it now, which holds the fidelities' latest progress.
  barOf(ticket: TicketClient, tile: Tile): TileBar {
    const progress = ticket.progressOn(tile.fidelities)
    const validate = validateFaceOf(progress)
    return {
      chips: chipsOf(tile.fidelities).map(chip => chipFaceOf(tile, chip)),
      isLocked: ticket.isLocked,
      runOff: !this.canRun(ticket, tile),
      // Validate runs in the chat; a review is the person's own approval, so it needs no chat.
      validateOff: !this.chat.canSend || !this.hasSomethingToCheck(ticket, progress, 'validate'),
      reviewOff: !this.hasSomethingToCheck(ticket, progress, 'review'),
      validate,
      review: stepFaceOf(standingOf(progress, 'review'), 'Review'),
      report: reportOf(progress),
      hasViolations: validate.text !== '',
    }
  }

  // One command names every fidelity the bar acts on, so a stage's work stays a single turn.
  async run(tile: Tile): Promise<void> {
    // The stage says which of its actions take the formats chosen; every other one writes or reads files without one.
    if (!tile.stage.actionsWithFormats.includes(tile.action)) return this.sendFor(tile, `/actions-${tile.action} ${namedIn(tile)}`)
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
    await Promise.all(tile.ticket.progressOn(tile.fidelities).map(progress => progress.finishReview()))
    await this.page.reader.refresh()
  }
}
