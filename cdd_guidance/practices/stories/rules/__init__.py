"""Story graph rules, one module per fidelity."""

from cdd_guidance.practices.stories.rules.acceptance_tests import (
    CodeStepsInvokeCode,
    DomainFixtureExampleFiles,
    ExampleRoleNames,
    ExamplesExportDataNotRepository,
)
from cdd_guidance.practices.stories.rules.scenarios import (
    AndChaining,
    BehavioralAndSystemObservableOutcomes,
    ButMarksMissingState,
    DomainTermsLinkToModel,
    ExamplesTraceDomainModel,
    FlaggedWritesIntendedGwt,
    GivenNamesComplexStateRootFirst,
    GwtStepsTraceToDomainOperations,
    OutlineRequiresManyPermutations,
    PlainEnglishGwtSteps,
    ScenarioNamesContinuation,
    ScenariosNameAStoryOnTheMap,
    ScenariosShape,
    WhenHoldsTheOperation,
    WhenNamesIntentNotInterfaceGesture,
)
from cdd_guidance.practices.stories.rules.story_map import (
    BehavioursNotOneTimeTasks,
    BranchOnMechanicalUniqueness,
    ChildCountFitsLayer,
    KebabCasePaths,
    StoryScenariosAtMostSeven,
    RightSizeStoryNodes,
    StoryNameCapturesSystemMechanic,
    VerbNounFormat,
)

RULES: tuple = (
    ChildCountFitsLayer(),
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
    CodeStepsInvokeCode(),
    ExampleRoleNames(),
    AndChaining(),
    ButMarksMissingState(),
    WhenHoldsTheOperation(),
    OutlineRequiresManyPermutations(),
    ExamplesTraceDomainModel(),
    DomainTermsLinkToModel(),
    WhenNamesIntentNotInterfaceGesture(),
    BehavioralAndSystemObservableOutcomes(),
    FlaggedWritesIntendedGwt(),
    BranchOnMechanicalUniqueness(),
    BehavioursNotOneTimeTasks(),
    GivenNamesComplexStateRootFirst(),
    ScenarioNamesContinuation(),
    ScenariosNameAStoryOnTheMap(),
)

BY_SLUG = {rule.slug: rule for rule in RULES}

__all__ = ["BY_SLUG", "RULES"]
