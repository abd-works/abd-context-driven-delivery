/**
 * # @toolset-manifest python -m tools manifest context_tools.stories.stories:Stories
 * # Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
 * # invoke-edit: action satisfy | toolset: context_tools.stories.stories:Stories
 * # invoke-check: action validate | toolset: context_tools.stories.stories:Stories
 *
 * Fidelity: specification (javascript channel)
 * Objects: ResolveChecksHelper → CheckExampleFactory / CheckResultExampleFactory (fake mode)
 */

/**
 * @type {import('../../../../context_tools/stories/code/javascript/seeds/story-types').Story}
 */
export const ResolveAbilityCheck = {
  story:       'Resolve Ability Check',
  actor:       'Player',
  domainTerms: ['Character', 'Ability', 'Trait', 'Check', 'DifficultyClass', 'CheckResult'],
  evidence:    [
    'sandbox/checks/.context/module-context.md',
    'sandbox/character/.context/module-context.md',
    'sandbox/checks/check.spec.js',
    'CheckExampleFactory.loadStrengthCheckFaceEight',
    'CheckExampleFactory.loadStrengthCheckFailsFaceOne',
    'CheckExampleFactory.loadCriticalNaturalTwentyNearMiss',
    'CheckExampleFactory.loadRoutineStrengthCheck',
  ],

  background: [
    'a Player resolving a Check against an Ability usable as a Trait',
  ],

  abilityCheckReportsDieTotalDegreeAndSuccess: {
    name: 'ability check reports die total degree and success',
    given: [
      'a **Check** from helper.givenStrengthCheckFaceEight (**Ability** as **Trait**, **DifficultyClass**, dice face {die_face})',
    ],
    interactions: [
      {
        when: [
          'the Player resolves that **Check**',
        ],
        then: [
          '**Check** die_roll equals {die_face}',
          'And **CheckResult** matches helper.expectedStrengthCheckSucceededDegreeOne (total {expected_total}, succeeded {succeeded}, degree {degree})',
        ],
      },
    ],
    examples: [
      { ability_name: 'strength', ability_rank: '5', difficulty_target: '10', die_face: '8', expected_total: '13', succeeded: 'true', degree: '1' },
    ],
  },

  abilityCheckFailureReportsNegativeDegree: {
    name: 'ability check failure reports negative degree',
    given: [
      'a **Check** from helper.givenStrengthCheckFailsFaceOne (**Ability** as **Trait**, **DifficultyClass**, dice face {die_face})',
    ],
    interactions: [
      {
        when: [
          'the Player resolves that **Check**',
        ],
        then: [
          '**Check** die_roll equals {die_face}',
          'And **CheckResult** matches helper.expectedStrengthCheckFailedDegreeNegOne (total {expected_total}, succeeded {succeeded}, degree {degree})',
        ],
      },
    ],
    examples: [
      { ability_name: 'strength', ability_rank: '5', difficulty_target: '10', die_face: '1', expected_total: '6', succeeded: 'false', degree: '-1' },
    ],
  },

  naturalTwentyAddsDegreeAndCanFlipNearMiss: {
    name: 'natural twenty adds degree and can flip near miss',
    given: [
      'a **Check** from helper.givenCriticalNaturalTwentyNearMiss (**Ability** rank {ability_rank}, **DifficultyClass** {difficulty_target}, dice face {die_face})',
    ],
    interactions: [
      {
        when: [
          'the Player resolves that **Check**',
        ],
        then: [
          '**Check** die_roll equals {die_face}',
          'And **CheckResult** matches helper.expectedCriticalSucceededDegreeOne (total {expected_total}, succeeded {succeeded}, degree {degree})',
        ],
      },
    ],
    examples: [
      { ability_name: 'strength', ability_rank: '0', difficulty_target: '21', die_face: '20', expected_total: '20', succeeded: 'true', degree: '1' },
    ],
  },

  routineCheckTreatsDieAsTen: {
    name: 'routine check treats die as ten',
    given: [
      'a **Check** from helper.givenRoutineStrengthCheck (**Ability** as **Trait**, **DifficultyClass**)',
    ],
    interactions: [
      {
        when: [
          'the Player resolves that **Check** as routine',
        ],
        then: [
          '**Check** die_roll equals {die_face}',
          'And **CheckResult** matches helper.expectedRoutineSucceededDegreeTwo (total {expected_total}, succeeded {succeeded}, degree {degree})',
        ],
      },
    ],
    examples: [
      { ability_name: 'strength', ability_rank: '5', difficulty_target: '10', die_face: '10', expected_total: '15', succeeded: 'true', degree: '2' },
    ],
  },
}

export const storyNames = ['Resolve Ability Check']
