---
name: stories-acceptance_tests
description: "Provide guidance for creating story maps, scenarios, and acceptance tests."
disable-model-invocation: true
---

# stories-acceptance_tests

Use stories guidance at `acceptance_tests` fidelity only.

Refer to these skills in order to fill in details from previous fidelities if not present:
@stories-scenarios
@stories-story_map
@stories-scaffold

# Contexts

Map stakeholder and system interactions as behaviours that deliver a solution.

Interactions fit into a hierarchy: a `StoryMap` of `Epic` → nestable `SubEpic` → `Story`. Each story is `Scenario`s with discrete steps; backgrounds and scenarios carry examples.

| Fidelity | Default Format | Produce |
|---|---|---|
| **story_map** | markdown | Story map + thin-slice |
| **scenarios** | typescript | Main-flow scenarios per story (single or multiple); optional variations; `examples/` + `givens.ts`. Pass `format markdown` when the strategy asks for a markdown view. |
| **acceptance_tests** | typescript | `tests/{epic}/{sub-epic}/{story}.{tier}.ts` — one GWT file per story per seam (`front-end`, `back-end`, or another system name). No story folder. Fixtures: `examples/` + `givens.ts`. CE runs alongside for wrap classes. |

**Templates** live under `templates/` per format. **Scanners** read the canonical model only — never language syntax.

---

## Shared rules

- **`vocabulary-traces-to-domain-source`** — Trace terms to domain language / model when present.
- **`artifacts-mirror-story-hierarchy`** — Mirror Epic → SubEpic → Story on disk as folders for epic and sub-epic, and as `{story}.{tier}.ts` files (no per-story directory).
- **`read-all-source-context-in-full`** — Before locking hierarchy **and before any grill/iterate question about a seam**, prove-read **every relevant referenced context** for that decision: owning `*-segment.md`, `module-context.md`, session sketches / grill-answers / handoff, peer story-context, build-order, and any path the plan or prior answers cite. Index / mid-epic stub columns are structure hints only — **not** story inventory. Grep or primer-only skims do not count; cite concrete terms from the files read in the question turn. Also re-read these rules. Do not thin from titles or memory!
- **`do-not-invent-requirements`** — Only model behaviours present in source context or an explicit ask. Never invent:
  - status concepts, maintenance signals, warning badges, or config columns (e.g. `Status (ok/stale)`) the source does not require — unconfigured / not-yet-current = **no row** + the existing fallback, never a new invented state to render;
  - a second, competing command / invoke surface beside one the user already specified (e.g. a raw YAML `toolset`/`fidelity`/`action` "Invoke" block given equal billing next to an already-locked `/{skill} <action> {fidelity}` line). Keep the specified surface primary; any secondary format is a subsidiary link at most — never inlined, never a co-equal page element.

---

## acceptance_tests

**Default format:** typescript

**Goal:** Turn locked scenarios into runnable acceptance coverage; CE runs alongside to produce matching wrap classes under `domain/`.

**Tooling & Idioms:** Refer to [`context_tools/language-tools.md`](/context_tools/language-tools.md) for language-specific tool recommendations and idiomatic patterns for tests.

**Produce:** `tests/{epic}/{sub-epic}/{story}.{tier}.ts` — one GWT file per story per seam. `{tier}` is `front-end`, `back-end`, or any other system name you are proving. No `{story}/` folder and no `*_story` / `*_test_helper` split. Fixtures live in `examples/` and `givens.ts` at the lowest shared epic / sub-epic / story folder.

### Rules

- **`behavioral-observable-outcomes`** — same rule as **scenarios**: assertions stay in domain-observable terms, never internals.
- **`explore-full-interaction-surface`** — same rule as **scenarios**: acceptance_tests must cover the explored interaction surface, not just translate the first main-flow scenario into Playwright. Trace react-hook-form rules, shared validation components, and stubbed failure modes during the sandbox walk-through; add a `scenario()` per distinct behavior.
- **`gwt-steps-trace-to-domain-operations`** — same rule as **scenarios**: each step in the test traces to a named domain operation or property. A hop to the next step is a named operation on the arriving aggregate, not a route or `waitForCompletion()`.
- **`reconcile-live-immediately`** — same rule as **scenarios**: live disagreement updates the sketch before the test is locked.
- **`explain-deep-link-arrival`** — same rule as **scenarios**.
- **`given-only-what-the-system-checks`** — same rule as **scenarios**.
- **`when-holds-the-operation`** — same rule as **scenarios**.
- **`then-and-chaining`** — same rule as **scenarios**.
- **`extract-assertion-helper`** — same rule as **scenarios**.
- **`infrastructure-in-lifecycle-hooks`** — same rule as **scenarios**.
- **`load-with-identity-in-hand`** — same rule as **scenarios**.
- **`seed-prior-story-as-given`** — same rule as **scenarios**.
- **`reuse-owning-aggregate-stubs`** — same rule as **scenarios**.

