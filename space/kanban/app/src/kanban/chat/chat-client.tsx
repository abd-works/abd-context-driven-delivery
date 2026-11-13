import { ChatClientGenerated, type ChatData } from '@cdd/harness/chat/chat'

import type { BoardApi } from '../board/board-api'
import type { BoardStore } from '../shared/board-store'

const SHOWN_COMMAND = 80
// A ticket's new chat is not opened again for this long, while the person confirms it and it checks in.
const STARTING_CHAT_MILLISECONDS = 120_000

// The prompt a ticket's new chat opens with. The Claude app gives a new chat no title, so the prompt asks for the ticket's.
const newChatPrompt = (ticket: string): string => `Title this session "${ticket}". You are the chat of the session board's ticket ${ticket}; work on that ticket. First call sessions.switch with name ${ticket}, so every tool works on its session, then read the session's latest handoff.`

type CommandKind = 'submit' | 'fill' | 'command'

const shortened = (text: string): string => (text.length > SHOWN_COMMAND ? `${text.slice(0, SHOWN_COMMAND)}…` : text)

// The chat a person works in. Commands wait in the chat's own folder until its cdd-board mod checks in and takes them.
export class ChatClient {
  constructor(
    private readonly store: BoardStore,
    private readonly api: BoardApi,
  ) {}

  // A chat is connected to send to; which one is decided per send: the ticket's own, else the one a person picked.
  get canSend(): boolean {
    return this.store.state.chats.length > 0
  }

  private get target(): ChatData | undefined {
    const { chats, targetChat } = this.store.state
    return chats.find(chat => chat.id === targetChat)
  }

  // The chat a person picked while it is connected, and none otherwise: the list reorders as chats work, so its first
  // chat is whichever was busy last. The pick is remembered, so a chat that reconnects is chosen again.
  async refresh(): Promise<void> {
    const chats = await ChatClientGenerated.list(this.api)
    if (!chats) return
    const { pickedChat } = this.store.state
    const picked = chats.find(chat => chat.id === pickedChat)
    this.store.change({ chats, targetChat: picked?.id ?? null })
    await this.readMessages()
  }

  // A connected chat by its id, as Python names the chat working on a ticket.
  connected(chat: string): ChatData | undefined {
    return this.store.state.chats.find(entry => entry.id === chat)
  }

  // Opening a ticket's worktree and then its chat in the Claude app takes a while, so the click shows at once that the chat
  // is on its way. Until it checks in, clicking the ticket again opens no second one.
  beginOpening(ticket: string): boolean {
    if (this.isOpeningFor(ticket)) return false
    this.store.change({ startingChats: { ...this.store.state.startingChats, [ticket]: Date.now() } })
    this.store.toast(`Opening the chat of ${ticket}…`)
    return true
  }

  // Until the ticket's chat checks in, which the ticket then names, it is on its way.
  isOpeningFor(ticket: string): boolean {
    const asked = this.store.state.startingChats[ticket]
    return asked !== undefined && Date.now() - asked < STARTING_CHAT_MILLISECONDS
  }

  // A ticket's new chat opens in the Claude app on the ticket's worktree, through Python's chat.open; the app asks the
  // person to confirm the folder and send.
  async startFor(ticket: string, worktree: string): Promise<void> {
    if (!worktree) {
      const { [ticket]: _given, ...starting } = this.store.state.startingChats
      this.store.change({ startingChats: starting })
      return
    }
    if (await ChatClientGenerated.open(this.api, worktree, newChatPrompt(ticket))) this.store.toast(`Confirm the folder and send in the Claude app to start the chat of ${ticket}`)
  }

  get hasPicked(): boolean {
    return this.store.state.targetChat !== null
  }

  ask(question: string): void {
    this.store.toast(question)
  }

  choose(chat: string): void {
    this.store.change({ pickedChat: chat || null, targetChat: chat || null })
    void this.readMessages()
  }

  // The chat a person has just assigned to each ticket, until a board read names it as the ticket's chat. A read can
  // take longer than the person waits before pressing the ticket, and one started before the assignment still names
  // the chat from before it, so until a read catches up the assignment is the ticket's chat.
  private readonly assigning = new Map<string, string>()

  assign(ticket: string, chat: string): void {
    if (chat) this.assigning.set(ticket, chat)
    else this.assigning.delete(ticket)
  }

  // The id of ticket's chat: the one just assigned while board reads still name another, else the one the read names.
  chatOf(ticket: string, read: string): string {
    const assigned = this.assigning.get(ticket)
    if (assigned === undefined) return read
    if (assigned === read) this.assigning.delete(ticket)
    return assigned
  }

