/**
 * @type {import('../../../../stories/code/javascript/seeds/story-types').Story}
 */
export const UpdateAbilityRank = {
  story:       'Update Ability Rank',
  actor:       'Player',
  domainTerms: ['Character', 'Ability', 'Rank'],
  evidence:    ['sandbox/character/.context/module-context.md', 'exploration example: strength 0 -> 5; PointTotals not asserted'],

  abilityRankChangesOnTheSheet: {
    name: 'ability rank changes on the sheet',
    given: [
      'a Character with Ability {ability_name}',
      'And that Ability has rank {starting_rank}',
    ],
    interactions: [
      {
        when: [
          'the Player updates that Ability rank to {new_rank}',
        ],
        then: [
          'that Ability rank equals {new_rank}',
        ],
      },
    ],
  },
}

export const storyNames = ['Update Ability Rank']
