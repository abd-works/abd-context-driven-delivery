import type { ViolationPlace } from '../graph/graph-selection';

// The broken place Fix this one was pressed on: the rule, the place chosen, the node the source view shows, and the
// lines the place marks, else the node's. Python writes what the fix says; the page asks for it with these and sends it.
export type FixAsked = {
  rule: string;
  place: ViolationPlace;
  nodeId: string;
  startLine: number;
  endLine: number;
};

// What a fix came to: whether it reached the chat that opened the page, and the words shown beside the button.
export type FixOutcome = { isSent: boolean; words: string };

// What a page does when Fix this one is pressed on one broken place, and Fix rule on the rule broken: it sends the fix
// Python writes to the chat that opened it, its own way, and answers what came of it.
export type FixOne = (asked: FixAsked) => Promise<FixOutcome>;
export type FixRule = (rule: string) => Promise<FixOutcome>;

// The fixes a page offers on a broken rule's banner: always Fix this one, and Fix rule where the page can fix every
// place of the rule at once.
export type ViolationFixes = { one: FixOne; rule?: FixRule };

export const SENT_TO_CHAT: FixOutcome = { isSent: true, words: 'Sent to chat' };
export const NOT_SENT: FixOutcome = { isSent: false, words: 'Not sent' };
