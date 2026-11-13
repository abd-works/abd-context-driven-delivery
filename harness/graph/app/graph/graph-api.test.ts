import { afterEach, describe, expect, it, vi } from 'vitest';

import { GraphApi } from './graph-api';

// A page opened on a project names it on every call, so the server answers it in the session open in that project, the
// one the board shows as active.
describe('Open The Graph On The Session Open In A Project', () => {
  const sent: Headers[] = [];
  vi.stubGlobal('fetch', (_path: string, init?: RequestInit) => {
    sent.push(new Headers(init?.headers));
    return Promise.resolve(Response.json({}));
  });
  afterEach(() => {
    sent.length = 0;
  });

  describe('with a page opened at ?project=C:/dev/sandbox', () => {
    it('should name the project on every call', async () => {
      await new GraphApi('C:/dev/sandbox').post('/graph/load-practice-roots');
      expect(sent[0]?.get('X-CDD-Project')).toBe('C:/dev/sandbox');
    });
  });

  describe('with a page opened without a project', () => {
    it('should name no project, so the server works on its own', async () => {
      await new GraphApi('').post('/graph/inventory');
      expect(sent[0]?.has('X-CDD-Project')).toBe(false);
    });
  });
});
