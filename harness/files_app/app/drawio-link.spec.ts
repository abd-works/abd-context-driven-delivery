// Reported 2026-11-26: a story's link in the story map, opened in the draw.io viewer, showed "not found" at
// 127.0.0.1:8791/story_tests/..., since the browser read the link against the viewer, which serves only diagrams. The
// viewer now sends such a link to the Files server, which opens the file in the Files app at the heading it names.
import { mkdirSync, mkdtempSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'

import { describe, expect, it } from 'vitest'

import { DrawioLink, headingLineOf } from './drawio-link'

const STORY_MAP = ['# Story Map', '', '## (E) Register Agent Toolsets', '', '### (S) Author --> Register Agent Toolsets', '', '## (E) Register Agent Toolsets'].join('\n')

describe('a heading a link names by its anchor', () => {
  it('should be found on its line, counted from 1', () => {
    expect(headingLineOf(STORY_MAP, 'e-register-agent-toolsets')).toBe(3)
  })

  it('should be found with its punctuation dropped, as GitHub writes the anchor', () => {
    expect(headingLineOf(STORY_MAP, 's-author----register-agent-toolsets')).toBe(5)
  })

  it('should be the second heading of a repeated name when the anchor ends in -1', () => {
    expect(headingLineOf(STORY_MAP, 'e-register-agent-toolsets-1')).toBe(7)
  })

  it('should be the first line when no heading has the anchor', () => {
    expect(headingLineOf(STORY_MAP, 'e-nowhere')).toBe(1)
  })
})

describe('a link in a diagram of a project', () => {
  const project = mkdtempSync(join(tmpdir(), 'cdd-drawio-link-'))
  mkdirSync(join(project, '.context'))
  mkdirSync(join(project, 'story_tests', 'register'), { recursive: true })
  writeFileSync(join(project, '.context', 'story-map.md'), STORY_MAP)
  writeFileSync(join(project, 'story_tests', 'register', 'register_story.test.md'), '# Register')
  const diagram = join(project, '.context', 'story-map.drawio')

  describe('that names a story file beside the diagram, climbing out of its folder', () => {
    const link = new DrawioLink(diagram, '../story_tests/register/register_story.test.md', project)

    it('should be there', () => {
      expect(link.isThere).toBe(true)
    })

    it('should name the file from the project root', () => {
      expect(link.file).toBe('story_tests/register/register_story.test.md')
    })
  })

  describe('that names a heading of the story map beside the diagram', () => {
    const link = new DrawioLink('.context/story-map.drawio', 'story-map.md#s-author----register-agent-toolsets', project)

    it('should open the Files app on the story map at that heading, for the ticket and chat named', () => {
      const page = new URLSearchParams(link.pageOf('ui-fixes', 'chat-1').slice(2))
      expect([page.get('files'), page.get('file'), page.get('line'), page.get('chat'), page.get('project')]).toEqual(['ui-fixes', '.context/story-map.md', '5', 'chat-1', project])
    })

    it('should list the main ticket\'s files when no ticket is named', () => {
      expect(new URLSearchParams(link.pageOf('', '').slice(2)).get('files')).toBe('main')
    })
  })

  describe('that names a file that is not there', () => {
    const link = new DrawioLink(diagram, '../story_tests/gone_story.test.md', project)

    it('should not be there', () => {
      expect(link.isThere).toBe(false)
    })

    it('should say which link of which diagram names it', () => {
      expect(link.missing).toContain('../story_tests/gone_story.test.md')
    })
  })
})
