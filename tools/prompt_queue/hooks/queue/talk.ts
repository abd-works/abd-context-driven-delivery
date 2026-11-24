// What the Claude app puts before a message sent while a board viewer is open: the viewer's live state, written by the
// viewer's page, never by the person, so it is not read as the person's words.
const VIEWER_STATE = /<artifact-view-context\b[^>]*>[\s\S]*?(?:<\/artifact-view-context>|$)/gi
// A markdown line's own marks, so a heading or a list item reads as its words.
const LINE_MARKS = /^\s*(?:#+|[-*>]|\d+[.)])\s+/
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
 * answers talk, so the agent is not asked to place it on the queue. A board viewer's state is not the person's words,
 * and a message that is nothing else is talk; a message holding a paste never is. */
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