---

## Templates

### typescript

## scenario-template.ts

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
 * Pattern: GWT structure only — // test code goes here in each step callback.
 */

import { afterAll, beforeAll } from "vitest";
import { background, scenario, story } from "../../story-test";

story("{Story Verb-Noun}", () => {
  beforeAll(async () => {
    // boot — test code goes here
  });

  afterAll(async () => {
    // teardown — test code goes here
  });

  background(({ given }) => {
    given("{background given step}", async () => {
      // test code goes here
    });

    scenario("{surface check — e.g. rules visible}", ({ when, then }) => {
      when("{primary when step}", async () => {
        // test code goes here
      });
      then("{observable surface outcome}", async () => {
        // test code goes here
      });
    });

    scenario("{validation branch while typing}", ({ when, then }) => {
      when("{primary when step}", async () => {
        // test code goes here
      }).and("{follow-on when step}", async () => {
        // test code goes here
      });
      then("{validation message on domain object}", () => {
        // test code goes here
      });
    });

    scenario("{validation clears when input conforms}", ({ when, then }) => {
      when("{primary when step}", async () => {
        // test code goes here
      }).and("{prior invalid state}", async () => {
        // test code goes here
      });
      when("{corrective action}", async () => {
        // test code goes here
      });
      then("{error cleared on domain object}", () => {
        // test code goes here
      });
    });

    scenario("{main-flow outcome}", ({ when, then }) => {
      when("{primary when step}", async () => {
        // test code goes here
      });
      when("{submit operation on domain object}", async () => {
        // test code goes here
      });
      then("{post-condition on loaded aggregate}", async () => {
        // test code goes here
      });
    });
  });
});


## story-test.ts

/**
 * Given / When / Then helpers (Vitest). Copy to tests/story-test.ts once per tests/ tree.
 *
 * ```
 * file: tests/story-test.ts
 * ```
 */

type WhenChain = {
  and: (s: string, fn: () => void | Promise<void>) => WhenChain;
};

type ThenChain = {
  and: (s: string, fn: () => void | Promise<void>) => ThenChain;
};

let activeBackgroundGivens: Array<() => void | Promise<void>> = [];

export function story(name: string, build: () => void): void {
  describe(name, build);
}

export function background(
  build: (steps: { given: (s: string, fn: () => void | Promise<void>) => void }) => void,
): void {
  const givens: Array<() => void | Promise<void>> = [];
  build({
    given: (_s, fn) => givens.push(fn),
  });
  activeBackgroundGivens = givens;
}

export function scenario(
  name: string,
  build: (steps: {
    given: (s: string, fn: () => void | Promise<void>) => void;
    when: (s: string, fn: () => void | Promise<void>) => WhenChain;
    then: (s: string, fn: () => void | Promise<void>) => ThenChain;
  }) => void,
): void {
  describe(name, () => {
    const givens: Array<() => void | Promise<void>> = [];
    const whens: Array<() => void | Promise<void>> = [];
    const thens: Array<{ step: string; fn: () => void | Promise<void> }> = [];
    const pushThen = (s: string, fn: () => void | Promise<void>) => {
      thens.push({ step: s, fn });
    };
    const thenChain: ThenChain = {
      and: (s, fn) => {
        pushThen(s, fn);
        return thenChain;
      },
    };
    const whenChain: WhenChain = {
      and: (s, fn) => {
        whens.push(fn);
        return whenChain;
      },
    };

    build({
      given: (_s, fn) => givens.push(fn),
      when: (_s, fn) => {
        whens.push(fn);
        return whenChain;
      },
      then: (s, fn) => {
        pushThen(s, fn);
        return thenChain;
      },
    });

    beforeAll(async () => {
      for (const g of [...activeBackgroundGivens, ...givens]) {
        await g();
      }
      for (const w of whens) {
        await w();
      }
    });

    thens.forEach(({ step, fn }, i) => {
      it(i === 0 ? `Then ${step}` : step, fn);
    });
  });
}

See examples in `context_tools/stories/examples/` if needed.