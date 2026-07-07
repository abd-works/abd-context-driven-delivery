// {lowest-sub-epic}-stories.js

export const BACKGROUND = [{ given: '<shared precondition>' }]

// ── Story 1 — main-flow only (Exploration fidelity) ──────────────────────────

export const VerbNounMainFlow = {
  story: '<Story Verb–Noun — main flow>',
  actor: '<Actor Name>',

  mainFlow: {
    name: '<happy-path scenario name>',
    steps: [
      { given: 'a **<ConceptA>** *<value>*' },
      { when:  'the **<actor>** *<value>* <triggering action>' },
      { then:  'the **<observed concept>** is *<observable outcome>*' },
      { and:   '<additional outcome>' },
    ],
  },
}

// ── Story 2 — inline (Specification fidelity) ─────────────────────────────────

export const VerbNounInline = {
  story: '<Story Verb–Noun — inline>',
  actor: '<Actor Name>',

  mainFlow: {
    name: '<main-flow scenario name>',
    steps: [
      { given: 'a **<ConceptA>** *<value>*' },
      { when:  'the **<actor>** *<value>* <triggering action>' },
      { then:  'the **<observed concept>** is *<observable outcome>*' },
      { and:   '<additional outcome>' },
    ],
  },

  negativePath: {
    name: '<negative scenario name>',
    steps: [
      { given: '<alternate precondition>' },
      { when:  '<alternate action>' },
      { then:  '<negative outcome>' },
      { but:   '<state that does NOT change>' },
    ],
  },
}

// ── Story 3 — outline (Specification fidelity, data-driven) ───────────────────

export const VerbNounOutline = {
  story: '<Story Verb–Noun — outline>',
  actor: '<Actor Name>',

  mainFlow: {
    name: '<scenario outline name>',
    steps: [
      { given: 'a **<ConceptA>** *<amount>*' },
      { when:  'the **<actor>** submits with *<method>*' },
      { then:  'the result is *<outcome>*' },
    ],
    examples: [
      { amount: '<value 1>', method: '<method 1>', outcome: '<outcome 1>' },
      { amount: '<value 2>', method: '<method 2>', outcome: '<outcome 2>' },
    ],
  },
}

// ── Story 4 — stub ───────────────────────────────────────────────────────────
// On the story map this is a named card in the sub-epic row — title and actor
// only. No scenarios yet. Appears as a sticky on the wall; nothing to run.

export const VerbNounStub = {
  story: '<Story Verb–Noun — stub>',
  actor: '<Actor Name>',
  // no scenarios — story is on the map but not yet specified
}
