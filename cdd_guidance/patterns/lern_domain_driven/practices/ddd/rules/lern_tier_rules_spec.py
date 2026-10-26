"""LERN tier rules flag the faulty shape and pass the repaired one — reading the tier facts the recorder sets."""

import tempfile
from pathlib import Path

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
from cdd_guidance.patterns.lern_domain_driven.tier_facts import (
    node_root_facts,
    route_facts,
    story_shared_facts,
    test_setup_text,
    web_path_literals,
)
from cdd_guidance.practices.clean_engineering.model.operation_metrics import prototype_swap_in_text
from cdd_guidance.practices.clean_engineering.rules.no_prototype_swapping import NoPrototypeSwapping
from harness.graph.graph import Node, PracticeGraph, Source
from harness.graph.practice_rules_registry import checks_for_practice


def tier_node(name, node_type, facts, file="src/a/a-node.ts"):
    """A graph node carrying the facts the LERN recorder would set on it."""
    node = Node(PracticeGraph("ddd"), node_type, f"ddd:{node_type}:{file}", name, Source(file, 1, 1))
    for key, value in facts.items():
        node.set_fact(key, value)
    return node


with description("the lern_domain_driven pattern rules"):
    with it("should load into the ddd and stories practices only when the overlay is active"):
        expect(list(checks_for_practice("ddd", ("lern_domain_driven",)))).to(contain("node-repository-parses-on-read"))
        expect(list(checks_for_practice("stories", ("lern_domain_driven",)))).to(contain("no-expect-in-given"))
        expect("node-repository-parses-on-read" in checks_for_practice("ddd")).to(equal(False))
        expect(sorted(BY_SLUG)).to(have_len(5))

    with description("node-repository-parses-on-read"):
        with it("should flag a node repository that reads its store without a Zod parse"):
            faulty = "export class XRepositoryNode extends XRepository { constructor() { const raw = JSON.parse(readFileSync(path, 'utf8')); } }"
            messages = NodeRepositoryParsesOnRead().check(tier_node("x-node", "NodeRoot", node_root_facts(faulty, "")), None)
            expect(messages).to(have_len(2))

        with it("should pass a node repository that parses through its document schema"):
            repaired = "export class XRepositoryNode extends XRepository { constructor() { const document = xDocumentSchema.parse(readLowDb(path, {})); } }"
            node = tier_node("x-node", "NodeRoot", node_root_facts(repaired, ""))
            expect(NodeRepositoryParsesOnRead().check(node, None)).to(equal([]))

        with it("should leave a node file without a node repository alone"):
            node = tier_node("x-node", "NodeRoot", node_root_facts("export class XNode extends X {}", ""))
            expect(NodeRepositoryParsesOnRead().check(node, None)).to(equal([]))

    with description("posted-body-parsed-in-node"):
        with it("should flag a route that reads a posted field directly"):
            faulty = "const code = req.body.code;\nconst email = text(req.body?.email);\nconst { plan } = req.body;"
            expect(PostedBodyParsedInNode().check(tier_node("x-routes", "Route", route_facts(faulty)), None)).to(have_len(3))

        with it("should pass a route that hands the request to the node"):
            repaired = "router.post('/x', (req, res) => { const { posted } = XNode.fromRequest(req); });"
            expect(PostedBodyParsedInNode().check(tier_node("x-routes", "Route", route_facts(repaired)), None)).to(equal([]))

    with description("throw-http-exceptions"):
        with it("should flag thrown objects and hand-written error replies"):
            faulty = "throw { status: 400, message: 'bad' };\nres.status(400).json({ message: 'bad' });"
            expect(ThrowHttpExceptions().check(tier_node("x-routes", "Route", route_facts(faulty)), None)).to(have_len(2))

        with it("should pass an HttpException"):
            repaired = route_facts("throw new HttpException(400, 'bad');")
            expect(ThrowHttpExceptions().check(tier_node("x-routes", "Route", repaired), None)).to(equal([]))

    with description("one-home-for-web-paths and reset-every-repository"):
        with before.each:
            self.root = Path(tempfile.mkdtemp())
            folder = self.root / "src" / "revenue" / "subscription"
            folder.mkdir(parents=True)
            (folder / "subscription-paths.ts").write_text("export const CHECKOUT_PATH = '/onboarding/checkout';\n", encoding="utf-8")
            self.node_text = (
                "import { CHECKOUT_PATH } from './subscription-paths';\n"
                "const DONE_PATH = '/onboarding/done';\n"
                "fetch('/api/onboarding/state');\n"
                "router.get('/onboarding/destination', handler);\n"
                "export const subscriptionRepositoryNode = new SubscriptionRepositoryNode();\n"
                "class SubscriptionRepositoryNode {}\n"
            )
            (folder / "subscription-node.ts").write_text(self.node_text, encoding="utf-8")
            (self.root / "tests").mkdir()

        with it("should flag a web path literal outside the paths module and ignore API paths"):
            facts = {"web_path_literals": web_path_literals(self.root, "src/revenue/subscription")}
            messages = OneHomeForWebPaths().check(tier_node("subscription", "Aggregate", facts, file="src/revenue/subscription"), None)
            expect(messages).to(have_len(1))
            expect(messages[0]).to(contain("/onboarding/done"))

        with it("should flag a repository instance the test setup never resets"):
            (self.root / "tests" / "vitest.setup.ts").write_text("otherRepository._reset();\n", encoding="utf-8")
            facts = node_root_facts(self.node_text, test_setup_text(self.root))
            expect(ResetEveryRepository().check(tier_node("subscription-node", "NodeRoot", facts), None)).to(have_len(1))

        with it("should pass once the repositories file lists it"):
            (self.root / "tests" / "repositories.ts").write_text("export const all = [subscriptionRepositoryNode];\n", encoding="utf-8")
            facts = node_root_facts(self.node_text, test_setup_text(self.root))
            expect(ResetEveryRepository().check(tier_node("subscription-node", "NodeRoot", facts), None)).to(equal([]))

    with description("shared story rules"):
        with it("should flag a context cast and pass the tier-bound accessor"):
            cast = story_shared_facts("const repo = ctx.planRepository as PlanRepository;")
            accessor = story_shared_facts("const repo = repositories.plans;")
            expect(TierBoundRepositoryAccessor().check(tier_node("x", "StoryShared", cast), None)).to(have_len(1))
            expect(TierBoundRepositoryAccessor().check(tier_node("x", "StoryShared", accessor), None)).to(equal([]))

        with it("should flag an expect inside a Given and pass one inside a Then"):
            faulty = story_shared_facts("given('the cart has no plan', () => {\n  expect(cart.plan).toBe(null);\n});")
            repaired = story_shared_facts(
                "given('the cart has no plan', () => {\n  cart = emptyCart();\n});\nthen('no plan', () => { expect(cart.plan).toBe(null); });"
            )
            expect(NoExpectInGiven().check(tier_node("x", "StoryShared", faulty), None)).to(have_len(1))
            expect(NoExpectInGiven().check(tier_node("x", "StoryShared", repaired), None)).to(equal([]))

    with description("no-prototype-swapping (Clean Engineering)"):
        with it("should flag a prototype swap and pass a factory"):
            swapped = {"prototype_swap": prototype_swap_in_text("Object.setPrototypeOf(loaded, XNode.prototype);", 1)}
            factory = {"prototype_swap": prototype_swap_in_text("return this.blank(id);", 1)}
            expect(NoPrototypeSwapping().check(tier_node("XRepositoryNode", "OoadClass", swapped), None)).to(have_len(1))
            expect(NoPrototypeSwapping().check(tier_node("XRepositoryNode", "OoadClass", factory), None)).to(equal([]))
