/**
 * Scenario template — refer to context_tools/language-tools.md for tooling.
 *
 * ```
 * epic:      {epic-verb-noun}
 * sub_epic:  {sub-epic-verb-noun}
 * story:     {story-verb-noun}
 * file:      tests/{epic-verb-noun}/{sub-epic-verb-noun}/{story_verb_noun}.{tier}.ts
 * tier:      front-end | back-end | external-system
 * examples:  tests/{epic-verb-noun}/{sub-epic-verb-noun}/examples/{story_verb_noun}.examples.ts
 * givens:    tests/{epic-verb-noun}/{sub-epic-verb-noun}/givens.ts
 * whens:     tests/{epic-verb-noun}/{sub-epic-verb-noun}/whens.ts
 * ```
 *
 * Pattern: sign-up-create-account.e2e.ts — vitest lifecycle, background() wrapping scenarios,
 * givens/whens/examples modules, when().and() chains, domain assertions in then().
 */

import { afterAll, beforeAll, expect } from "vitest";
import { {AppPascal}E2e, config, type {AppPascal} } from "../../domain/{bounded-context}/runtime";
import type { {AggregatePascal} } from "../../domain/{bounded-context}/{aggregate_snake}";
import { {ErrorConstant}_MESSAGE } from "../../domain/{bounded-context}/{aggregate_snake}";
import { background, scenario, story } from "../../story-test";
import {
  invalid{Field}Example,
  valid{Field}Example,
  valid{Aggregate}Example,
} from "./examples/{story_verb_noun}.examples";
import { {backgroundGivenFn} } from "./givens";
import { {primaryWhenFn} } from "./whens";

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
      await {backgroundGivenFn}({app_camel});
    });

    scenario("{surface check — e.g. rules visible}", ({ when, then }) => {
      when("{primary when step}", async () => {
        {aggregate_camel} = await {primaryWhenFn}({app_camel});
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
        {aggregate_camel} = await {primaryWhenFn}({app_camel});
      }).and("{follow-on when step}", async () => {
        {aggregate_camel}.{field} = invalid{Field}Example;
        await {aggregate_camel}.validate();
      });
      then("{validation message on domain object}", () => {
        expect({aggregate_camel}.errors.{field}).toBe({ErrorConstant}_MESSAGE);
      });
    });

    scenario("{validation clears when input conforms}", ({ when, then }) => {
      when("{primary when step}", async () => {
        {aggregate_camel} = await {primaryWhenFn}({app_camel});
      }).and("{prior invalid state}", async () => {
        {aggregate_camel}.{field} = invalid{Field}Example;
        await {aggregate_camel}.validate();
      });
      when("{corrective action}", async () => {
        {aggregate_camel}.{field} = valid{Field}Example;
        await {aggregate_camel}.validate();
      });
      then("{error cleared on domain object}", () => {
        expect({aggregate_camel}.errors.{field}).toBeNull();
      });
    });

    scenario("{main-flow outcome}", ({ when, then }) => {
      when("{primary when step}", async () => {
        {aggregate_camel} = await {primaryWhenFn}({app_camel});
      });
      when("{submit operation on domain object}", async () => {
        {aggregate_camel}.{field} = valid{Aggregate}Example.{field};
        await {aggregate_camel}.{operation}();
      });
      then("{post-condition on loaded aggregate}", async () => {
        const {entity_camel} = await {app_camel}.{repository}().load({aggregate_camel});
        expect({entity_camel}.isAt{State}("{StateName}")).toBe(true);
      });
    });
  });
});
