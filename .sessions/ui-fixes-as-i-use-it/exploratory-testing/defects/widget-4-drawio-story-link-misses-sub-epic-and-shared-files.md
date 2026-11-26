# widget-4: A rendered story map links a story to its scenarios only when a file is named after that story; a story whose scenarios are in a sub-epic file or a shared story file links back to the story map

- **Charter:** C4
- **Tester:** Widget
- **Story:** Draw Practice Models On Claude Whiteboard (links); no scenario covers which file a story's card links to. Promise in `render_spec.py` "should link a rendered story map to the story files beside the map it reads", and the layouts the scenario reader now supports (card 9fb1b3e76773: one story per file, sub-epic file, code only, shared story files).
- **Module and class:** `cdd_guidance/practices/stories/model/markdown/links.py` `StoryMapLinks.story_path` / `_by_story` (a story's file is found only by the slug of the file name), used by `drawio/nodes.py` `Vertex.take_links` (and the whiteboard and markdown renders that share StoryMapLinks).
- **Severity:** wrong result (the link opens the map heading, not the story's scenarios; a person following every link never reaches those scenarios from the diagram)

## Steps

1. Copy `cdd_guidance/practices/stories/model/fixtures/bookshop` to a throwaway folder; add `story_tests/browse-books/browse_books_story.test.md` holding `## Story: View Book` and `## Story: Filter Books` with a scenario each (the "sub-epic file holding several stories" layout).
2. `Render().for_call(ToolCall({}, root)).render("stories-story-map", format="drawio", paths=[".context/story-map.md"], source="markdown")`
3. `grep -o 'link="[^"]*"' .context/story-map.drawio`

## Expected

View Book and Filter Books link to `../story_tests/browse-books/browse_books_story.test.md` (with `#story-view-book` etc.), Cancel Order to `../story_tests/check-out/confirm-order/confirm-order.story.shared.ts`, Mark Order Shipped to `../story_tests/fulfil-order/fulfil-order.story.shared.py`: the files the graph reads their scenarios from (the graph knows: `StoryTree.scenarios` gives each scenario's file).

## Actual

```
link="story-map.md#s-customer----view-book"
link="story-map.md#s-customer----filter-books"
link="story-map.md#s-customer----cancel-order"
link="story-map.md#s-shop-clerk----mark-order-shipped"
```
while stories with a file named after them link to it (`../story_tests/browse-books/search-books/search_books_story.test.md`). The same happens on pml-web if its scenarios are ever kept in a sub-epic file; there the map's own markdown links carry `#story-…` anchors that the drawing drops.

## Tier that should catch it

Unit: render_spec / links spec example with a sub-epic file of two stories and a shared story file; no example has one.

## Also seen by
