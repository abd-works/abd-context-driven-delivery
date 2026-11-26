# widget-6: The story explorer's "open" request for every scenario written in a story test in code names line 0, and a scenario a shared story file or a screen spec writes is named in the other file

- **Charter:** C4
- **Tester:** Widget
- **Story:** Explore Stories In Story UI / Navigate The Story Tree (the explorer's rows and their open ⧉ requests); no scenario covers code-written scenarios. The pml-web expected tree (`choose_lines_explorer.expected.json`) has markdown only.
- **Module and class:** `cdd_guidance/practices/ux/model/claude_design/story_canvas.py` `ClaudeDesignStoryMap` (the explorer tree's `f` of each scenario), fed by `ProjectStoryCanvas.story_map()`; the row's `copyOf(sc.f, …)` in `explorer.dc.html` copies "Copy a request to open <f>".
- **Severity:** wrong result (open ⧉ on a code scenario sends the chat to line 0, and for the duplicated rows to the wrong file)

## Steps

1. Copy `cdd_guidance/practices/stories/model/fixtures/bookshop` to a throwaway folder.
2. Draw the explorer as `choose_lines_explorer_spec._drawn_tree` does:
   ```python
   canvas = ProjectStoryCanvas(ROOT, ROOT / "ux", ROOT, NoCanvasFixtures([]))
   story_map = canvas.story_map()
   setup = StoryCanvasSetup(ux_map=JsonUxMap().parse({"screens": []}), sources=canvas.sources(story_map), files_root=ROOT)
   page = json.loads(ClaudeDesignStoryMap(setup=setup).render(story_map))[f"project/{EXPLORER_FILE}"]
   ```
   then `CanvasExplorer(folder).tree()` on the page, and read each scenario's `f`.

## Expected

Each scenario's `f` is the file that writes it and the line of its `scenario(` / `with scenario(` / `test(` call, as markdown scenarios get their `#### Scenario:` line (`submit_order_story.test.md:9`).

## Actual

Every code scenario has line 0: `pack_order_story.test.py:0` (x2), `authorize_payment_story.test.py:0` (x2), `submit_order_story.test.py:0`, `fulfil-order.story.shared.py:0` (x2), `confirm-order.story.shared.ts:0`, `view_order_confirmation_story.test.ts:0` (x3), `confirm-order.story.ui.spec.ts:0` (x2). Story rows are right (`pack_order_story.test.py:13` is `# Story: Pack Order`).
Wrong file: Cancel Order's two "Cancel a submitted order" rows both name `confirm-order.story.ui.spec.ts:0`, though one is the shared file's (`confirm-order.story.shared.ts`, where the graph places it); View Order Confirmation's two "Show the confirmation of a submitted order" rows both name `view_order_confirmation_story.test.ts:0`, though one is the screen spec's. The story row of View Order Confirmation names `confirm-order.story.ui.spec.ts:1` (the screen spec's header comment), not `view_order_confirmation_story.test.ts`. So the two duplicate rows (see widget-2) cannot be told apart even by their file.

## Tier that should catch it

Unit: an explorer spec over the bookshop fixture (code layouts), like `choose_lines_explorer_spec.py` is for pml-web's markdown.

## Also seen by
