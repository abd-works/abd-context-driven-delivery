import { describe, expect, it } from 'vitest';

import type { CddApi } from '@cdd/cdd-shared';

import { GraphFailures } from './graph-failures';

// What Python writes for the correction, which the page sends as it is; its words are pinned by Python's spec.
const PROMPT = 'Fix this violation using the Clean Engineering practice guidelines and a test-driven approach.\n…\nRule: limit-operation-parameters';

// The Graph app's server as the page reaches it: each post is kept in order; it answers the correction Python writes,
// none for a node that no longer breaks the rule; a chat send can be made to fail.
class FakeGraphServer implements CddApi {
  readonly posts: { path: string; body: Record<string, unknown> }[] = [];
  isChatDown = false;
  correction = PROMPT;

  async post<Result>(path: string, body: Record<string, unknown> = {}): Promise<Result | null> {
    this.posts.push({ path, body });
    if (path === '/graph/correction-prompt') return this.correction as Result;
    if (this.isChatDown && body.kind === 'fill') throw new Error("chat 'chat-1' is not connected");
    return null;
  }
}

const CORRECTION = {
  violation: { rule: 'limit-operation-parameters', message: "Operation 'failure' takes 4 parameters (maximum 2).", startLine: 10, endLine: 18 },
  nodeId: 'clean_engineering:Operation:failure',
  startLine: 10,
  endLine: 18,
};

const filledIn = (server: FakeGraphServer): string[] =>
  server.posts.filter((post) => post.path === '/chat/chat-1/send' && post.body.kind === 'fill').map((post) => String(post.body.text));

// Correct in the Graph app reaches the chat as a sent file comment does: the chat's prompt box is filled with it, for
// the person to review and send; requested 2026-11-20: Correct must work "the same as comments".
describe('Correct Broken Rule In Graph App', () => {
  describe('with a page the chat bar opened', () => {
    it('should ask Python for the correction of the rule on its node', async () => {
      const server = new FakeGraphServer();
      await new GraphFailures(server, 'chat-1').correct(CORRECTION);
      expect(server.posts.filter((post) => post.path === '/graph/correction-prompt').map((post) => post.body)).toEqual([
        { node_id: 'clean_engineering:Operation:failure', rule: 'limit-operation-parameters' },
      ]);
    });

    it("should fill the chat's prompt with the correction Python wrote", async () => {
      const server = new FakeGraphServer();
      await new GraphFailures(server, 'chat-1').correct(CORRECTION);
      expect(filledIn(server)).toEqual([PROMPT]);
    });

    it('should answer that it was sent to the chat', async () => {
      expect(await new GraphFailures(new FakeGraphServer(), 'chat-1').correct(CORRECTION)).toEqual({ isSent: true, words: 'Sent to chat' });
    });

    describe('that is not connected', () => {
      it('should answer that it was not sent, and say why in a toast', async () => {
        const server = new FakeGraphServer();
        server.isChatDown = true;
        const failures = new GraphFailures(server, 'chat-1');
        expect(await failures.correct(CORRECTION)).toEqual({ isSent: false, words: 'Not sent' });
        expect(failures.shown).toContain("The correction for limit-operation-parameters was not sent: chat 'chat-1' is not connected");
      });
    });

    describe('with a node that no longer breaks the rule', () => {
      const withNoCorrection = (): FakeGraphServer => Object.assign(new FakeGraphServer(), { correction: '' });

      it('should answer that it was not sent', async () => {
        expect(await new GraphFailures(withNoCorrection(), 'chat-1').correct(CORRECTION)).toEqual({ isSent: false, words: 'Not sent' });
      });

      it("should leave the chat's prompt as it was", async () => {
        const server = withNoCorrection();
        await new GraphFailures(server, 'chat-1').correct(CORRECTION);
        expect(filledIn(server)).toEqual([]);
      });
    });
  });

  describe('with a page no chat opened', () => {
    it('should answer that it was not sent, and say to open the page from the chat bar', async () => {
      const server = new FakeGraphServer();
      const failures = new GraphFailures(server, '');
      expect(await failures.correct(CORRECTION)).toEqual({ isSent: false, words: 'Not sent' });
      expect(server.posts).toEqual([]);
      expect(failures.shown).toContain('No chat opened this page, so the correction was not sent: open the Graph app from the chat bar.');
    });
  });
});
