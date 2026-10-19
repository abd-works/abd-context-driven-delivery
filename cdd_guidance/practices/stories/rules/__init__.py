"""Story graph rules, one module per fidelity."""

from cdd_guidance.practices.stories.rules.acceptance_tests import (
    DomainFixtureExampleFiles,
    ExampleRoleNames,
    ExamplesExportDataNotRepository,
    OriginatingSubEpicExamples,
)
from cdd_guidance.practices.stories.rules.scenarios import (
    AndChaining,
    BehavioralAndSystemObservableOutcomes,
    ButMarksMissingState,
    DomainOperationInTheStep,
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
    EvidenceDistinguishesObservedInferredAndIntended,
    FourToNineChildren,
    KebabCasePaths,
    RightSizeStoryNodes,
    StoryNameCapturesSystemMechanic,
    VerbNounFormat,
)

RULES: tuple = (
    FourToNineChildren(),
    VerbNounFormat(),
    ScenariosShape(),
    KebabCasePaths(),
    StoryNameCapturesSystemMechanic(),
    PlainEnglishGwtSteps(),
    RightSizeStoryNodes(),
    EvidenceDistinguishesObservedInferredAndIntended(),
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
