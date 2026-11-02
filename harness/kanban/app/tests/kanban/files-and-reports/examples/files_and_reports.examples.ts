import type { ReportData } from '@cdd/harness/kanban/ticket'
import { boardHolding, placedTicket } from 'test-utils/board-examples'
import type { ExampleAnswers } from 'test-utils/behavior-test/example-api'

const SLUG = 'stories-story_map'
const STORY_MAP = 'tests/story-map.md'

const checkoutFlow = placedTicket('checkout-flow', 'Discovery', {
  progress: { [SLUG]: 'violations', 'ddd-bounded_context': 'not_started' },
  reports: { [SLUG]: '.sessions/checkout-flow/validation-reports/stories-story-map-20261101T100000.md' },
  violation_counts: { [SLUG]: 1 },
})

const REPORT: ReportData = {
  path: '.sessions/checkout-flow/validation-reports/stories-story-map-20261101T100000.md',
  text: '# Graph rule validation',
  has_saved_graph: true,
  rules: [
    {
      fidelity: SLUG,
      name: 'verb-noun-format',
      description: 'Name the story with a verb',
      count: 1,
      violations: [{ location: STORY_MAP, line: 6, message: 'Name the story with a verb', source: [{ number: 6, text: '- Handle Payment' }] }],
    },
  ],
}

export const BOARD_WITH_REPORT = boardHolding([checkoutFlow], [], 'checkout-flow')

export const FILE_ANSWERS: ExampleAnswers = {
  'POST /api/tickets/checkout-flow/files': { body: { [SLUG]: { markdown: [{ path: STORY_MAP, exists: true }], drawio: [{ path: 'tests/story-map.drawio', exists: false }] } } },
  'GET /api/tickets/checkout-flow/file?path=tests%2Fstory-map.md': { body: { path: STORY_MAP, text: '# Check Out Order' } },
  'GET /api/tickets/checkout-flow/report?fidelity=stories-story_map': { body: REPORT },
}
