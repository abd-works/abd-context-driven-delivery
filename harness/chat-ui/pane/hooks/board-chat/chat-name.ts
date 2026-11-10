import type { EngineInterface } from 'claude-code'

// The name a person reads for this chat in the board's chat picker.
const NAME_CHARACTERS = 48
// A compacted chat opens with its summary, not with anything the person typed, so that message names nothing.
const SUMMARY_OPENINGS = ['This session is being continued', 'The summarized conversation']

let chatName = ''

// What a person typed, without the notices the app wraps in tags, inside and all.
const typedText = (text: string): string =>
  text
    .replace(/<([a-z][\w-]*)[^>]*>[\s\S]*?<\/\1>/gi, ' ')
    .replace(/<[^>]*>/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()

// A mod cannot read the title the app shows for a chat, so the board names it by its folder and the first thing the
// person typed. The board keeps sending to the chat's id; the name is only what a person reads in its picker.
export async function readName($: EngineInterface): Promise<void> {
  const folder = (await $.session.root()).split(/[\\/]/).filter(Boolean).at(-1) ?? ''
  const typed = (await $.session.messages()).filter(message => message.role === 'user').map(message => typedText(message.text))
  const opening = typed.find(text => text && !SUMMARY_OPENINGS.some(summary => text.startsWith(summary))) ?? ''
  const words = opening.length > NAME_CHARACTERS ? `${opening.slice(0, NAME_CHARACTERS)}…` : opening
  chatName = [folder, words].filter(Boolean).join(' · ')
}

export function currentChatName(): string {
  return chatName
}
