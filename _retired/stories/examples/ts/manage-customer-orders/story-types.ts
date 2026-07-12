// story-types.ts
// Shared types for every `<story>-stories.ts` file in this epic.
// See ../story-context.md for how these types relate to the story map.
//
// Steps are just ordered strings. Author writes the FIRST of each phase
// unprefixed; the runner adds `Given/When/Then` in the report label.
// Continuation steps carry their own `And ` or `But ` prefix as part of the
// string — the tier class uses that same string as its key.

export type Interaction = {
  readonly when: readonly string[]
  readonly then: readonly string[]
}

export type Scenario = {
  readonly name: string
  readonly given: readonly string[]
  readonly interactions: readonly Interaction[]
}

export type Story = {
  readonly story: string
  readonly actor: string
  readonly domainTerms: readonly string[]
  readonly evidence: readonly string[]
} & { readonly [key: string]: Scenario | string | readonly string[] }

// A step is either sync or async — pure-domain steps don't need `async`.
export type StepFn = () => void | Promise<void>

// The tier-implementation contract, derived from the scenario at compile time.
// Keys of `given` / `when` / `then` are exactly the strings the scenario declares.
export type TierImpl<S extends Scenario> = {
  given: { [K in S['given'][number]]: StepFn }
  when: { [K in S['interactions'][number]['when'][number]]: StepFn }
  then: { [K in S['interactions'][number]['then'][number]]: StepFn }
  cleanup: StepFn
}
