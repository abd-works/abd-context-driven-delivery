"""Acme's graph rules on the DDD practice, replacing the practice's rule of the same name."""

from harness.graph.practice_rule import PracticeGraphRule


class NoRepositoryLifecycle(PracticeGraphRule):
    """No aggregate is kept by a repository: the root saves itself."""

    slug = "repository-is-collection-lifecycle"
    node_types = ("Repository",)

    def check(self, node, context):
        return []


RULES: tuple = (NoRepositoryLifecycle(),)

BY_SLUG = {rule.slug: rule for rule in RULES}
