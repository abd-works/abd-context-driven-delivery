import type { Column, TicketFiles } from './board'
import { guidanceSlug } from './board'
import type { BoardApi } from './board-api'
import { pathPart } from './board-api'
import { ACTION_STANDINGS, countOf, practiceOf, STEP_FAILED } from './board-brand'
import type { BoardClient } from './board-client'
import type { BoardStore, Tile } from './board-store'
import type { ChatClient } from '../chat/chat-client'
import type { TicketClient } from './ticket-client'
import { chipDoneCount, chipOfferedCount, chipsOf, chosenFormats, defaultPicks } from './tile-formats'
import type { FormatChip } from './tile-formats'

// The opened card's bar over all its fidelities stays up while the tiles below it open and close, so it is kept apart.
export const CARD_MENU = 'menu'
const DEFAULT_ACTION = 'generate'
const ACTIONS_WITH_FORMATS = ['generate', 'render']
const HOVER_OPEN_MILLISECONDS = 500
const HOVER_CLOSE_MILLISECONDS = 250

export const cellPlace = (stage: string, slug: string): string => `cell-${stage}-${slug}`
export const headPlace = (stage: string): string => `head-${stage}`

const slugsOf = (tile: Tile): string => tile.slugs.map(guidanceSlug).join(' ')

export type ChipFace = FormatChip & { hint: string; isOn: boolean; isDone: boolean; count: string }
export type StepFace = { mark: string; color: string; hint: string; text: string }
export type TileBar = {
  chips: ChipFace[]
  isLocked: boolean
  runOff: boolean
  validateOff: boolean
  reviewOff: boolean
  generate: StepFace
  validate: StepFace
  review: StepFace
  reportSlug: string | undefined
  hasViolations: boolean
}

