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

## Triage

- **Status:** confirmed
- **Severity:** wrong result (the card opens the map heading, not the story's scenarios)
- **Triaged by:** Prism
- **Why:** `StoryMapLinks.story_path` found a story's file only by the slug of a file name (`*_story.test.md`, `*_story.test.py/.ts`), and never looked at shared story files. Reproduced on a bookshop copy with a sub-epic file `browse_books_story.test.md` holding View Book and Filter Books: their cards, Cancel Order's and Mark Order Shipped's linked to `story-map.md#…`.

## Fix

- **Test (unit):** `cdd_guidance/practices/stories/model/markdown/story_map_links_spec.py` over the scenario-layouts fixture: own file, sub-epic markdown (at `#story-…`), Python story test holding two stories, TypeScript shared story file, and the drawio render. Seen failing first (4 of 5).
- **Scenario:** "Link each story of a drawn story map to the file that writes its scenarios, in every layout" in `story_tests/deliver-work-with-context-guidance/produce-formal-artifacts/take-practice-artifacts-to-other-formats-and-back/take_artifact_to_another_format_and_back_story.test.md`.
- **Fix:** `story_map_files.py` gains `SHARED_STORY_SUFFIXES`, `StoryMapFiles.shared_stories_below()` and `story_line(text, name)` (the line naming a story: a `Story:` heading or comment, or its `story(`/`shareStory(`/`.scenario(` call). `links.py` `StoryMapLinks.story_path` falls back to the first story file, story test or shared story file that names the story; `story_file` adds the story's heading anchor when that file is markdown holding it among others. drawio, markdown and whiteboard renders share it. Re-run on the bookshop copy: View Book and Filter Books link to `browse_books_story.test.md#story-…`, Cancel Order to `confirm-order.story.shared.ts`, Mark Order Shipped to `fulfil-order.story.shared.py`.
- **Commit:** pending
