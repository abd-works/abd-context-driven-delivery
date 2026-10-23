"""LERN tier rules flag the faulty shape and pass the repaired one."""

import tempfile
from pathlib import Path
from types import SimpleNamespace

from expects import contain, equal, expect, have_len
from mamba import before, description, it

from cdd_guidance.patterns.lern_domain_driven.practices.ddd.rules import BY_SLUG
from cdd_guidance.patterns.lern_domain_driven.practices.ddd.rules.lern_tier_rules import (
    NodeRepositoryParsesOnRead,
    OneHomeForWebPaths,
    PostedBodyParsedInNode,
    ResetEveryRepository,
    ThrowHttpExceptions,
)
from cdd_guidance.patterns.lern_domain_driven.practices.stories.rules.shared_story_rules import (
    NoExpectInGiven,
    TierBoundRepositoryAccessor,
)
from cdd_guidance.practices.clean_engineering.rules.no_prototype_swapping import NoPrototypeSwapping
from harness.graph.practice_rules_registry import checks_for_practice


def node(name, node_type, file="src/a/a-node.ts"):
    return SimpleNamespace(name=name, type=node_type, source=SimpleNamespace(file=file, start_line=1, end_line=1))


def context(text, root=None):
    return SimpleNamespace(text=lambda _node: text, span=lambda _node: text, source_root=root)


with description("the lern_domain_driven pattern rules"):
    with it("should load into the ddd and stories practices only when the overlay is active"):
        expect(list(checks_for_practice("ddd", ("lern_domain_driven",)))).to(contain("node-repository-parses-on-read"))
        expect(list(checks_for_practice("stories", ("lern_domain_driven",)))).to(contain("no-expect-in-given"))
        expect("node-repository-parses-on-read" in checks_for_practice("ddd")).to(equal(False))
        expect(sorted(BY_SLUG)).to(have_len(5))

    with description("node-repository-parses-on-read"):
        with it("should flag a node repository that reads its store without a Zod parse"):
            faulty = "export class XRepositoryNode extends XRepository { constructor() { const raw = JSON.parse(readFileSync(path, 'utf8')); } }"
            messages = NodeRepositoryParsesOnRead().check(node("x-node", "NodeRoot"), context(faulty))
            expect(messages).to(have_len(2))

        with it("should pass a node repository that parses through its document schema"):
            repaired = "export class XRepositoryNode extends XRepository { constructor() { const document = xDocumentSchema.parse(readLowDb(path, {})); } }"
            expect(NodeRepositoryParsesOnRead().check(node("x-node", "NodeRoot"), context(repaired))).to(equal([]))

        with it("should leave a node file without a node repository alone"):
            expect(NodeRepositoryParsesOnRead().check(node("x-node", "NodeRoot"), context("export class XNode extends X {}"))).to(equal([]))

    with description("posted-body-parsed-in-node"):
        with it("should flag a route that reads a posted field directly"):
            faulty = "const code = req.body.code;\nconst email = text(req.body?.email);\nconst { plan } = req.body;"
            expect(PostedBodyParsedInNode().check(node("x-routes", "Route"), context(faulty))).to(have_len(3))

        with it("should pass a route that hands the request to the node"):
            repaired = "router.post('/x', (req, res) => { const { posted } = XNode.fromRequest(req); });"
            expect(PostedBodyParsedInNode().check(node("x-routes", "Route"), context(repaired))).to(equal([]))

    with description("throw-http-exceptions"):
        with it("should flag thrown objects and hand-written error replies"):
            faulty = "throw { status: 400, message: 'bad' };\nres.status(400).json({ message: 'bad' });"
            expect(ThrowHttpExceptions().check(node("x-routes", "Route"), context(faulty))).to(have_len(2))

        with it("should pass an HttpException"):
            expect(ThrowHttpExceptions().check(node("x-routes", "Route"), context("throw new HttpException(400, 'bad');"))).to(equal([]))

    with description("one-home-for-web-paths and reset-every-repository"):
        with before.each:
            self.root = Path(tempfile.mkdtemp())
            folder = self.root / "src" / "revenue" / "subscription"
            folder.mkdir(parents=True)
            (folder / "subscription-paths.ts").write_text("export const CHECKOUT_PATH = '/onboarding/checkout';\n", encoding="utf-8")
            (folder / "subscription-node.ts").write_text(
                "import { CHECKOUT_PATH } from './subscription-paths';\n"
                "const DONE_PATH = '/onboarding/done';\n"
                "fetch('/api/onboarding/state');\n"
                "router.get('/onboarding/destination', handler);\n"
                "export const subscriptionRepositoryNode = new SubscriptionRepositoryNode();\n",
                encoding="utf-8",
            )
            (self.root / "tests").mkdir()
            self.aggregate = node("subscription", "Aggregate", file="src/revenue/subscription")

        with it("should flag a web path literal outside the paths module and ignore API paths"):
            messages = OneHomeForWebPaths().check(self.aggregate, context("", self.root))
            expect(messages).to(have_len(1))
            expect(messages[0]).to(contain("/onboarding/done"))

        with it("should flag a repository instance the test setup never resets"):
            (self.root / "tests" / "vitest.setup.ts").write_text("otherRepository._reset();\n", encoding="utf-8")
            text = (self.root / "src/revenue/subscription/subscription-node.ts").read_text(encoding="utf-8")
            node_file = node("subscription-node", "NodeRoot", file="src/revenue/subscription/subscription-node.ts")
            expect(ResetEveryRepository().check(node_file, context(text + "class SubscriptionRepositoryNode {}", self.root))).to(have_len(1))

        with it("should pass once the repositories file lists it"):
            (self.root / "tests" / "repositories.ts").write_text("export const all = [subscriptionRepositoryNode];\n", encoding="utf-8")
            text = (self.root / "src/revenue/subscription/subscription-node.ts").read_text(encoding="utf-8")
            node_file = node("subscription-node", "NodeRoot", file="src/revenue/subscription/subscription-node.ts")
            expect(ResetEveryRepository().check(node_file, context(text + "class SubscriptionRepositoryNode {}", self.root))).to(equal([]))

    with description("shared story rules"):
        with it("should flag a context cast and pass the tier-bound accessor"):
            story = node("x.story.shared.ts", "StoryShared", file="tests/x/x.story.shared.ts")
            expect(TierBoundRepositoryAccessor().check(story, context("const repo = ctx.planRepository as PlanRepository;"))).to(have_len(1))
            expect(TierBoundRepositoryAccessor().check(story, context("const repo = repositories.plans;"))).to(equal([]))

        with it("should flag an expect inside a Given and pass one inside a Then"):
            story = node("x.story.shared.ts", "StoryShared", file="tests/x/x.story.shared.ts")
            faulty = "given('the cart has no plan', () => {\n  expect(cart.plan).toBe(null);\n});"
            repaired = "given('the cart has no plan', () => {\n  cart = emptyCart();\n});\nthen('no plan', () => { expect(cart.plan).toBe(null); });"
            expect(NoExpectInGiven().check(story, context(faulty))).to(have_len(1))
            expect(NoExpectInGiven().check(story, context(repaired))).to(equal([]))

    with description("no-prototype-swapping (Clean Engineering)"):
        with it("should flag a prototype swap and pass a factory"):
            operation = node("XRepositoryNode", "OoadClass")
            expect(NoPrototypeSwapping().check(operation, context("Object.setPrototypeOf(loaded, XNode.prototype);"))).to(have_len(1))
            expect(NoPrototypeSwapping().check(operation, context("return this.blank(id);"))).to(equal([]))