  // A message the chat took but did not show goes back in its queue, and the chat takes it again.
  resend(message: string): Promise<void> {
    return this.actOnTarget(chat => chat.resend(message))
  }

  remove(message: string): Promise<void> {
    return this.actOnTarget(chat => chat.remove(message))
  }

  toggleMessages(): void {
    this.store.change({ isMessagesOpen: !this.store.state.isMessagesOpen })
  }

  // The target chat's client, made once for each chat the person targets rather than on every call to it.
  private held: { chat: string; client: ChatClientGenerated } | null = null

  private get targetClient(): ChatClientGenerated | null {
    const { targetChat } = this.store.state
    if (!targetChat) return null
    if (this.held?.chat !== targetChat) this.held = { chat: targetChat, client: ChatClientGenerated.named(this.api, targetChat) }
    return this.held.client
  }

  // Act on the target chat's messages, then read them again to show what the act changed; nothing with no target.
  private async actOnTarget(act: (chat: ChatClientGenerated) => Promise<unknown>): Promise<void> {
    const chat = this.targetClient
    if (!chat || !(await act(chat))) return
    await this.readMessages()
  }

  private async readMessages(): Promise<void> {
    const chat = this.targetClient
    const messages = chat ? await chat.messages() : []
    if (messages) this.store.change({ messages })
  }

  // The chat's name, so the person knows which chat to look in.
  private get targetName(): string {
    return this.target?.name || this.store.state.targetChat || ''
  }

  // A prompt that starts with / is a command, which runs the skill. The whole command is named, because what is cut off
  // is often the session it ran on. Given a chat, such as a ticket's own, it goes there, whichever chat was picked last.
  command(text: string, chat?: ChatData): Promise<void> {
    this.chooseChat(chat)
    return this.send('command', text, `Sent to ${this.targetName}: ${text}`)
  }

  // A fill waits for the chat while a turn runs, so the person is told it has not reached the prompt yet.
  fill(text: string, chat?: ChatData): Promise<void> {
    this.chooseChat(chat)
    const wait = this.target?.is_busy ? ' It goes in when this turn ends.' : ''
    return this.send('fill', text, `Queued for the prompt of ${this.targetName}, for you to review: ${shortened(text)}${wait}`)
  }

  private chooseChat(chat: ChatData | undefined): void {
    if (chat && chat.id !== this.store.state.targetChat) this.choose(chat.id)
  }

  private async send(kind: CommandKind, text: string, sent: string): Promise<void> {
    if (!this.store.state.targetChat) {
      if (this.canSend) this.store.toast('Pick the chat to send to in the chat list first.')
      return
    }
    await this.actOnTarget(async chat => {
      const isSent = await chat.send(kind, text)
      if (isSent) this.store.toast(sent)
      return isSent
    })
  }
}

// One ticket's chat, the connected chat Python names as its chat: the one a person assigned to it, else the one named
// after it, else the one working in its worktree. The ticket owns it, so whatever the board sends
// for the ticket goes to that chat without a caller finding it again.
export class TicketChat {
  constructor(
    private readonly chats: ChatClient,
    private readonly ticket: string,
    private readonly working: { id: string } | null,
  ) {}

  get found(): ChatData | undefined {
    const chat = this.chats.chatOf(this.ticket, this.working?.id ?? '')
    return chat ? this.chats.connected(chat) : undefined
  }

  get isOpening(): boolean {
    return !this.found && this.chats.isOpeningFor(this.ticket)
  }

  // A ticket's commands go to its own chat, else to the chat a person picked; with neither, the person is asked for one
  // rather than the command reaching an unrelated chat.
  command(text: string): Promise<void> {
    if (this.isWithoutChat) return this.askForChat()
    return this.chats.command(text, this.found)
  }

  fill(text: string): Promise<void> {
    if (this.isWithoutChat) return this.askForChat()
    return this.chats.fill(text, this.found)
  }

  private get isWithoutChat(): boolean {
    return !this.found && !this.chats.hasPicked
  }

  private async askForChat(): Promise<void> {
    this.chats.ask(`No chat works on ${this.ticket} yet: open its chat from its card, or pick one in the chat list.`)
  }

  beginOpening(): boolean {
    return this.chats.beginOpening(this.ticket)
  }

  // The new chat opens on the worktree given, which can have been opened only now.
  start(worktree: string): Promise<void> {
    return this.chats.startFor(this.ticket, worktree)
  }
}
