/**
 * @type {import('../../../../stories/code/javascript/seeds/story-types').Story}
 */
export const CreateCharacter = {
  story:       'Create Character',
  actor:       'Player',
  domainTerms: ['Character', 'Abilities', 'Ability', 'Rank'],
  evidence:    ['sandbox/character/.context/module-context.md', 'exploration example: all eight Abilities at rank 0'],

  newCharacterHasHandbookAbilitiesAtRankZero: {
    name: 'new character has handbook abilities at rank zero',
    given: [
      'no Character yet',
    ],
    interactions: [
      {
        when: [
          'the Player creates a Character',
        ],
        then: [
          'a Character exists with Abilities',
          'And each of the eight Abilities has rank 0',
        ],
      },
    ],
  },
}

export const storyNames = ['Create Character']
