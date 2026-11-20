import { describe, expect, it } from 'vitest'

import { opensRendered, renderedFormOf, renderingOf } from './file-rendering'

// Render each format the page can draw, with Source a press away (review_files_in_files_app_story.test.md, View File In
// Source View): markdown as its page, HTML in a frame that runs no script, SVG as its drawing, and JSON laid out.
describe('Render a file as the page it describes', () => {
  describe('the form a file renders in, by its name', () => {
    it('should render .md and .markdown files as markdown, whatever their case', () => {
      expect([renderedFormOf('README.md'), renderedFormOf('.context/story-map.MD'), renderedFormOf('notes/plan.markdown')]).toEqual(['markdown', 'markdown', 'markdown'])
    })

    it('should render .html and .htm as a page, .svg as a drawing and .json laid out', () => {
      expect([renderedFormOf('notes/page.html'), renderedFormOf('notes/old.htm'), renderedFormOf('design/cart.svg'), renderedFormOf('data/cart.json')]).toEqual(['html', 'html', 'svg', 'json'])
    })

    it('should give a code file, a text file or a draw.io file no rendered form', () => {
      expect([renderedFormOf('src/checkout/order.py'), renderedFormOf('notes/plain.txt'), renderedFormOf('design/.context/story-map.drawio')]).toEqual([null, null, null])
    })
  })

  describe('Scenario: Render a markdown file as the page it describes', () => {
    it('should show # Checkout as a heading reading Checkout, not as # Checkout', () => {
      const rendering = renderingOf('markdown', '# Checkout\n\nPlace an order from a cart.\n')
      expect(rendering.html).toContain('<h1>Checkout</h1>')
      expect(rendering.html).not.toContain('# Checkout')
    })

    it("should keep each of a scenario's steps on a line of its own", () => {
      const rendering = renderingOf('markdown', '*Given* a cart with two items\n*When* the Person places the order\n')
      expect(rendering.html).toContain('<em>Given</em> a cart with two items<br>')
    })

    it("should draw a scenario's table as a table", () => {
      const rendering = renderingOf('markdown', '| file | text |\n| --- | --- |\n| order.py | class Order |\n')
      expect(rendering.html).toContain('<td>order.py</td>')
    })

    it('should run no script the markdown holds, in a script tag or an attribute', () => {
      const rendering = renderingOf('markdown', '# Checkout\n\n<script>window.hacked = 1</script><img src="x" onerror="window.hacked = 1">\n')
      expect([rendering.html.includes('<script'), rendering.html.includes('onerror')]).toEqual([false, false])
    })
  })

  describe('Scenario: Render each format the page can draw', () => {
    it('should hand an HTML page to the frame as it is, since the frame runs no script', () => {
      const page = '<h1>Checkout</h1><script>parent.hacked = 1</script>'
      expect(renderingOf('html', page)).toEqual({ form: 'html', html: page, problem: '' })
    })

    it('should draw an SVG with its circle and without its script', () => {
      const rendering = renderingOf('svg', '<svg xmlns="http://www.w3.org/2000/svg"><circle r="4"/><script>alert(1)</script></svg>')
      expect([rendering.html.includes('<circle'), rendering.html.includes('<script')]).toEqual([true, false])
    })

    it('should lay out JSON two spaces to a level', () => {
      const rendering = renderingOf('json', '{"items":[1,2]}')
      expect(rendering.html.split('\n')[1]).toEqual('  &quot;items&quot;: [')
    })

    it('should show JSON that is not valid as its text, and say it is not valid JSON', () => {
      const rendering = renderingOf('json', '{"items":')
      expect([rendering.html, rendering.problem.startsWith('Not valid JSON')]).toEqual(['{&quot;items&quot;:', true])
    })
  })

  describe('Scenario: Open a rendered file as source at the lines asked for', () => {
    it('should open a file with a rendered form rendered when no lines are asked for', () => {
      expect(opensRendered('markdown', [])).toBe(true)
    })

    it('should open it as source when lines are asked for, such as a node selected in the graph view', () => {
      expect(opensRendered('markdown', [{ start: 3, end: 5 }])).toBe(false)
    })

    it('should open a file with no rendered form as source', () => {
      expect(opensRendered(null, [])).toBe(false)
    })
  })
})
