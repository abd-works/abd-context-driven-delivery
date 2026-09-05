/**
 * Scenario template — refer to context_tools/language-tools.md for tooling.
 *
 * ```
 * # Params — fill before writing code
 * epic:       {epic-verb-noun}           # kebab folder under tests/
 * sub_epic:   {sub-epic-verb-noun}       # kebab folder under epic/ (omit level if story hangs off epic)
 * story:      {story-verb-noun}          # Verb Noun title from the story map
 * story_file: {story-kebab-slug}         # kebab file slug, e.g. sign-up-create-account
 * tier:       e2e | front-end | back-end | {system}
 *
 * # Artifact layout (artifacts-mirror-story-hierarchy)
 * tests/
 *   {epic-verb-noun}/
 *     {sub-epic-verb-noun}/              # omit when the story file lives under epic/
 *       {story-kebab-slug}.{tier}.ts     # one GWT file per story per tier
 *
 * # Machinery (copy once per tests/ tree — full source inlined below)
 * story-test: tests/story-test.ts
 *
 * # Naming rules
 * - Epic / SubEpic folders → kebab-case verb-noun (Sign Up → sign-up)
 * - Story test file        → {story-kebab-slug}.{tier}.ts at epic or sub-epic — NO {story}/ folder
 * - Tier                   → file extension segment (.e2e.ts, .front-end.ts, .back-end.ts)
 * - Forbidden              → {story}/ folders, *_story.*, *_test_helper.* splits
 * ```
 *
 * Pattern: story-test machinery only — lifecycle, background(), scenario(), inline step bodies.
 */

import { afterAll, beforeAll, expect } from "vitest";
import { {AppPascal}E2e, config, type {AppPascal} } from "../../domain/{bounded-context}/runtime";
import type { {AggregatePascal} } from "../../domain/{bounded-context}/{aggregate_snake}";
import { {ErrorConstant}_MESSAGE } from "../../domain/{bounded-context}/{aggregate_snake}";
import { background, scenario, story } from "../../story-test";

story("{Story Verb-Noun}", () => {
  let {app_camel}: {AppPascal};
  let {aggregate_camel}: {AggregatePascal};

  beforeAll(async () => {
    {app_camel} = await {AppPascal}E2e.initialize(config);
  });

  afterAll(async () => {
    if ({app_camel}) await {app_camel}.close();
  });

  background(({ given }) => {
    given("{background given step}", async () => {
      await {app_camel}.{background_operation}();
    });

    scenario("{surface check — e.g. rules visible}", ({ when, then }) => {
      when("{primary when step}", async () => {
        {aggregate_camel} = await {app_camel}.{primary_when_operation}();
      });
      then("{observable surface outcome}", async () => {
        await expect
          .poll(async () => {
            {aggregate_camel}.{field} = "";
            await {aggregate_camel}.validate();
            return {aggregate_camel}.errors.{field}.length;
          }, { timeout: 15_000 })
          .toBeGreaterThanOrEqual(1);
      });
    });

    scenario("{validation branch while typing}", ({ when, then }) => {
      when("{primary when step}", async () => {
        {aggregate_camel} = await {app_camel}.{primary_when_operation}();
      }).and("{follow-on when step}", async () => {
        {aggregate_camel}.{field} = {invalid_value};
        await {aggregate_camel}.validate();
      });
      then("{validation message on domain object}", () => {
        expect({aggregate_camel}.errors.{field}).toBe({ErrorConstant}_MESSAGE);
      });
    });

    scenario("{validation clears when input conforms}", ({ when, then }) => {
      when("{primary when step}", async () => {
        {aggregate_camel} = await {app_camel}.{primary_when_operation}();
      }).and("{prior invalid state}", async () => {
        {aggregate_camel}.{field} = {invalid_value};
        await {aggregate_camel}.validate();
      });
      when("{corrective action}", async () => {
        {aggregate_camel}.{field} = {valid_value};
        await {aggregate_camel}.validate();
      });
      then("{error cleared on domain object}", () => {
        expect({aggregate_camel}.errors.{field}).toBeNull();
      });
    });

    scenario("{main-flow outcome}", ({ when, then }) => {
      when("{primary when step}", async () => {
        {aggregate_camel} = await {app_camel}.{primary_when_operation}();
      });
      when("{submit operation on domain object}", async () => {
        {aggregate_camel}.{field} = {valid_aggregate_value};
        await {aggregate_camel}.{operation}();
      });
      then("{post-condition on loaded aggregate}", async () => {
        const {entity_camel} = await {app_camel}.{repository}().load({aggregate_camel});
        expect({entity_camel}.isAt{State}("{StateName}")).toBe(true);
      });
    });
  });
});
