import { reasonOf } from '@cdd/cdd-page-failures';
import type { CddApi } from '@cdd/cdd-shared';
import { ChatClientGenerated } from '@cdd/harness/chat/chat';

// How long a failure stays on the page as a toast.
export const TOAST_MILLISECONDS = 8_000;
// The query the chat bar puts in every app link it opens: the chat that opened the page.
const CHAT_QUERY = 'chat';

// The chat that opened the page, as its link names it; none for a page no chat opened.
export function chatOfPage(): string {
  return new URLSearchParams(window.location.search).get(CHAT_QUERY)?.trim() ?? '';
}

type ToastsListener = (toasts: string[]) => void;

// Every failure the Graph app meets: shown on the page as a toast and sent to the chat that opened the page, which shows
// it on its chat bar as it shows its own, so the person can have the chat fix it. Each failure is shown and sent once,
// however often the progress read every few hundred milliseconds meets it again.
export class GraphFailures {
  private readonly toldChat = new Set<string>();
  private toasts: string[] = [];
  private readonly listeners = new Set<ToastsListener>();

  constructor(
    readonly api: CddApi,
    readonly chat: string,
  ) {}

  get shown(): string[] {
    return this.toasts;
  }

  // Calls listener with the toasts each time they change; answers what stops it.
  onChange(listener: ToastsListener): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  fail(failure: string, context: string): void {
    if (this.toldChat.has(failure)) return;
    this.toast(failure);
    this.tellChat(failure, context);
    this.toldChat.add(failure);
  }

  // A failure that cannot reach the chat stays on the page, since telling the chat again would fail the same way.
  private tellChat(failure: string, context: string): void {
    if (!this.chat) return;
    const told = ChatClientGenerated.named(this.api, this.chat).send('failure', JSON.stringify({ failure, context }));
    void told.catch((reason) => this.toast(`The chat was not told: ${reasonOf(reason)}`));
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
