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

  describe('Scenario: Show text in angle brackets that is no HTML tag', () => {
    it("should show a class's stereotypes, <<Aggregate Root>> <<Entity>>, as the file writes them", () => {
      const rendering = renderingOf('markdown', '#### Cart <<Aggregate Root>> <<Entity>>\n')
      expect(rendering.html).toContain('Cart &lt;&lt;Aggregate Root&gt;&gt; &lt;&lt;Entity&gt;&gt;')
    })

    it('should show what a collection holds, Collection<Cart>', () => {
      const rendering = renderingOf('markdown', '+ << aggregation >> carts: Collection<Cart>\n')
      expect(rendering.html).toContain('carts: Collection&lt;Cart&gt;')
    })

    it('should show a class named as an HTML tag is, <Address>, as text', () => {
      const rendering = renderingOf('markdown', 'ships to: Optional<Address>\n')
      expect(rendering.html).toContain('Optional&lt;Address&gt;')
    })

    it('should show a line that starts with a class in angle brackets', () => {
      const rendering = renderingOf('markdown', '<Cart> holds lines\n\n<<Repository>>\n')
      expect([rendering.html.includes('&lt;Cart&gt; holds lines'), rendering.html.includes('&lt;&lt;Repository&gt;&gt;')]).toEqual([true, true])
    })

    it('should still draw the HTML a markdown file holds, such as <details>', () => {
      const rendering = renderingOf('markdown', '<details><summary>More</summary>\n\nhidden\n\n</details>\n')
      expect(rendering.html).toContain('<details><summary>More</summary>')
    })
  })

  describe("Scenario: Show a file's front matter as its facts, under no heading", () => {
    const storyMap = '---\nfidelity: [discovery]\nartifact: [story-map]\nformat: md\n---\n\n# Story Map - Bookshop\n'
    const drawn = (text: string): HTMLElement => {
      const page = document.createElement('div')
      page.innerHTML = renderingOf('markdown', text).html
      return page
    }

    it("should show the page's title as its only heading", () => {
      expect([...drawn(storyMap).querySelectorAll('h1, h2')].map(heading => heading.textContent)).toEqual(['Story Map - Bookshop'])
    })

    it('should show each line of the front matter small, above the page', () => {
      expect([...drawn(storyMap).querySelectorAll('.front-matter > div')].map(fact => fact.textContent)).toEqual(['fidelity: [discovery]', 'artifact: [story-map]', 'format: md'])
    })

    it('should show a rule later in the file as a rule', () => {
      expect(renderingOf('markdown', '# Checkout\n\n---\n\nPlace an order.\n').html).toContain('<hr>')
    })
  })

  describe("Scenario: Underline a scenario's domain terms and examples", () => {
    it('should underline ++Book++ ++Tiny Tales++ and print no plus sign', () => {
      const rendering = renderingOf('markdown', '*Given* the Bookshop sells ++Book++ ++Tiny Tales++\n')
      expect(rendering.html).toContain('<em>Given</em> the Bookshop sells <u>Book</u> <u>Tiny Tales</u>')
    })

    it('should underline a domain term that is a link, keeping the link', () => {
      const rendering = renderingOf('markdown', '++[Book](../domain-model.md#book)++ - a title\n')
      expect(rendering.html).toContain('<u><a href="../domain-model.md#book">Book</a></u>')
    })

    it('should leave plus signs in code as they are', () => {
      expect(renderingOf('markdown', 'Use `count++ + ++count` here\n').html).toContain('<code>count++ + ++count</code>')
    })
  })

  describe('Scenario: Keep the levels of an indented tree', () => {
    const realization = ['a shipment', '  that has been created for a paid order', '    ```', '    -> Cart.add(book: Book)', "    it should list the order's books", '    ```', '    that has been dispatched', '      ```', '      -> Shipment.dispatch()', '      ```', ''].join('\r\n')
    const drawn = (): HTMLElement => {
      const page = document.createElement('div')
      page.innerHTML = renderingOf('markdown', realization).html
      return page
    }
    const indentOf = (element: Element): string => element.closest('[data-indent]')?.getAttribute('data-indent') ?? '0'

    it('should indent each state as deep as the file does, with spaces that do not collapse', () => {
      const html = renderingOf('markdown', realization).html
      expect([html.includes('<p>a shipment<br>&nbsp;&nbsp;that has been created for a paid order</p>'), html.includes('<p>&nbsp;&nbsp;&nbsp;&nbsp;that has been dispatched</p>')]).toEqual([true, true])
    })

    it('should keep each line of a call graph on a line of its own, indented under its state', () => {
      const graphs = [...drawn().querySelectorAll('pre')].map(graph => [graph.textContent, indentOf(graph)])
      expect(graphs).toEqual([["-> Cart.add(book: Book)\nit should list the order's books\n", '4'], ['-> Shipment.dispatch()\n', '6']])
    })

    it("should leave a list's nested items to the list", () => {
      const rendering = renderingOf('markdown', '- one\n  - two\n')
      expect([rendering.html.includes('data-indent'), rendering.html.includes('<li>two</li>')]).toEqual([false, true])
    })

    it("should keep a scenario's And step on a line of its own under its Given", () => {
      const rendering = renderingOf('markdown', '*Given* a cart  \n  *And* a book\n')
      expect(rendering.html).toContain('<br>&nbsp;&nbsp;<em>And</em> a book')
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
