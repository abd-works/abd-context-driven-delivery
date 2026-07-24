# chapter core_mechanics — modules: check | measurement

Check
  trait
  dieRoll                          # set by resolve after rolling — visible to players, not hidden
  difficultyClass
  resolve modifiers
   -> trait.rank
   -> modifiers                    # sum amounts
   -> difficultyClass              # compare total vs target
  // difficultyClass set at construction, not a resolve param
  // dieRoll written during resolve (shown to users)

  ----
 OpposedCheck : Check
      opposingTrait                    # construction — needed for comparison and to build oppose check
      resolve modifiers optonal: comparison
       // comparison true: skip roll/super — rank vs rank
       -> trait.rank
       -> opposingTrait.rank
       // comparison false/absent: opposingCheck = Check(opposingTrait, ...) at runtime
       -> opposingCheck.resolve
       // difficultyClass overridden from opposing CheckResult
       -> super.resolve
       // opposingTrait set at construction; opposing Check is not held
  ----
 Trait
      rank
   -> Rank
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
      degree                         # filled by resolve (graded check)

  ----
 Rank
      value
      toMeasure dimension
      distanceFrom timeRank speedRank
      timeFrom distanceRank speedRank
      throwDistance strengthRank massRank
   
  ----
 MeasurementsTable
      lookup rank dimension
      measureToRank measure dimension
   -> Rank
  ----
 Measure
      amount
      dimension
