import { afterEach, describe, expect, it, vi } from 'vitest';

import type { CddApi } from '@cdd/cdd-shared';

import { chatOfPage, GraphFailures, TOAST_MILLISECONDS } from './graph-failures';

// The Graph app's server as the page reaches it: each post is kept in order; a chat send can be made to fail.
class FakeGraphServer implements CddApi {
  readonly posts: { path: string; body: Record<string, unknown> }[] = [];
  isChatDown = false;

  async post<Result>(path: string, body: Record<string, unknown> = {}): Promise<Result | null> {
    this.posts.push({ path, body });
    if (this.isChatDown) throw new Error('the cdd server is not running');
    return null;
  }

  sent(): { failure: string; context: string }[] {
    return this.posts.filter((post) => post.path === '/chat/chat-1/send').map((post) => JSON.parse(String(post.body.text)));
  }
}

const DIAGNOSIS = 'I just encountered an error doing load_working_copy on C:/work. Please diagnose and fix.\n\nno such folder';
const CONTEXT = 'Loading the graph of C:/work';

async function settled(): Promise<void> {
  await new Promise((resolve) => setTimeout(resolve, 0));
}

describe('Graph app failures', () => {
  afterEach(() => {
    vi.useRealTimers();
    window.history.replaceState(null, '', '/');
  });

  describe('with a page the chat bar opened', () => {
    it('should name the chat from the page link', () => {
      window.history.replaceState(null, '', '/?project=C:/work&chat=chat-1');
      expect(chatOfPage()).toBe('chat-1');
    });

    describe('that meets a failure the server diagnosed', () => {
      it('should send the diagnosis to the chat that opened the page', () => {
        const server = new FakeGraphServer();
        new GraphFailures(server, 'chat-1').fail(DIAGNOSIS, CONTEXT);
        expect(server.posts).toEqual([
          { path: '/chat/chat-1/send', body: { kind: 'failure', text: JSON.stringify({ failure: DIAGNOSIS, context: CONTEXT }) } },
        ]);
      });

      it('should show the diagnosis on the page', () => {
        const failures = new GraphFailures(new FakeGraphServer(), 'chat-1');
        failures.fail(DIAGNOSIS, CONTEXT);
        expect(failures.shown).toEqual([DIAGNOSIS]);
      });

      it('should take the toast away after a few seconds', () => {
        vi.useFakeTimers();
        const failures = new GraphFailures(new FakeGraphServer(), 'chat-1');
        failures.fail(DIAGNOSIS, CONTEXT);
        vi.advanceTimersByTime(TOAST_MILLISECONDS);
        expect(failures.shown).toEqual([]);
      });
    });

    describe('that meets the same failure again on the next progress read', () => {
      it('should send it to the chat once', () => {
        const server = new FakeGraphServer();
        const failures = new GraphFailures(server, 'chat-1');
        failures.fail(DIAGNOSIS, CONTEXT);
        failures.fail(DIAGNOSIS, CONTEXT);
        expect(server.sent()).toHaveLength(1);
      });

      it('should show it once', () => {
        const failures = new GraphFailures(new FakeGraphServer(), 'chat-1');
        failures.fail(DIAGNOSIS, CONTEXT);
        failures.fail(DIAGNOSIS, CONTEXT);
        expect(failures.shown).toEqual([DIAGNOSIS]);
      });
    });

    describe('that cannot reach the chat', () => {
      it('should show on the page that the chat was not told', async () => {
        const server = new FakeGraphServer();
        server.isChatDown = true;
        const failures = new GraphFailures(server, 'chat-1');
        failures.fail(DIAGNOSIS, CONTEXT);
        await settled();
        expect(failures.shown).toEqual([DIAGNOSIS, 'The chat was not told: the cdd server is not running']);
      });

      it('should not send the failure of telling the chat to the chat', async () => {
        const server = new FakeGraphServer();
        server.isChatDown = true;
        new GraphFailures(server, 'chat-1').fail(DIAGNOSIS, CONTEXT);
        await settled();
        expect(server.posts).toHaveLength(1);
      });
    });
  });

  describe('with a page no chat opened', () => {
    it('should show the failure on the page', () => {
      const failures = new GraphFailures(new FakeGraphServer(), '');
      failures.fail(DIAGNOSIS, CONTEXT);
      expect(failures.shown).toEqual([DIAGNOSIS]);
    });

    it('should send nothing', () => {
      const server = new FakeGraphServer();
      new GraphFailures(server, '').fail(DIAGNOSIS, CONTEXT);
      expect(server.posts).toEqual([]);
    });
  });
});
