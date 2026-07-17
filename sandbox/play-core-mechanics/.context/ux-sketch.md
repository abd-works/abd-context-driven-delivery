# UX sketch — Play Core Mechanics Increment 1

Fidelity: `mockup`
Stories: Create Character · Update Ability Rank · Resolve Ability Check.

```
═══════════════════════════════════════════════════════════
  SITE MAP
═══════════════════════════════════════════════════════════

character sheet
  └─ [action] resolve check on ability ──→ resolve check

resolve check
  └─ [action] dismiss result ────────────→ character sheet

═══════════════════════════════════════════════════════════
  SCREENS
═══════════════════════════════════════════════════════════

[ character sheet ]                                 sidebar
  ┌────────────────┬────────────────────────────┐
  │ ▼ Characters   │ Abilities                  │
  │   › Hero ‹     ├────────────────────────────┤
  │                │ ability · rank             │
  │                │ › strength · 5 ‹           │
  │                │ agility · 0                │
  │                │ [ Create Character ]       │
  │                │ [ Update Rank ] [ Check ]  │
  └────────────────┴────────────────────────────┘
  Stories (~2): Create Character · Update Ability Rank
  Domain terms: Character · Ability · Rank
  key:
    tree · list · [ btn ] button
    ›sel‹ selected
    on [ Create Character ] → add Character under tree (abilities rank 0)
    on [ Update Rank ] → bump selected Ability rank; sheet stays consistent
    on [ Check ] → resolve check (ability prefilled)

[ resolve check ]                                   modal
  ┌─────────────────────────────┐
  │ ability [ strength    ▾ ]   │
  │ DC [ 10____ ]               │
  │ [ Resolve ]                 │
  │─────────────────────────────│
  │ die · total · degree        │
  │ face 8 · total 13 · deg 1   │
  │ succeeded                   │
  │ [ Done ]                    │
  └─────────────────────────────┘
  Stories (~1): Resolve Ability Check
  Domain terms: Check · DifficultyClass · CheckResult
  key:
    [▾] dropdown · [____] text · [ btn ] button
    on [ Resolve ] → show result (stub roll)
    on [ Done ] → character sheet

// context: rank update must leave sheet consistent before check
```
