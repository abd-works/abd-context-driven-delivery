"""Story graph rules — language-agnostic (map / graph shape)."""

from practices.stories.rules.four_to_nine_children import FourToNineChildren
from practices.stories.rules.kebab_case_paths import KebabCasePaths
from practices.stories.rules.scenario_rules import (
    AndChaining,
    BehavioursNotOneTimeTasks,
    BehavioralAndSystemObservableOutcomes,
    BranchOnMechanicalUniqueness,
    ButMarksMissingState,
    ExamplesTraceDomainModel,
    FlaggedWritesIntendedGwt,
    GivenNamesComplexStateRootFirst,
    OutlineRequiresManyPermutations,
    ScenarioNamesContinuation,
    WhenHoldsTheOperation,
    WhenNamesIntentNotInterfaceGesture,
)
from practices.stories.rules.scenarios_shape import ScenariosShape
from practices.stories.rules.ts_story_rules import (
    DomainFixtureExampleFiles,
    DomainOperationInTheStep,
    ExampleRoleNames,
    GwtStepsTraceToDomainOperations,
    OriginatingSubEpicExamples,
)
from practices.stories.rules.story_content_rules import (
    ExamplesExportDataNotRepository,
    PlainEnglishGwtSteps,
    RightSizeStoryNodes,
    StoryNameCapturesSystemMechanic,
    VocabularyTracesToDomainSource,
)
from practices.stories.rules.verb_noun_format import VerbNounFormat

RULES: tuple = (
    FourToNineChildren(),
    VerbNounFormat(),
    ScenariosShape(),
    KebabCasePaths(),
    StoryNameCapturesSystemMechanic(),
    PlainEnglishGwtSteps(),
    RightSizeStoryNodes(),
    VocabularyTracesToDomainSource(),
    ExamplesExportDataNotRepository(),
    GwtStepsTraceToDomainOperations(),
    DomainOperationInTheStep(),
    DomainFixtureExampleFiles(),
    ExampleRoleNames(),
    OriginatingSubEpicExamples(),
    AndChaining(),
    ButMarksMissingState(),
    WhenHoldsTheOperation(),
    OutlineRequiresManyPermutations(),
    ExamplesTraceDomainModel(),
    WhenNamesIntentNotInterfaceGesture(),
    BehavioralAndSystemObservableOutcomes(),
    FlaggedWritesIntendedGwt(),
    BranchOnMechanicalUniqueness(),
    BehavioursNotOneTimeTasks(),
    GivenNamesComplexStateRootFirst(),
    ScenarioNamesContinuation(),
)

BY_SLUG = {rule.slug: rule for rule in RULES}

__all__ = ["BY_SLUG", "RULES"]
