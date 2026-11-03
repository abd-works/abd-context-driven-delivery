import { ChatClientGenerated, type ChatData } from '@cdd/tools/chat/chat'

import type { BoardApi } from '../board/board-api'
import type { BoardStore } from '../board/board-store'

const SHOWN_COMMAND = 80

type CommandKind = 'submit' | 'fill' | 'command'

const shortened = (text: string): string => (text.length > SHOWN_COMMAND ? `${text.slice(0, SHOWN_COMMAND)}…` : text)

// The chat a person works in. Commands wait in the chat's own folder until its cdd-board mod checks in and takes them.
export class ChatClient {
  constructor(
    private readonly store: BoardStore,
    private readonly api: BoardApi,
  ) {}

  get canSend(): boolean {
    return this.store.state.targetChat !== null
  }

  private get target(): ChatData | undefined {
    const { chats, targetChat } = this.store.state
    return chats.find(chat => chat.id === targetChat)
  }

  // The chat a person picked while it is connected, else the first connected one, because with none chosen every
  // button that sends to a chat is off. The pick is remembered, so a chat that reconnects is chosen again.
  async refresh(): Promise<void> {
    const chats = await ChatClientGenerated.list(this.api)
    if (!chats) return
    const { pickedChat } = this.store.state
    const picked = chats.find(chat => chat.id === pickedChat) ?? chats[0]
    this.store.change({ chats, targetChat: picked?.id ?? null })
    await this.readMessages()
  }

  choose(chat: string): void {
    this.store.change({ pickedChat: chat || null, targetChat: chat || null })
    void this.readMessages()
  }

  // A message the chat took but did not show goes back in its queue, and the chat takes it again.
  async resend(message: string): Promise<void> {
    const { targetChat } = this.store.state
    if (!targetChat || !(await ChatClientGenerated.named(this.api, targetChat).resend(message))) return
    await this.readMessages()
  }

  async remove(message: string): Promise<void> {
    const { targetChat } = this.store.state
    if (!targetChat || !(await ChatClientGenerated.named(this.api, targetChat).remove(message))) return
    await this.readMessages()
  }

  toggleMessages(): void {
    this.store.change({ isMessagesOpen: !this.store.state.isMessagesOpen })
  }

  private async readMessages(): Promise<void> {
    const { targetChat } = this.store.state
    const messages = targetChat ? await ChatClientGenerated.named(this.api, targetChat).messages() : []
    if (messages) this.store.change({ messages })
  }

  // The chat's name, so the person knows which chat to look in.
  private get targetName(): string {
    return this.target?.name || this.store.state.targetChat || ''
  }

  // A prompt that starts with / is a command, which runs the skill. The whole command is named, because what is cut off
  // is often the session it ran on.
  command(text: string): Promise<void> {
    return this.send('command', text, `Sent to ${this.targetName}: ${text}`)
  }

  // A fill waits for the chat while a turn runs, so the person is told it has not reached the prompt yet.
  fill(text: string): Promise<void> {
    const wait = this.target?.is_busy ? ' It goes in when this turn ends.' : ''
    return this.send('fill', text, `Queued for the prompt of ${this.targetName}, for you to review: ${shortened(text)}${wait}`)
  }

  private async send(kind: CommandKind, text: string, sent: string): Promise<void> {
    const { targetChat } = this.store.state
    if (!targetChat) return
    if (!(await ChatClientGenerated.named(this.api, targetChat).send(kind, text))) return
    this.store.toast(sent)
    await this.readMessages()
  }
}
