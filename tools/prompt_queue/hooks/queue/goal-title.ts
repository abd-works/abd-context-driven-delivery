// How Claude Code hands the mod a paste: the pasted text inside <pasted_content id="..."> tags, the closing tag
// sometimes missing when the paste runs to the end of the message.
const PASTED = /<pasted_content\b[^>]*>([\s\S]*?)(?:<\/pasted_content>|$)/gi
const STRAY_TAG = /<\/?pasted_content\b[^>]*>/gi
// What the Claude app puts before a message sent while a board viewer is open: the viewer's live state, written by the
// viewer's page, never by the person, so no title is made from it.
const VIEWER_STATE = /<artifact-view-context\b[^>]*>[\s\S]*?(?:<\/artifact-view-context>|$)/gi
// A markdown line's own marks, so a heading or a list item reads as its words.
const LINE_MARKS = /^\s*(?:#+|[-*>]|\d+[.)])\s+/
// The end of a message's first sentence.
const SENTENCE_END = /^(.+?[.!?])(?:\s|$)/
// How long a goal's title may be, enough to tell goals apart on one line of the band.
const TITLE_COLUMNS = 80
const ELLIPSIS = '…'
// What a message holding only empty paste tags is called.
const UNTITLED_PASTE = 'Pasted text'

/** A goal's title, made from a message the person sent: the person's own words, with any board viewer's state, and any
 * pasted text and its <pasted_content> tags, taken out; when the message is only a paste, the paste's first line. The title is the first
 * sentence of those words, cut to one line of the band with an ellipsis, so a long or pasted message never becomes the
 * goal's whole title. The agent still reads the whole message in the chat. */
export function goalTitleOf(message: string): string {
  const pastes: string[] = []
  const ownWords = message.replace(VIEWER_STATE, '\n').replace(PASTED, (_, pasted: string) => {
    pastes.push(pasted)
    return '\n'
  }).replace(STRAY_TAG, '\n')
  const words = wordsOf(ownWords) || pastes.map(firstLineOf).find(line => line !== '') || UNTITLED_PASTE
  return cutToTitle(words)
}

// A message that is only an answer or an acknowledgement, such as yes, no, ok or thanks.
const ANSWER = /^(?:y|n|yes|yeah|yep|no|nope|ok|okay|k|sure|thanks|thank you|thx|agreed|agree|done|good|great|fine|right|correct|got it|go|go ahead|do it)[\s.!]*$/i
// A message that is only marks, such as ??? or !.
const ONLY_MARKS = /^[\s?!.,]*$/
// The words a question opens with.
const QUESTION_OPENING = /^(?:why|what|where|when|who|which|how|is|are|was|were|do|does|did|can|could|should|would|will|has|have|isn't|aren't|doesn't|don't|didn't)\b/i
// The words that ask for work, so a message holding them is work even when it also asks something.
const ASKS_FOR_WORK = /\b(?:please|pls|fix|add|make|change|remove|delete|move|rename|build|write|run|deploy|pin|repin|commit|push|merge|update|create|implement|refactor|restart|install|open|close|start|stop|put|send|show|hide)\b/i
// Where a paste starts: a paste is the person's material for work, so a message holding one is never only talk.
const PASTE_OPENING = /<pasted_content\b/i
// The most words a message that is only talk holds; a longer one is likely to ask for something.
const TALK_WORDS = 15

/** Whether a message the person sent is only talk, not work to do: an answer or an acknowledgement (yes, ok,
 * thanks), only marks (???), or a short question that asks for no work (why is there no flush button?). The chat
 * answers talk; the queue holds only work, so a question or a comment never becomes a card or a step. A board viewer's
 * state and any paste are not the person's words, and a message that is nothing else is talk. */
export function isOnlyTalk(message: string): boolean {
  if (PASTE_OPENING.test(message)) {
    return false
  }
  const words = wordsOf(message.replace(VIEWER_STATE, '\n'))
  if (ONLY_MARKS.test(words) || ANSWER.test(words)) {
    return true
  }
  const isQuestion = words.trimEnd().endsWith('?') || QUESTION_OPENING.test(words)
  return isQuestion && words.split(' ').length <= TALK_WORDS && !ASKS_FOR_WORK.test(words)
}

/** Text's lines as one line of words, each line's markdown marks taken off. */
function wordsOf(text: string): string {
  return text.split(/\r?\n/).map(line => line.replace(LINE_MARKS, '').trim()).filter(line => line !== '').join(' ').replace(/\s+/g, ' ')
}

function firstLineOf(text: string): string {
  return text.split(/\r?\n/).map(line => wordsOf(line)).find(line => line !== '') ?? ''
}

/** The first sentence of the words, cut at a word with an ellipsis when it is longer than a title. */
function cutToTitle(words: string): string {
  const sentence = SENTENCE_END.exec(words)?.[1] ?? words
  if (sentence.length <= TITLE_COLUMNS) {
    return sentence
  }
  const room = sentence.slice(0, TITLE_COLUMNS - ELLIPSIS.length)
  const lastSpace = room.lastIndexOf(' ')
  return `${(lastSpace > 0 ? room.slice(0, lastSpace) : room).trimEnd()}${ELLIPSIS}`
}
