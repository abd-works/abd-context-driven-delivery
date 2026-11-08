"""Story graph rules, one module per fidelity."""

from cdd_guidance.practices.stories.rules.acceptance_tests import (
    DomainFixtureExampleFiles,
    ExampleRoleNames,
    ExamplesExportDataNotRepository,
)
from cdd_guidance.practices.stories.rules.scenarios import (
    AndChaining,
    BehavioralAndSystemObservableOutcomes,
    ButMarksMissingState,
    ExamplesTraceDomainModel,
    FlaggedWritesIntendedGwt,
    GivenNamesComplexStateRootFirst,
    GwtStepsTraceToDomainOperations,
    OutlineRequiresManyPermutations,
    PlainEnglishGwtSteps,
    ScenarioNamesContinuation,
    ScenariosShape,
    WhenHoldsTheOperation,
    WhenNamesIntentNotInterfaceGesture,
)
from cdd_guidance.practices.stories.rules.story_map import (
    BehavioursNotOneTimeTasks,
    BranchOnMechanicalUniqueness,
    FourToNineChildren,
    KebabCasePaths,
    StoryScenariosAtMostSeven,
    RightSizeStoryNodes,
    StoryNameCapturesSystemMechanic,
    VerbNounFormat,
)

RULES: tuple = (
    FourToNineChildren(),
    StoryScenariosAtMostSeven(),
    VerbNounFormat(),
    ScenariosShape(),
    KebabCasePaths(),
    StoryNameCapturesSystemMechanic(),
    PlainEnglishGwtSteps(),
    RightSizeStoryNodes(),
    ExamplesExportDataNotRepository(),
    GwtStepsTraceToDomainOperations(),
    DomainFixtureExampleFiles(),
    ExampleRoleNames(),
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
