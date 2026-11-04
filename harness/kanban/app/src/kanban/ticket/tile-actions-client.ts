import { TicketClientGenerated } from '@cdd/harness/kanban/ticket'

import { ACTION_STANDINGS, countOf, guidanceSlug, STEP_FAILED } from '../board/board-brand'
import type { BoardPage } from '../board/board-page'
import type { Tile } from '../board/board-store'
import type { ColumnClient } from '../board/column-client'
import type { TicketClient } from './ticket-client'
import { chipDoneCount, chipOfferedCount, chipsOf, chosenFormats } from './tile-formats'
import type { FormatChip } from './tile-formats'

const ACTIONS_WITH_FORMATS = ['generate', 'render']

const slugsOf = (tile: Tile): string => tile.slugs.map(guidanceSlug).join(' ')

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
  const reported = tile.slugs.filter(slug => ticket.reports[slug])
  return reported.find(slug => ticket.stateOf(slug).key === 'violations') ?? reported[0]
}

function chipFaceOf(stage: ColumnClient, tile: Tile, chip: FormatChip): ChipFace {
  const done = chipDoneCount(tile.files, tile.slugs, chip)
  const offered = chipOfferedCount(stage, tile.slugs, chip)
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
  if (!tile.slugs.some(slug => ticket.stateOf(slug).key === 'violations')) return stepFaceOf(ticket.standingOf(tile.slugs, 'validate'), 'Validate')
  const count = ticket.violationCountOf(tile.slugs)
  const text = count ? countOf(count, 'violation') : 'violations'
  return { mark: STEP_FAILED, color: 'var(--violations)', hint: text, text }
}

const allowsAll = (ticket: TicketClient, tile: Tile, action: string): boolean => tile.slugs.length > 0 && tile.slugs.every(slug => ticket.allows(slug, action))

const hasFiles = (tile: Tile): boolean => Object.values(tile.files).some(formats => Object.values(formats).some(entries => entries.some(entry => entry.exists)))

// What an open action bar offers, and what its controls send to the chat.
export class TileActionsClient {
  constructor(private readonly page: BoardPage) {}

  private get chat(): BoardPage['chat'] {
    return this.page.chat
  }

  private save(tile: Tile, change: Partial<Tile>): void {
    this.page.tiles.change(tile.ticket, tile.place, open => ({ ...open, ...change, isPinned: true }))
  }

  chooseAction(tile: Tile, action: string): void {
    this.save(tile, { action })
  }

  toggleFormat(tile: Tile, chip: string): void {
    this.save(tile, { picked: tile.picked.includes(chip) ? tile.picked.filter(entry => entry !== chip) : [...tile.picked, chip] })
  }

  private canRun(ticket: TicketClient, stage: ColumnClient, tile: Tile): boolean {
    if (ticket.isLocked || !this.chat.canSend || !tile.slugs.length) return false
    if (!chosenFormats(stage, tile.slugs, tile.picked).length) return false
    return tile.action !== 'render' || chipsOf(stage, tile.slugs).some(chip => chipDoneCount(tile.files, tile.slugs, chip) > 0)
  }

  // Validate and Review need something to look at: an action the ticket recorded, or files the bar found on disk.
  private hasSomethingToCheck(ticket: TicketClient, tile: Tile, action: string): boolean {
    return !ticket.isLocked && (allowsAll(ticket, tile, action) || hasFiles(tile))
  }

  barOf(ticket: TicketClient, stage: ColumnClient, tile: Tile): TileBar {
    const validate = validateFaceOf(ticket, tile)
    return {
      chips: chipsOf(stage, tile.slugs).map(chip => chipFaceOf(stage, tile, chip)),
      isLocked: ticket.isLocked,
      runOff: !this.canRun(ticket, stage, tile),
      // Validate runs in the chat; a review is the person's own approval, so it needs no chat.
      validateOff: !this.chat.canSend || !this.hasSomethingToCheck(ticket, tile, 'validate'),
      reviewOff: !this.hasSomethingToCheck(ticket, tile, 'review'),
      validate,
      review: stepFaceOf(ticket.standingOf(tile.slugs, 'review'), 'Review'),
      reportSlug: reportSlugOf(ticket, tile),
      hasViolations: validate.text !== '',
    }
  }

  async runCommandsOf(ticket: string, fidelities: string[], formats: string[]): Promise<void> {
    const commands = await TicketClientGenerated.named(this.page.api, ticket).generateCommands(fidelities, formats)
    for (const command of commands ?? []) await this.chat.command(command)
  }

  // One command names every fidelity the bar acts on, so a stage's work stays a single turn.
  async run(tile: Tile, stage: ColumnClient): Promise<void> {
    if (!ACTIONS_WITH_FORMATS.includes(tile.action)) return this.sendFor(tile, `/actions-${tile.action} ${slugsOf(tile)}`)
    const formats = chosenFormats(stage, tile.slugs, tile.picked)
    this.save(tile, { picked: [] })
    if (tile.action === 'generate') await this.runCommandsOf(tile.ticket, tile.slugs, formats)
    else await this.sendFor(tile, `/actions-render ${slugsOf(tile)} format=${formats.join(',')}`)
  }

  validate(tile: Tile): Promise<void> {
    return this.sendFor(tile, `/actions-validate ${slugsOf(tile)}`)
  }

  // The tile's ticket names its own session in the command.
  private sendFor(tile: Tile, command: string): Promise<void> {
    const ticket = this.page.board.tickets.find(shown => shown.name === tile.ticket)
    return this.chat.command(ticket ? ticket.actionCommand(command) : command)
  }

  // The ticket writes the review to its session log, and the board read after it shows the fidelity reviewed.
  async review(tile: Tile): Promise<void> {
    await TicketClientGenerated.named(this.page.api, tile.ticket).finishReview(tile.slugs)
    await this.page.reader.refresh()
  }
}
