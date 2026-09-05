/**
 * Scenario template — refer to context_tools/language-tools.md for tooling.
 *
 * ```
 * epic:      {epic-verb-noun}
 * sub_epic:  {sub-epic-verb-noun}
 * story:     {story-verb-noun}
 * file:      tests/{epic-verb-noun}/{sub-epic-verb-noun}/{story_verb_noun}.{tier}.ts
 * tier:      front-end | back-end | external-system
 * ```
 */

import { scenario, story } from "../../../story-test";

story("{Story Verb-Noun}", () => {
  scenario("{main-flow outcome}", ({ given, when, then }) => {
    given("{given step text}", async () => {
      // arrange
    });
    when("{when step text}", async () => {
      // act
    });
    then("{then step text}", async () => {
      // assert
    });
  });
});
