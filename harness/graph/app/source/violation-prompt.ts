import type { ViolationFocus } from '../graph/graph-selection';

// The broken rule Correct was pressed on: the violation chosen, the node the source view shows, and the lines the
// violation marks, else the node's. Python writes what Correct sends; the page asks for it with these and sends it.
export type CorrectionAsked = {
  violation: ViolationFocus;
  nodeId: string;
  startLine: number;
  endLine: number;
};

// What Correct came to: whether the correction reached the chat that opened the page, and the words the banner shows.
export type CorrectionOutcome = { isSent: boolean; words: string };

// What a page does when Correct is pressed: it sends the correction Python writes to the chat that opened it, its own
// way, and answers what came of it.
export type CorrectViolation = (asked: CorrectionAsked) => Promise<CorrectionOutcome>;

export const SENT_TO_CHAT: CorrectionOutcome = { isSent: true, words: 'Sent to chat' };
export const NOT_SENT: CorrectionOutcome = { isSent: false, words: 'Not sent' };
