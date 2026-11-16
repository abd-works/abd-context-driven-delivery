// How an app server finds the port it listens on, as the story Serve Dev Lane Apps On Their Own Ports asks
// (story_tests/register-and-install-toolsets/serve-cdd-code-in-lanes/serve-dev-lane-apps-on-their-own-ports/).
import { describe, expect, it } from 'vitest'

import { servePort } from './serve-port'

describe('the port an app server listens on', () => {
  describe('started by a dev-lane chat with --port', () => {
    it('should listen on the port the argument names, before its env variable and its ports file', () => {
      expect(servePort(['node', 'serve.ts', '--port', '9783'], 8783)).toBe(9783)
    })
  })

  describe('started by a stable-lane chat, which names no port', () => {
    it('should listen on its fallback, its env variable or its ports file', () => {
      expect(servePort(['node', 'serve.ts'], 8783)).toBe(8783)
    })
  })

  describe('started with --port and no number after it', () => {
    it('should listen on its fallback', () => {
      expect(servePort(['node', 'serve.ts', '--port'], 8783)).toBe(8783)
    })
  })
})
