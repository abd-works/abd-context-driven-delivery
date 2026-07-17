# module measurement  (chapter: core_mechanics)

Rank
  value
  toMeasure dimension
  distanceFrom timeRank speedRank
  timeFrom distanceRank speedRank
  throwDistance strengthRank massRank
   -> MeasurementsTable.lookup

  ----
 MeasurementsTable
      lookup rank dimension
      measureToRank measure dimension
   -> Rank
  ----
 Measure
      amount
      dimension
