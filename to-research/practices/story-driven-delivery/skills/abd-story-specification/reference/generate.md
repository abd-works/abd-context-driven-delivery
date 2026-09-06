# Generate — abd-story-specification

## What a stories file is

Each `*-stories.ts` is the single source of truth for a sub-epic. Spec files (`*.spec.ts`) import from it — never from a separate `*-scenarios.ts` file.

One exported `const` per story. The const holds:
- `story` — English display name
- `actor` — primary actor
- `acceptance_criteria` — array of `AcceptanceCriterion[]` (each criterion is a `Step[]`)
- `domain_terms` — key domain concepts
- `evidence` — source files / research docs
- one entry per scenario, keyed by camelCase description

## Plain scenario

No data variation. Each scenario has a `name` and a `steps` array of `Step` objects.

```typescript
import type { Step, AcceptanceCriterion } from '../../story-types'

export const VIEW_SIGN_IN_FORM = {
  story: `View Sign-In Form`,
  actor: `Self-Care Customer`,

  acceptance_criteria: [
    [
      { when: `the **Self-Care Customer** navigates to */sign-in*` },
      { then: `a *"Welcome to Paradise"* heading, Email, Password, and Sign In button are displayed` },
    ],
  ] as const satisfies readonly AcceptanceCriterion[],

  domain_terms: ['self-care customer'] as const,
  evidence: ['extraction/01-sign-in/aria.yaml', 'story-map'] as const,

  signInPageRendersHeadingFieldsAndForgotPasswordLink: {
    name: `sign-in page renders heading, fields, and forgot-password link`,
    steps: [
      { given: `an unauthenticated visitor on */sign-in*` },
      { when: `the sign-in page loads` },
      { then: `*"Welcome to Paradise"* heading is visible` },
      { and: `email and password fields are visible` },
      { and: `*"Sign in"* button is visible` },
      { and: `*"Forgot your password?"* link is visible` },
    ] as const satisfies readonly Step[],
  },
} as const
```

Spec usage:
```typescript
it(VIEW_SIGN_IN_FORM.signInPageRendersHeadingFieldsAndForgotPasswordLink.name, () => { ... })
```

## Scenario outline (data-driven)

Export an `EXAMPLES` array above the story const. Use `{param_name}` placeholders in step strings.

```typescript
import type { Step, AcceptanceCriterion } from '../../story-types'

export const VIEW_SIM_SELECTION_EXAMPLES = [
  { scenario: 'Scenario 1', disable_psim: false, disable_esim: false, esim_shown: true,  psim_shown: true  },
  { scenario: 'Scenario 2', disable_psim: true,  disable_esim: false, esim_shown: true,  psim_shown: false },
  { scenario: 'Scenario 3', disable_psim: false, disable_esim: true,  esim_shown: false, psim_shown: true  },
] as const

export const VIEW_SIM_SELECTION = {
  story: `View SIM Selection`,
  actor: `Onboarding Customer`,

  acceptance_criteria: [
    [
      { when: `the **Onboarding Customer** views the SIM selection step` },
      { then: `each SIM option is shown or hidden based on **GrowthBook** flags` },
    ],
  ] as const satisfies readonly AcceptanceCriterion[],

  domain_terms: ['onboarding customer', 'GrowthBook', 'SIM type'] as const,
  evidence: ['extraction/22-onboarding-select-sim/aria.yaml', 'flags — disable-psim / disable-esim'] as const,

  simOptionsShownOrHiddenBasedOnGrowthBookFlags: {
    name: `SIM options shown or hidden based on GrowthBook flags`,
    steps: [
      { given: `an **Onboarding Customer** on */onboarding/select-sim* with the chosen number displayed` },
      { when: `the customer views the SIM selection step with *disable-psim={disable_psim}* and *disable-esim={disable_esim}*` },
      { then: `eSIM shown: *{esim_shown}*` },
      { and: `pSIM shown: *{psim_shown}*` },
    ] as const satisfies readonly Step[],
  },
} as const
```

Spec usage:
```typescript
it.each(VIEW_SIM_SELECTION_EXAMPLES)(
  `${VIEW_SIM_SELECTION.simOptionsShownOrHiddenBasedOnGrowthBookFlags.name} — $scenario`,
  ({ disable_psim, disable_esim, esim_shown, psim_shown }) => { ... }
)
```

## Fixture constants

Route, expected copy, and fixture imports live at the top of the stories file before the story consts:

```typescript
export const ROUTE = '/sign-in'

export const EXPECTED_ELEMENTS = {
  heading: 'Welcome to Paradise',
  signInButton: 'sign in',
} as const

export { SUBSCRIBER } from '../../fixtures'
```

## Naming rules

| What | Convention |
|------|-----------|
| File | `<sub-epic-slug>-stories.ts` |
| Story const | `SCREAMING_SNAKE` matching the story name |
| Scenario key | `camelCase` full description of the outcome |
| Examples array | `STORY_EXPORT_NAME_EXAMPLES` — `SCREAMING_SNAKE` prefixed with the story const name |
