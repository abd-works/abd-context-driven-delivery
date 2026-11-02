import type { Request } from 'express'
import { z } from 'zod'

import { HttpException } from '../../session-board/http-exception'
import type { Chat, ChatCommand } from './chat'

const CONFLICT = 409
const ChatAddress = z.object({ chat: z.string().min(1) })
const SentCommand = z.object({ kind: z.enum(['submit', 'fill', 'command']), text: z.string().min(1) })
const ChatPoll = z.object({ is_busy: z.boolean().default(false) })
// The chat-mod polls every second, so a chat silent for this long has gone.
const CHAT_GONE_MILLISECONDS = 5000

type ChatState = { isBusy: boolean; seen: number; waiting: ChatCommand[] }

// In memory on purpose: a chat registers itself again within a second of a restart, so nothing here needs to outlive the process.
export class ChatsNode {
  private readonly chats = new Map<string, ChatState>()

  constructor(private readonly now: () => number = Date.now) {}

  private stateOf(chat: string): ChatState {
    const state = this.chats.get(chat) ?? { isBusy: false, seen: 0, waiting: [] }
    this.chats.set(chat, state)
    return state
  }

  get connected(): Chat[] {
    return [...this.chats].filter(([, state]) => this.now() - state.seen < CHAT_GONE_MILLISECONDS).map(([id, state]) => ({ id, isBusy: state.isBusy }))
  }

  sendRequested(req: Request): { ok: true } {
    const { chat } = ChatAddress.parse(req.params)
    const command = SentCommand.parse(req.body)
    if (!this.connected.some(connected => connected.id === chat)) {
      throw new HttpException(CONFLICT, 'That chat is not connected: is the cdd-board mod loaded in it?')
    }
    this.stateOf(chat).waiting.push(command)
    return { ok: true }
  }

  nextRequested(req: Request): ChatCommand | null {
    return this.next(ChatAddress.parse(req.params).chat, ChatPoll.parse(req.body).is_busy)
  }

  // A fill during a running turn can report success and show nothing, so it waits here until the turn ends.
  // A submit and a command are the engine's to hold until idle, so they go at once.
  next(chat: string, isBusy: boolean): ChatCommand | null {
    const state = this.stateOf(chat)
    state.seen = this.now()
    state.isBusy = isBusy
    const ready = state.waiting.findIndex(command => command.kind !== 'fill' || !isBusy)
    return ready < 0 ? null : (state.waiting.splice(ready, 1)[0] ?? null)
  }
}
