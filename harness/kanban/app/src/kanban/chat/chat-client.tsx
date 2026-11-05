import { ChatClientGenerated, type ChatData } from '@cdd/tools/chat/chat'

import type { BoardApi } from '../board/board-api'
import type { BoardStore } from '../board/board-store'

const SHOWN_COMMAND = 80
// A ticket's new chat is not opened again for this long, while the person confirms it and it checks in.
const STARTING_CHAT_MILLISECONDS = 120_000
// The Claude app opens a new session on a folder from this link, with its prompt filled in for the person to send.
const NEW_CHAT_LINK = 'claude://code/new'

// A folder as the mod and as git each write it, so the two compare: one kind of slash, no trailing one, one case.
const folderKey = (folder: string): string => folder.replaceAll('\\', '/').replace(/\/+$/, '').toLowerCase()

// A chat works in a checkout from its root or from any folder inside it, since its working folder can move.
export const isWorkingIn = (chatFolder: string, checkout: string): boolean => {
  if (!chatFolder || !checkout) return false
  const [chat, root] = [folderKey(chatFolder), folderKey(checkout)]
  return chat === root || chat.startsWith(`${root}/`)
}

// The link that opens a ticket's new chat on its worktree. The link names no title, so its prompt asks for the ticket's.
export const newChatLink = (ticket: string, worktree: string): string => {
  const prompt = `Title this session "${ticket}". You are the chat of the session board's ticket ${ticket}; work on that ticket.`
  return `${NEW_CHAT_LINK}?folder=${encodeURIComponent(worktree)}&q=${encodeURIComponent(prompt)}`
}

type CommandKind = 'submit' | 'fill' | 'command'

const shortened = (text: string): string => (text.length > SHOWN_COMMAND ? `${text.slice(0, SHOWN_COMMAND)}…` : text)

// The chat a person works in. Commands wait in the chat's own folder until its cdd-board mod checks in and takes them.
export class ChatClient {
  constructor(
    private readonly store: BoardStore,
    private readonly api: BoardApi,
    private readonly openLink: (link: string) => void,
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

  // The connected chat working in folder or a folder inside it, such as a ticket's worktree.
  chatIn(folder: string): ChatData | undefined {
    return this.store.state.chats.find(chat => isWorkingIn(chat.folder, folder))
  }

  // A ticket's new chat opens in the Claude app on the ticket's worktree; the app asks the person to confirm the folder and
  // send. Until it checks in, clicking the ticket again opens no second one.
  startFor(ticket: string, worktree: string): void {
    const asked = this.store.state.startingChats[ticket]
    if (!worktree || (asked !== undefined && Date.now() - asked < STARTING_CHAT_MILLISECONDS)) return
    this.store.change({ startingChats: { ...this.store.state.startingChats, [ticket]: Date.now() } })
    this.openLink(newChatLink(ticket, worktree))
    this.store.toast(`Confirm the folder and send in the Claude app to start the chat of ${ticket}`)
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
  command(text: string, worktree = ''): Promise<void> {
    this.chooseChatIn(worktree)
    return this.send('command', text, `Sent to ${this.targetName}: ${text}`)
  }

  // A fill waits for the chat while a turn runs, so the person is told it has not reached the prompt yet.
  fill(text: string, worktree = ''): Promise<void> {
    this.chooseChatIn(worktree)
    const wait = this.target?.is_busy ? ' It goes in when this turn ends.' : ''
    return this.send('fill', text, `Queued for the prompt of ${this.targetName}, for you to review: ${shortened(text)}${wait}`)
  }

  // A ticket's command goes to the chat working in its worktree when one is connected, whichever chat was picked last.
  private chooseChatIn(worktree: string): void {
    const chat = this.chatIn(worktree)
    if (chat && chat.id !== this.store.state.targetChat) this.choose(chat.id)
  }

  private async send(kind: CommandKind, text: string, sent: string): Promise<void> {
    const { targetChat } = this.store.state
    if (!targetChat) return
    if (!(await ChatClientGenerated.named(this.api, targetChat).send(kind, text))) return
    this.store.toast(sent)
    await this.readMessages()
  }
}
