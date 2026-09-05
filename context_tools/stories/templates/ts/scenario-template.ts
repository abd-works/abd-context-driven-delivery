/**
 * Scenario template — refer to context_tools/language-tools.md for tooling.
 *
 * ```
 * epic:      {epic-verb-noun}
 * sub_epic:  {sub-epic-verb-noun}
 * story:     {story-verb-noun}
 * file:      tests/{epic-verb-noun}/{sub-epic-verb-noun}/{story_verb_noun}.{tier}.ts
 * tier:      front-end | back-end | external-system
 * fixtures:  tests/{epic-verb-noun}/examples/  tests/{epic-verb-noun}/{sub-epic-verb-noun}/givens.ts
 * ```
 *
 * Pattern: sign-up-create-account.e2e.ts — one file per story per tier; domain ops in When;
 * observable assertions in Then/.and(); infrastructure in beforeAll; shared state on StoryScenario.
 */

import { story, scenario, expect } from "../../story-test";
import { {AppPascal} } from "../../domain/{bounded-context}/{app_snake}";
import type { {AggregatePascal} } from "../../domain/{bounded-context}/{aggregate_snake}";

/** Shared boot, background, and typed handles for this story's scenarios. */
class {StoryPascal}Story {
  app!: {AppPascal};
  {aggregate_camel}!: {AggregatePascal};

  /** Infrastructure — browser boot / app wiring only. Never domain assertions here. */
  static async boot(): Promise<{AppPascal}> {
    return {AppPascal}.initialize(/* config from examples/ */);
  }

  /** Background — shared Given state every scenario inherits. Domain state only. */
  background(app: {AppPascal}): void {
    this.app = app;
    this.{aggregate_camel} = app.{aggregate_camel}();
  }
}

story("{Story Verb-Noun}", () => {
  let ctx: {StoryPascal}Story;

  beforeAll(async () => {
    const app = await {StoryPascal}Story.boot();
    ctx = new {StoryPascal}Story();
    ctx.background(app);
  });

  scenario("{main-flow outcome}", ({ given, when, then }) => {
    given("{given step text}", () => {
      // extra per-scenario Given — reuse ctx.{aggregate_camel}
    });

    when("{when step text}", () => {
      // domain operation under test — e.g. ctx.app.authentication().register(...)
    });

    then("{then step text}", () => {
      expect(ctx.{aggregate_camel}.{observable}()).toBe(/* expected */);
    }).and("{additional outcome}", () => {
      expect(ctx.{aggregate_camel}.{observable2}()).toBe(/* expected */);
    });
  });

  scenario("{alternate outcome — e.g. validation branch}", ({ given, when, then }) => {
    given("{alternate given}", () => {
      // ...
    });

    when("{alternate when}", () => {
      // ...
    });

    then("{alternate then}", () => {
      expect(/* observable */).toBe(/* expected */);
    });
  });
});
