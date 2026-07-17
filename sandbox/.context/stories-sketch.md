Play Core Mechanics
    * approx 12-16 total stories
    Manage Character Sheet
        Player --> Create Character
            new character has handbook abilities at rank zero
                given no Character yet
                when the Player creates a Character
                then a Character exists with Abilities
                    and each of the eight Abilities has rank 0
        Player --> Update Ability Rank
            ability rank changes on the sheet
                given a Character with Ability {ability_name}
                    and that Ability has rank {starting_rank}
                when the Player updates that Ability rank to {new_rank}
                then that Ability rank equals {new_rank}
                    // example: strength 0 -> 5; PointTotals NOT in this story
        Player --> Refresh Point Totals
        Player --> Update Defense Ranks
        * approx 2-3 more stories (initiative, absent, debilitated)
    Resolve Checks
        Player --> Resolve Ability Check
            ability check reports die total degree and success
                given a Character with Ability as Trait
                    and a DifficultyClass.target
                    and dice that will roll face
                when the Player resolves a Check on that Ability
                then Check.die_roll, CheckResult.total / succeeded / degree are shown
                    // example: strength rank=5, face=8, DC=10 -> total=13, degree=1
        Player --> Resolve Opposed Check
        Player --> Resolve Routine Check
        Player --> Assist Team Check
        * approx 2-3 more stories (comparison, routine opposition, fail/crit)
~> Increment 1: Hero resolves an ability check: Create Character, Update Ability Rank, Resolve Ability Check
