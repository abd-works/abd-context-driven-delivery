# widget-2 (question): A scenario renamed in markdown but not in its story test is held twice by its story, and no rule says so; a scenario a shared story file and its screen spec both write is held twice too

- **Charter:** C4
- **Tester:** Widget
- **Story:** Map Work Into Knowledge Graph / Build Practice Trees From Source / Read Story And Spec Trees From Source, scenario "Give a story the scenarios of every story file in code that specifies it" (it checks with `contain`, so it passes with the duplicate). No scenario covers a name that differs between markdown and code.
- **Module and class:** `cdd_guidance/practices/stories/model/story_map.py` `StoryTestScenarios._merged` (merges by `_words_of(name)` only; a code scenario with another name is appended, and two code files writing one name "each keep their own").
- **Severity:** question (if a renamed scenario should be one scenario: wrong result)

## Steps

1. Copy `cdd_guidance/practices/stories/model/fixtures/bookshop` to a throwaway folder.
2. Beside `story_tests/check-out/place-order/submit-order/submit_order_story.test.py` (scenarios "Submit a cart with one book", "Refuse an empty cart") write `submit_order_story.test.md` with `## Story: Submit Order` and the scenarios "Submit a cart holding one book" (same steps as the code's first scenario), "Refuse an empty cart", "Submit a cart twice".
3. `Graph().load_files(root, ["stories","ddd","clean_engineering"], [".context","story_tests","src","ordering"])`, then `StoryTree(...).scenarios(<map story Submit Order>)`.
4. Run every Stories graph rule (`SchemaRuleRun(BY_SLUG[slug], RuleCheckContext(stories))` for each slug).

## Expected

Either the renamed scenario is held once (markdown's name, code's body), or a rule reports that the story test writes a scenario the markdown does not, so the person knows to rename one side. The charter names this case ("scenarios dropped, duplicated or taken from the wrong side when markdown and code disagree").

## Actual

Submit Order holds 4 scenarios: the three markdown ones plus "Submit a cart with one book" from the `.py`, the same scenario under its old name. No Stories graph rule reports anything about it (`scenarios-differ-in-when-or-outcome` does not either, since the step words differ by their links).

Same story without my edit: Cancel Order holds "Cancel a submitted order" twice (from `confirm-order.story.shared.ts` and from `confirm-order.story.ui.spec.ts`), and View Order Confirmation holds "Show the confirmation of a submitted order" twice (ui spec and `view_order_confirmation_story.test.ts`). The docstring says this is meant ("each keep their own"); asking whether the explorer and the story's scenario count should show one scenario per name with both files as its places (as `Node.places` / `written_in` now do for markdown beside code).

## Tier that should catch it

Unit (`story_tests_on_map_spec.py`): an example with a renamed scenario, and `equal` instead of `contain` on Cancel Order's scenarios.

## Also seen by
