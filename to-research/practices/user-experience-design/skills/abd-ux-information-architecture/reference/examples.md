# abd-information-architecture — Examples

## The shape of a good initial IA

The reference pattern — each tab state is its own screen, list regions show representative rows, actions are a verb row, chrome is named but not described, and each screen carries ~4 stories.

```
[ game directory prompt ]                          modal dialog
  ┌─────────────────────────────┐
  │ COH game directory          │  — label only
  │ directory path · browse     │  — field labels only
  │ validation feedback         │  — conditional region label
  │ continue                    │  — action gate
  └─────────────────────────────┘
  Stories (~2): Validate Game Directory · Prompt if Invalid
  Domain terms: COH game directory

       │ submits valid path
       ▼

[ crowd manager — identities ]                     left panel + body
  ┌────────────────┬────────────────────────────┐
  │ crowd tree     │ [ Identities ] Abilities   │  ← inactive tabs greyed; crowd tree
  │ (chrome,       │   Movements                │    uses --slot panel in sidebar layout
  │ --slot panel)  ├────────────────────────────┤    so it renders beside body, not above
  │                │ identity row: name · type  │  ← representative row 1
  │                │   active / default         │
  │                │ identity row: name · type  │  ← representative row 2
  │                │   active / default         │
  │                │ add · remove · set default │  ← verb row (light fill, black border)
  │                │   set active · reorder     │
  └────────────────┴────────────────────────────┘
  Stories (~4): Add Identity · Set Default Identity · Set Active Identity · Remove Identity
  Domain terms: identity · model identity · costume identity · active identity · default identity

  ↓ selects Abilities tab                ↓ selects Movements tab

[ crowd manager — abilities ]           [ crowd manager — movements ]
  ┌────────────────┬──────────────────┐   ┌────────────────┬──────────────────┐
  │ crowd tree     │ Identities       │   │ crowd tree     │ Identities       │
  │ (--panel left, │ [Abilities]      │   │ (--panel left, │ Abilities        │
  │  --dimmed)     │ Movements        │   │  --dimmed)     │ [Movements]      │
  │                ├──────────────────┤   │                ├──────────────────┤
  │                │ ability row      │   │                │ movement row     │
  │                │ ability row      │   │                │ movement row     │
  │                │ create · delete  │   │                │ add · remove     │
  │                │ play · stop      │   │                │ set default      │
  │                │ set key · edit   │   │                │ set key · edit   │
  └────────────────┴──────────────────┘   └────────────────┴──────────────────┘
  crowd tree dimmed (--dimmed) = grey fill    crowd tree dimmed (--dimmed) = grey fill
  signals "same chrome as primary screen"     signals "same chrome as primary screen"

  edit──► [ ability editor screen ]
  Stories (~4): Create Animated Ability       Stories (~3): Add Movement
    Delete · Set Key · Toggle Persistence       Edit Movement Parameters
  Domain terms: animated ability              Domain terms: character movement
```

No screen carries toolbar actions, navigation content, acceptance criteria, controls, copy, or wireframe-level detail. If a screen has more than ~4 user stories, a tab state or edit screen is missing.
