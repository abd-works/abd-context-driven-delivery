"""BDD spec for OssPortalDomainDriven - construction, the rules its markdown states, and where they apply."""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import be_a, be_true, equal, expect
from mamba import before, context, description, it

from cdd_guidance.patterns.oss_portal_domain_driven.oss_portal_domain_driven import OssPortalDomainDriven
from harness.guidance.rule import RulesCollection

_MODULE_DIR = Path(__file__).resolve().parent

_ALL_RULE_SLUGS = (
    "aggregate-folder-holds-every-tier",
    "service-is-the-bounded-context",
    "screens-live-in-their-domain",
    "tier-classes-extend-the-domain",
    "maintain-layer-purity",
    "browser-calls-only-the-bff",
    "tokens-stay-on-the-server",
    "bff-decides-next-page",
    "views-render-only",
    "gov-bm-blocked-at-four-layers",
    "staff-roles-from-entra-claims",
    "one-proxy-per-service",
    "standard-policy-chain",
    "version-breaking-changes",
    "sanitised-errors-only",
    "one-database-per-service",
    "no-cross-service-tables",
    "repository-owns-aggregate-lifecycle",
    "attachments-in-cloud-storage",
    "cache-holds-nothing-authoritative",
    "reporting-reads-bigquery",
    "expand-and-contract-migrations",
    "revision-rollback-safe",
    "publish-events-from-the-owning-service",
    "idempotent-subscribers",
    "integrate-through-application-integration",
    "content-from-system-config",
    "secrets-from-secret-manager",
    "no-personal-data-in-logs",
    "least-data-in-responses",
    "build-once-promote-digest",
    "register-every-service",
    "label-every-resource",
    "reduce-story-overlap",
    "service-tier-runs-a-real-database",
    "journey-test-per-release",
    "no-expect-in-given",
    "outline-entries-loop-over-examples",
    "scaffold-test-scripts",
    "ask-cross-aggregate-sync",
)

with description("an OssPortalDomainDriven pattern"):
    with before.each:
        self.tool = OssPortalDomainDriven()

    with context("that has been constructed"):
        with it("should default format to typescript"):
            expect(self.tool.format).to(equal("typescript"))

        with it("should key on oss_portal_domain_driven"):
            expect(self.tool.key).to(equal("oss_portal_domain_driven"))

        with it("should resolve module_dir to this package"):
            expect(self.tool.module_dir).to(equal(_MODULE_DIR))

    with context("whose instructions are expanded"):
        with before.each:
            self.rendered = self.tool.scoped_markdown()

        with it("should name every rule"):
            missing = [slug for slug in _ALL_RULE_SLUGS if slug not in self.rendered]
            expect(missing).to(equal([]))

        with it("should cite the handover pack"):
            expect("Handover Pack" in self.rendered).to(be_true)

    with context("whose rules collection is loaded"):
        with before.each:
            self.rules = self.tool.rules

        with it("should hold every rule"):
            expect(self.rules).to(be_a(RulesCollection))
            expect(len(list(self.rules))).to(equal(len(_ALL_RULE_SLUGS)))

        with it("should apply to an aggregate's BFF file"):
            expect(self.rules.applies_to.matches("src/summer-camp-service/camp-application/camp-application-bff.ts")).to(equal(True))

        with it("should apply to a service migration"):
            expect(self.rules.applies_to.matches("src/summer-camp-service/migrations/0007-expand-add-seat-preference.sql")).to(equal(True))

        with it("should not apply to a LERN node file"):
            expect(self.rules.applies_to.matches("src/online-portal/form/form-node.ts")).to(equal(False))
