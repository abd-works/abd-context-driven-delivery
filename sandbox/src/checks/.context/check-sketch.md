# module checks

Check
  trait
  dieRoll
  difficultyClass
  dice                              # optional; default 1d20; stub/mock in tests
  resolve modifiers optional: routine
   -> trait.rank
   -> modifiers
   -> difficultyClass
   -> dice.roll                     # face written to dieRoll (unless routine)
  // difficultyClass + dice set at construction
  // routine true: treat die as 10; dieRoll = 10
  // else dice.roll(); dieRoll written (shown to users)
  // natural 20 → +1 degree (critical success; can flip fail→success)
  // degree from margin (±5 bands)

  ----
 OpposedCheck : Check
      opposingTrait
      resolve modifiers optional: comparison, routineOpposition
       // comparison true: trait.rank vs opposingTrait.rank (no die)
       -> trait.rank
       -> opposingTrait.rank
       // routineOpposition true (and not comparison):
       //   DC = opposingTrait.rank + 10 (no opposing roll)
       // else: opposingCheck = Check(opposingTrait, ...) at runtime
       -> opposingCheck.resolve
       // difficultyClass overridden from opposing CheckResult
       -> super.resolve
       // opposed / comparison ties: higher bonus/rank wins, else coin-flip
  ----
 TeamCheck
      addHelper helper
      assist
       -> helper.trait
       // helper is external (e.g. Character); owns trait — not defined here
       // ephemeral Check(helper.trait) vs DC 10 per helper
       // degrees → Modifier (+2 / +5 / −2) for leader resolve
  ----
 Trait
      rank
   -> Rank                    # from measurement module
  ----
 Modifier
      amount
      reason
  ----
 DifficultyClass
      target
  ----
 CheckResult
      succeeded
      total
      degree

# out of scope: AttackCheck (combat later)
