"""The OSS Portal rules, proven through the graph a validate run loads: each rule's faulty fixture breaks it and its
repaired fixture passes, so the overlay, the schema, and the rule are checked together."""

import shutil
import tempfile
from pathlib import Path

from expects import contain, equal, expect
from mamba import description, it

from harness.graph.graph import Graph

_PATTERN = Path(__file__).resolve().parents[3]
_AGGREGATE = "src/summer-camp-service/camp-application"

# A small clean aggregate every fixture is laid over, so the overlay finds the service and the aggregate.
_BASE = {
    f"{_AGGREGATE}/camp-application.ts": "export class CampApplication { constructor(readonly id: string) {} }\nexport class CampApplicationRepository {}\n",
    f"{_AGGREGATE}/camp-application-paths.ts": "export const APPLIED_PATH = '/summer-camp/applied';\n",
    f"{_AGGREGATE}/camp-application-bff.ts": "import { CampApplication } from './camp-application';\nimport { APPLIED_PATH } from './camp-application-paths';\nexport class CampApplicationBff extends CampApplication {\n  destination() { return APPLIED_PATH; }\n}\n",
    f"{_AGGREGATE}/camp-application-service.ts": "import { CampApplication, CampApplicationRepository } from './camp-application';\nexport class CampApplicationService extends CampApplication {}\nexport class CampApplicationRepositorySql extends CampApplicationRepository {}\n",
}

_PRACTICE_OF = {
    "service-tier-runs-a-real-database": "stories",
    "journey-test-per-release": "stories",
}


def _fixture(rule, kind):
    practice = _PRACTICE_OF.get(rule, "ddd")
    return _PATTERN / "practices" / practice / "model" / "typescript" / "_examples" / rule / kind


def _violations(rule, kind):
    """slug -> messages, from a graph loaded the way validate loads one, over the base aggregate and the fixture."""
    root = Path(tempfile.mkdtemp(prefix="oss-rules-"))
    for relative, text in _BASE.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    shutil.copytree(_fixture(rule, kind), root, dirs_exist_ok=True)
    graph = Graph()
    roots = {name: str(root) for name in ("clean_engineering", "stories", "ddd", "bdd", "ux")}
    graph.load_working_copy(str(root), roots, database=str(root), overlays=["oss_portal_domain_driven"], force=True)
    found = {}
    for practice in ("ddd", "stories"):
        for node in graph.practice(practice).reading.in_graph.nodes():
            for violation in node.rules.violations:
                found.setdefault(violation.rule, []).append(violation.message)
    return found


_RULES = sorted(path.name for practice in ("ddd", "stories") for path in (_PATTERN / "practices" / practice / "model" / "typescript" / "_examples").iterdir())


with description("the oss_portal_domain_driven pattern rules"):
    with it("should keep a faulty and a repaired fixture for every graph rule"):
        from cdd_guidance.patterns.oss_portal_domain_driven.practices.ddd.rules import BY_SLUG as DDD_RULES
        from cdd_guidance.patterns.oss_portal_domain_driven.practices.stories.rules.oss_story_rules import JourneyTestPerRelease, ServiceTierRunsARealDatabase

        expected = sorted({*DDD_RULES, ServiceTierRunsARealDatabase.slug, JourneyTestPerRelease.slug})
        expect(_RULES).to(equal(expected))

    with description("every faulty fixture"):
        with it("should break the rule it is named for"):
            unflagged = [rule for rule in _RULES if rule not in _violations(rule, "faulty")]
            expect(unflagged).to(equal([]))

    with description("every repaired fixture"):
        with it("should pass the rule its faulty fixture breaks"):
            broken = {rule: _violations(rule, "repaired").get(rule) for rule in _RULES}
            expect({rule: messages for rule, messages in broken.items() if messages}).to(equal({}))