function chipFaceOf(stage: Column, tile: Tile, chip: FormatChip): ChipFace {
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

// Open action bars: which is open, what it offers, and what its controls send to the chat.
export class TileClient {
  private hoverOpenTimer: ReturnType<typeof setTimeout> | undefined
  private hoverCloseTimer: ReturnType<typeof setTimeout> | undefined
  private opening = 0

  constructor(
    private readonly store: BoardStore,
    private readonly api: BoardApi,
    private readonly chat: ChatClient,
    private readonly board: BoardClient,
  ) {}

  private readFiles(ticket: string, slugs: string[]): Promise<TicketFiles | null> {
    return this.api.post<TicketFiles>(`/tickets/${pathPart(ticket)}/files`, { fidelities: slugs })
  }

  private async started(ticket: string, stage: Column, place: string, slugs: string[], isPinned: boolean): Promise<Tile> {
    const files = (await this.readFiles(ticket, slugs)) ?? {}
    return { ticket, place, stage: stage.name, slugs, action: DEFAULT_ACTION, picked: defaultPicks(stage, slugs, files), isPinned, files }
  }

  // Only the latest open wins, so a slow read for a tile the pointer has left cannot replace the one under it.
  async open(ticket: string, stage: Column, place: string, slugs: string[], isPinned: boolean): Promise<void> {
    const order = ++this.opening
    const tile = await this.started(ticket, stage, place, slugs, isPinned)
    if (order === this.opening) this.store.change({ tile })
  }

  isOpen(ticket: string, place: string): boolean {
    const { tile } = this.store.state
    return tile?.ticket === ticket && tile.place === place
  }

  close(): void {
    this.store.change({ tile: null })
  }

  pin(): void {
    this.store.change(state => ({ tile: state.tile ? { ...state.tile, isPinned: true } : null }))
  }

  // The first press on a tile a hover opened keeps it open; the next closes it.
  async toggle(ticket: TicketClient, stage: Column, place: string, slugs: string[]): Promise<void> {
    clearTimeout(this.hoverOpenTimer)
    ticket.select()
    if (!this.isOpen(ticket.name, place)) return this.open(ticket.name, stage, place, slugs, true)
    if (this.store.state.tile?.isPinned) this.close()
    else this.pin()
  }

  // A hover only looks, so it leaves a bar a person pressed open.
  hoverIn(ticket: string, stage: Column, place: string, slugs: string[]): void {
    clearTimeout(this.hoverOpenTimer)
    clearTimeout(this.hoverCloseTimer)
    if (this.isOpen(ticket, place) || this.store.state.tile?.isPinned) return
    this.hoverOpenTimer = setTimeout(() => void this.open(ticket, stage, place, slugs, false), HOVER_OPEN_MILLISECONDS)
  }

  hoverOut(place: string): void {
    clearTimeout(this.hoverOpenTimer)
    clearTimeout(this.hoverCloseTimer)
    this.hoverCloseTimer = setTimeout(() => {
      const { tile } = this.store.state
      if (tile?.place === place && !tile.isPinned) this.close()
    }, HOVER_CLOSE_MILLISECONDS)
  }

  // A card opens with its action bar ready, over all its fidelities, so generating needs no hover first.
  async toggleCard(ticket: TicketClient, stage: Column): Promise<void> {
    ticket.select()
    if (this.store.state.openCard === ticket.name) return this.closeCard()
    this.store.change({ openCard: ticket.name, cardMenu: null, tile: null })
    await this.openCardBar(ticket, stage)
  }

  private closeCard(): void {
    this.store.change(state => ({ openCard: null, cardMenu: null, tile: state.tile?.ticket === state.openCard ? null : state.tile }))
  }

  private async openCardBar(ticket: TicketClient, stage: Column): Promise<void> {
    const slugs = ticket.enabledSlugs(stage)
    if (slugs.length === 1) return this.open(ticket.name, stage, cellPlace(stage.name, slugs[0]!), slugs, true)
    if (!slugs.length) return
    const cardMenu = await this.started(ticket.name, stage, CARD_MENU, slugs, true)
    if (this.store.state.openCard === ticket.name) this.store.change({ cardMenu })
  }

  // A press on a segment opens the card on that fidelity.
  async openSegment(ticket: TicketClient, stage: Column, slug: string): Promise<void> {
    if (this.store.state.openCard !== ticket.name) await this.toggleCard(ticket, stage)
    await this.open(ticket.name, stage, cellPlace(stage.name, slug), [slug], true)
  }

  private save(tile: Tile, change: Partial<Tile>): void {
    if (tile.place === CARD_MENU) this.store.change(state => ({ cardMenu: state.cardMenu ? { ...state.cardMenu, ...change } : null }))
    else this.store.change(state => ({ tile: state.tile ? { ...state.tile, ...change, isPinned: true } : null }))
  }

  chooseAction(tile: Tile, action: string): void {
    this.save(tile, { action })
  }

  toggleFormat(tile: Tile, chip: string): void {
    this.save(tile, { picked: tile.picked.includes(chip) ? tile.picked.filter(entry => entry !== chip) : [...tile.picked, chip] })
  }

  private canRun(ticket: TicketClient, stage: Column, tile: Tile): boolean {
    if (ticket.isLocked || !this.chat.canSend || !tile.slugs.length) return false
    if (!chosenFormats(stage, tile.slugs, tile.picked).length) return false
    return tile.action !== 'render' || chipsOf(stage, tile.slugs).some(chip => chipDoneCount(tile.files, tile.slugs, chip) > 0)
  }

  private canSendFor(ticket: TicketClient, tile: Tile, action: string): boolean {
    return !ticket.isLocked && this.chat.canSend && allowsAll(ticket, tile, action)
  }

  barOf(ticket: TicketClient, stage: Column, tile: Tile): TileBar {
    const validate = validateFaceOf(ticket, tile)
    return {
      chips: chipsOf(stage, tile.slugs).map(chip => chipFaceOf(stage, tile, chip)),
      isLocked: ticket.isLocked,
      runOff: !this.canRun(ticket, stage, tile),
      validateOff: !this.canSendFor(ticket, tile, 'validate'),
      reviewOff: !this.canSendFor(ticket, tile, 'review'),
      generate: stepFaceOf(ticket.standingOf(tile.slugs, 'generate'), 'Generate'),
      validate,
      review: stepFaceOf(ticket.standingOf(tile.slugs, 'review'), 'Review'),
      reportSlug: tile.slugs.find(slug => ticket.reports[slug]),
      hasViolations: validate.text !== '',
    }
  }

  async runCommandsOf(ticket: string, fidelities: string[], formats: string[]): Promise<void> {
    const commands = await this.api.post<string[]>(`/tickets/${pathPart(ticket)}/generate-commands`, { fidelities, formats })
    for (const command of commands ?? []) await this.chat.command(command)
  }

  // One command names every fidelity the bar acts on, so a stage's work stays a single turn.
  async run(tile: Tile, stage: Column): Promise<void> {
    if (!ACTIONS_WITH_FORMATS.includes(tile.action)) return this.chat.command(`/actions-${tile.action} ${slugsOf(tile)}`)
    const formats = chosenFormats(stage, tile.slugs, tile.picked)
    this.save(tile, { picked: [] })
    if (tile.action === 'generate') await this.runCommandsOf(tile.ticket, tile.slugs, formats)
    else await this.chat.command(`/actions-render ${slugsOf(tile)} format=${formats.join(',')}`)
  }

  validate(tile: Tile): Promise<void> {
    return this.chat.command(`/actions-validate ${slugsOf(tile)}`)
  }

  review(tile: Tile): Promise<void> {
    return this.chat.command(`/actions:review:review ${slugsOf(tile)}`)
  }

  // What a bar shows was generated can change under it, so it is read again with the board.
  async reload(): Promise<void> {
    const { tile, cardMenu } = this.store.state
    if (tile) await this.reloadFiles(tile, files => this.store.change(state => ({ tile: state.tile?.place === tile.place ? { ...state.tile, files } : state.tile })))
    if (cardMenu) await this.reloadFiles(cardMenu, files => this.store.change(state => ({ cardMenu: state.cardMenu ? { ...state.cardMenu, files } : null })))
  }

  private async reloadFiles(tile: Tile, keep: (files: TicketFiles) => void): Promise<void> {
    const files = await this.readFiles(tile.ticket, tile.slugs)
    if (files) keep(files)
  }

  // A ticket's address changes with its column, so the selection and an open bar go with it: the bar to the tile the
  // ticket works on next, and an opened card's bar to the fidelities of its new stage.
  async follow(moved: TicketClient): Promise<void> {
    moved.select()
    const stage = this.board.stageOf(moved)
    if (!stage) return
    const { tile, cardMenu } = this.store.state
    if (tile?.ticket === moved.name) await this.followBar(moved, stage)
    if (cardMenu?.ticket === moved.name) await this.openCardBar(moved, stage)
  }

  private async followBar(moved: TicketClient, stage: Column): Promise<void> {
    const slugs = moved.enabledSlugs(stage)
    const slug = slugs.find(entry => moved.stateOf(entry).key !== 'done') ?? slugs[0]
    if (slug) await this.open(moved.name, stage, cellPlace(stage.name, slug), [slug], true)
    else this.close()
  }

  releaseTicket(ticket: string): void {
    this.store.change(state => ({
      openCard: state.openCard === ticket ? null : state.openCard,
      cardMenu: state.cardMenu?.ticket === ticket ? null : state.cardMenu,
      tile: state.tile?.ticket === ticket ? null : state.tile,
    }))
  }

  // A practice turned off has no tile to act on, so an open bar lets go of it.
  dropPractice(ticket: string, practice: string): void {
    const remaining = (tile: Tile | null): Tile | null => {
      if (tile?.ticket !== ticket) return tile
      const slugs = tile.slugs.filter(slug => practiceOf(slug)?.key !== practice)
      return slugs.length ? { ...tile, slugs } : null
    }
    this.store.change(state => ({ tile: remaining(state.tile), cardMenu: remaining(state.cardMenu) }))
  }
}
