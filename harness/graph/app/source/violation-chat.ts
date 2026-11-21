import { ChatClientGenerated } from '@cdd/harness/chat/chat';

import { reasonOf } from '@cdd/cdd-page-failures';
import type { GraphFailures } from '../graph/graph-failures';
import { buildViolationCorrectPrompt, NOT_SENT, SENT_TO_CHAT, type CorrectViolation } from './violation-prompt';

const NO_CHAT = 'No chat opened this page, so the correction was not sent: open the Graph app from the chat bar.';

// Correct in the Graph app: the whole correction fills the prompt of the chat that opened the page, as a file comment
// sent from the Files app does, for the person to review and send. The Graph app keeps no session's comments, so the
// correction goes to the chat directly; a page no chat opened, or a chat that does not take it, says why in a toast.
export function correctInChat(failures: GraphFailures): CorrectViolation {
  return async (correction) => {
    if (!failures.chat) {
      failures.fail(NO_CHAT, `Correct ${correction.rule} in the Graph app`);
      return NOT_SENT;
    }
    try {
      await ChatClientGenerated.named(failures.api, failures.chat).send('fill', buildViolationCorrectPrompt(correction));
      return SENT_TO_CHAT;
    } catch (cause) {
      failures.fail(`The correction for ${correction.rule} was not sent: ${reasonOf(cause)}`, `Correct ${correction.rule} in the Graph app`);
      return NOT_SENT;
    }
  };
}
