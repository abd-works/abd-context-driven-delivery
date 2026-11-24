// How Claude Code hands the mod a paste: the pasted text inside <pasted_content id="..."> tags, the closing tag
// sometimes missing when the paste runs to the end of the message.
const PASTED = /<pasted_content\b[^>]*>([\s\S]*?)(?:<\/pasted_content>|$)/gi
const STRAY_TAG = /<\/?pasted_content\b[^>]*>/gi
// A markdown line's own marks, so a heading or a list item reads as its words.
const LINE_MARKS = /^\s*(?:#+|[-*>]|\d+[.)])\s+/
// The end of a message's first sentence.
const SENTENCE_END = /^(.+?[.!?])(?:\s|$)/
// How long a goal's title may be, enough to tell goals apart on one line of the band.
const TITLE_COLUMNS = 80
const ELLIPSIS = '…'
// What a message holding only empty paste tags is called.
const UNTITLED_PASTE = 'Pasted text'

/** A goal's title, made from a message the person sent: the person's own words, with any pasted text and its
 * <pasted_content> tags taken out; when the message is only a paste, the paste's first line. The title is the first
 * sentence of those words, cut to one line of the band with an ellipsis, so a long or pasted message never becomes the
 * goal's whole title. The agent still reads the whole message in the chat. */
export function goalTitleOf(message: string): string {
  const pastes: string[] = []
  const ownWords = message.replace(PASTED, (_, pasted: string) => {
    pastes.push(pasted)
    return '\n'
  }).replace(STRAY_TAG, '\n')
  const words = wordsOf(ownWords) || pastes.map(firstLineOf).find(line => line !== '') || UNTITLED_PASTE
  return cutToTitle(words)
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
