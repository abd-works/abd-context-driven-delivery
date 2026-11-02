import type { BoardApi } from '../board/board-api'
import { pathPart } from '../board/board-api'
import type { BoardStore } from '../board/board-store'
import type { Chat, ChatCommand } from './chat'

const SHOWN_COMMAND = 80

const shortened = (text: string): string => (text.length > SHOWN_COMMAND ? `${text.slice(0, SHOWN_COMMAND)}…` : text)

// The chat a person works in, reached through the cdd-board mod polling the server.
export class ChatClient {
  constructor(
    private readonly store: BoardStore,
    private readonly api: BoardApi,
  ) {}

  get canSend(): boolean {
    return this.store.state.targetChat !== null
  }

  private get target(): Chat | undefined {
    const { chats, targetChat } = this.store.state
    return chats.find(chat => chat.id === targetChat)
  }

  async refresh(): Promise<void> {
    const chats = await this.api.get<Chat[]>('/chats')
    if (!chats) return
    const { targetChat } = this.store.state
    const kept = chats.some(chat => chat.id === targetChat) ? targetChat : null
    this.store.change({ chats, targetChat: kept ?? (chats.length === 1 ? chats[0]!.id : null) })
  }

  choose(chat: string): void {
    this.store.change({ targetChat: chat || null })
  }

  // A prompt that starts with / is a command, which runs the skill.
  command(text: string): Promise<void> {
    return this.send('command', text, `Sent to the chat: ${shortened(text)}`)
  }

  // A fill waits at the server while a turn runs, so the person is told it has not reached the prompt yet.
  fill(text: string): Promise<void> {
    const wait = this.target?.isBusy ? ' It goes in when this turn ends.' : ''
    return this.send('fill', text, `Queued for the prompt, for you to review: ${shortened(text)}${wait}`)
  }

  private async send(kind: ChatCommand['kind'], text: string, sent: string): Promise<void> {
    const { targetChat } = this.store.state
    if (!targetChat) return
    if (await this.api.post(`/chats/${pathPart(targetChat)}/commands`, { kind, text })) this.store.toast(sent)
  }
}
