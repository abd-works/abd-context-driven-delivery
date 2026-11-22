import { ChatToldFailures, reasonOf } from '@cdd/cdd-page-failures';
import type { CddApi } from '@cdd/cdd-shared';
import { ChatClientGenerated } from '@cdd/harness/chat/chat';

import { buildViolationCorrectPrompt, NOT_SENT, SENT_TO_CHAT, type CorrectionOutcome, type ViolationCorrection } from '../source/violation-prompt';

// How long a failure stays on the page as a toast.
export const TOAST_MILLISECONDS = 8_000;

const NO_CHAT = 'No chat opened this page, so the correction was not sent: open the Graph app from the chat bar.';

type ToastsListener = (toasts: string[]) => void;

// Every failure the Graph app meets: shown on the page as a toast and sent to the chat that opened the page, which shows
// it on its chat bar as it shows its own, so the person can have the chat fix it. Each failure is shown and sent once,
// however often the progress read every few hundred milliseconds meets it again. A correction of a broken rule goes to
// the same chat.
export class GraphFailures extends ChatToldFailures {
  private readonly shownOnce = new Set<string>();
  private toasts: string[] = [];
  private readonly listeners = new Set<ToastsListener>();

  // api is the page's way to its server, which the chat is told through and a correction sent through.
  constructor(
    private readonly api: CddApi,
    chat: string,
  ) {
    super(chat, () => api);
  }

  get shown(): string[] {
    return this.toasts;
  }

  // Calls listener with the toasts each time they change; answers what stops it.
  onChange(listener: ToastsListener): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  // Correct in the Graph app: the whole correction fills the prompt of the chat that opened the page, as a file comment
  // sent from the Files app does, for the person to review and send. The Graph app keeps no session's comments, so the
  // correction goes to the chat directly; a page no chat opened, or a chat that does not take it, says why in a toast.
  readonly correct = async (correction: ViolationCorrection): Promise<CorrectionOutcome> => {
    const context = `Correct ${correction.rule} in the Graph app`;
    if (!this.chat) {
      this.fail(NO_CHAT, context);
      return NOT_SENT;
    }
    try {
      await ChatClientGenerated.named(this.api, this.chat).send('fill', buildViolationCorrectPrompt(correction));
      return SENT_TO_CHAT;
    } catch (cause) {
      this.fail(`The correction for ${correction.rule} was not sent: ${reasonOf(cause)}`, context);
      return NOT_SENT;
    }
  };

  // A failure already shown once is not shown again, as it is not sent again.
  protected show(failure: string): void {
    if (this.shownOnce.has(failure)) return;
    this.shownOnce.add(failure);
    this.toast(failure);
  }

  // A failure that cannot reach the chat stays on the page, since telling the chat again would fail the same way.
  protected notTold(reason: string): void {
    this.toast(`The chat was not told: ${reason}`);
  }

  // A toast already showing is not shown twice: toasts are known by their text, and two alike confuse the list.
  toast(text: string): void {
    if (this.toasts.includes(text)) return;
    this.change([...this.toasts, text]);
    setTimeout(() => this.change(this.toasts.filter((shown) => shown !== text)), TOAST_MILLISECONDS);
  }

  private change(toasts: string[]): void {
    this.toasts = toasts;
    this.listeners.forEach((listener) => listener(toasts));
  }
}
