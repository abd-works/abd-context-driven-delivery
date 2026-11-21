// A broken rule a person asked to correct: the rule and what it says is wrong, the node and file it is in, the lines it
// marks, and the node's text.
export type ViolationCorrection = {
  rule: string;
  message: string;
  nodeName: string;
  nodeType: string;
  file: string;
  startLine: number;
  endLine: number;
  excerpt: string;
};

// What Correct came to: whether the correction reached the chat that opened the page, and the words the banner shows.
export type CorrectionOutcome = { isSent: boolean; words: string };

// What a page does when Correct is pressed: it sends the correction to the chat that opened it, its own way, and answers
// what came of it.
export type CorrectViolation = (correction: ViolationCorrection) => Promise<CorrectionOutcome>;

export const SENT_TO_CHAT: CorrectionOutcome = { isSent: true, words: 'Sent to chat' };
export const NOT_SENT: CorrectionOutcome = { isSent: false, words: 'Not sent' };

const HOW_TO_FIX = [
  'Fix this violation using the Clean Engineering practice guidelines and a test-driven approach.',
  'Run or add tests that express the intended behavior before or alongside the fix.',
];

// The whole correction, for a chat that is told nothing else: the node, the file and lines, the rule, the code, and
// what is wrong with it.
export function buildViolationCorrectPrompt(correction: ViolationCorrection): string {
  const fileSpan = correction.startLine >= 1 ? `${correction.file}:${correction.startLine}-${correction.endLine}` : correction.file;
  return [
    ...HOW_TO_FIX,
    '',
    `Node: ${correction.nodeName} (${correction.nodeType})`,
    fileSpan ? `File: ${fileSpan}` : '',
    `Rule: ${correction.rule}`,
    '',
    'Erroneous code:',
    '```',
    correction.excerpt,
    '```',
    '',
    `Violation: ${correction.message}`,
  ].join('\n');
}

// The correction as the words of a comment on the rule's lines: the file, the lines, and what they hold are left out,
// since a comment sent to the chat already names the file and lines and quotes them.
export function buildViolationCorrectComment(correction: ViolationCorrection): string {
  return [...HOW_TO_FIX, '', `Rule: ${correction.rule}`, `Violation: ${correction.message}`].join('\n');
}
