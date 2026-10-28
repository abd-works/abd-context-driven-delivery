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
    DomainOperationsInlineInSteps,
    NoExpectInGiven,
    OutlineRowsLoopOverExamples,
    TierBoundRepositoryAccessor,
)
from cdd_guidance.patterns.lern_domain_driven.tier_facts import (
    core_request_reads,
    node_root_facts,
    route_facts,
    story_file_facts,
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


def node_root(text, setup_text=""):
    return tier_node("x-node", "NodeRoot", node_root_facts(text, setup_text))


def route(text):
    return tier_node("x-routes", "Route", route_facts(text))


def story_file(text, node_type="StoryShared"):
    return tier_node("x.story.shared.ts", node_type, story_file_facts(text), file="tests/x/x.story.shared.ts")


with description("the lern_domain_driven pattern rules"):
    with it("should load into the ddd and stories practices only when the overlay is active"):
        expect(list(checks_for_practice("ddd", ("lern_domain_driven",)))).to(contain("node-repository-parses-on-read"))
        expect(list(checks_for_practice("stories", ("lern_domain_driven",)))).to(contain("no-expect-in-given"))
        expect(list(checks_for_practice("stories", ("lern_domain_driven",)))).to(contain("domain-operations-inline-in-steps"))
        expect("node-repository-parses-on-read" in checks_for_practice("ddd")).to(equal(False))
        expect(sorted(BY_SLUG)).to(have_len(5))

    with description("node-repository-parses-on-read"):
        with it("should flag a node repository that reads its store without a Zod parse"):
            faulty = "export class XRepositoryNode extends XRepository { constructor() { const raw = JSON.parse(readFileSync(path, 'utf8')); } }"
            expect(NodeRepositoryParsesOnRead().check(node_root(faulty), None)).to(have_len(2))

        with it("should pass a node repository that parses through its document schema"):
            repaired = "export class XRepositoryNode extends XRepository { constructor() { const document = xDocumentSchema.parse(readLowDb(path, {})); } }"
            expect(NodeRepositoryParsesOnRead().check(node_root(repaired), None)).to(equal([]))

        with it("should follow a store read into a same-file helper the repository calls"):
            faulty = (
                "const storePath = join(here, 'numbers.json');\n"
                "function readNumbers() { return JSON.parse(readFileSync(storePath, 'utf8')); }\n"
                "export class NumberRepositoryNode extends NumberRepository { constructor() { this.rows = readNumbers(); } }"
            )
            expect(NodeRepositoryParsesOnRead().check(node_root(faulty), None)).to(have_len(2))

        with it("should leave a wrapper repository that never reads a store alone"):
            wrapper = "export class OnboardingRepositoryNode extends XRepositoryNode { load(p) { return this._inner.load(p); } }"
            expect(NodeRepositoryParsesOnRead().check(node_root(wrapper), None)).to(equal([]))

        with it("should leave a node file without a node repository alone"):
            expect(NodeRepositoryParsesOnRead().check(node_root("export class XNode extends X {}"), None)).to(equal([]))

    with description("posted-body-parsed-in-node"):
        with it("should flag a route that reads a posted field directly"):
            faulty = "const code = req.body.code;\nconst email = text(req.body?.email);\nconst { plan } = req.body;"
            expect(PostedBodyParsedInNode().check(route(faulty), None)).to(have_len(3))

        with it("should flag a node that reads the posted body without a schema"):
            faulty = "static fromRequest(req) {\n  const posted = req.body ?? {};\n  return new XNode(String(req.body?.code ?? ''));\n}"
            expect(PostedBodyParsedInNode().check(node_root(faulty), None)).to(have_len(2))

        with it("should pass a node that parses the posted body with its schema"):
            repaired = "static fromRequest(req) {\n  const posted = postedSchema.parse(req.body ?? {});\n  const merged = postedSchema.parse({ ...(req.query ?? {}), ...(req.body ?? {}) });\n}"
            expect(PostedBodyParsedInNode().check(node_root(repaired), None)).to(equal([]))

        with it("should pass a route that hands the request to the node"):
            repaired = "router.post('/x', (req, res) => { const { posted } = XNode.fromRequest(req); });"
            expect(PostedBodyParsedInNode().check(route(repaired), None)).to(equal([]))

    with description("throw-http-exceptions"):
        with it("should flag thrown objects and hand-written error replies"):
            faulty = "throw { status: 400, message: 'bad' };\nres.status(400).json({ message: 'bad' });"
            expect(ThrowHttpExceptions().check(route(faulty), None)).to(have_len(2))

        with it("should pass an HttpException"):
            expect(ThrowHttpExceptions().check(route("throw new HttpException(400, 'bad');"), None)).to(equal([]))

    with description("one-home-for-web-paths and reset-every-repository"):
        with before.each:
            self.root = Path(tempfile.mkdtemp())
            self.folder = "src/revenue/subscription"
            folder = self.root / self.folder
            folder.mkdir(parents=True)
            (folder / "subscription-paths.ts").write_text("export const CHECKOUT_PATH = '/onboarding/checkout';\n", encoding="utf-8")
            self.node_text = (
                "import { CHECKOUT_PATH } from './subscription-paths';\n"
                "const DONE_PATH = '/onboarding/done';\n"
                "fetch('/api/onboarding/state');\n"
                "router.get('/onboarding/destination', handler);\n"
                "export const subscriptionRepositoryNode = new SubscriptionRepositoryNode();\n"
                "class SubscriptionRepositoryNode { constructor() { readLowDb(path, {}); } }\n"
            )
            (folder / "subscription-node.ts").write_text(self.node_text, encoding="utf-8")
            (self.root / "tests").mkdir()

        with it("should flag a web path literal outside the paths module and ignore API paths"):
            facts = {"web_path_literals": web_path_literals(self.root, self.folder)}
            messages = OneHomeForWebPaths().check(tier_node("subscription", "Aggregate", facts, file=self.folder), None)
            expect(messages).to(have_len(1))
            expect(messages[0]).to(contain("/onboarding/done"))

        with it("should not read a path named in a comment"):
            (self.root / self.folder / "subscription-node.ts").write_text(
                "/**\n * Sign-up opens on the plan catalog (pml-my `/sign-up/`).\n */\n"
                "const step = SIGN_UP_PATH; // pml-my redirects to '/sign-up/'\n",
                encoding="utf-8",
            )
            expect(web_path_literals(self.root, self.folder)).to(equal([]))

        with it("should flag the core reading the request"):
            (self.root / self.folder / "subscription.ts").write_text(
                "export class Sim { static fromRequest(req) { const body = req.body ?? {}; } }\n", encoding="utf-8")
            facts = {"core_request_reads": core_request_reads(self.root, self.folder)}
            messages = PostedBodyParsedInNode().check(tier_node("subscription", "Aggregate", facts, file=self.folder), None)
            expect(messages).to(have_len(1))
            expect(messages[0]).to(contain("framework-free core"))

        with it("should flag a repository instance the test setup never resets"):
            (self.root / "tests" / "vitest.setup.ts").write_text("otherRepository._reset();\n", encoding="utf-8")
            expect(ResetEveryRepository().check(node_root(self.node_text, test_setup_text(self.root)), None)).to(have_len(1))

        with it("should pass once the repositories file lists it"):
            (self.root / "tests" / "repositories.ts").write_text("export const all = [subscriptionRepositoryNode];\n", encoding="utf-8")
            expect(ResetEveryRepository().check(node_root(self.node_text, test_setup_text(self.root)), None)).to(equal([]))

        with it("should pass once the step library's repositories file lists it"):
            library = self.root / "test-utils" / "story-test"
            library.mkdir(parents=True)
            (library / "repositories.ts").write_text("export const all = [subscriptionRepositoryNode];\n", encoding="utf-8")
            expect(ResetEveryRepository().check(node_root(self.node_text, test_setup_text(self.root)), None)).to(equal([]))

    with description("shared story rules"):
        with it("should flag a context cast and pass the tier-bound accessor"):
            expect(TierBoundRepositoryAccessor().check(story_file("const repo = ctx.planRepository as PlanRepository;"), None)).to(have_len(1))
            expect(TierBoundRepositoryAccessor().check(story_file("const repo = repositories.plans;"), None)).to(equal([]))

        with it("should flag an expect inside a Given and pass one inside a Then"):
            faulty = "given('the cart has no plan', () => {\n  expect(cart.plan).toBe(null);\n});"
            repaired = "given('the cart has no plan', () => {\n  cart = emptyCart();\n});\nthen('no plan', () => { expect(cart.plan).toBe(null); });"
            expect(NoExpectInGiven().check(story_file(faulty), None)).to(have_len(1))
            expect(NoExpectInGiven().check(story_file(repaired), None)).to(equal([]))

        with it("should flag a story-file helper that wraps a repository call and pass the call inline"):
            faulty = (
                "async function reloadAccount(): Promise<AccountCredentials> {\n"
                "  const stored = await repositories.credentials.load(lookup);\n"
                "  return stored;\n"
                "}\n"
                "then('the account holds a token', async () => {\n"
                "  expect((await reloadAccount()).isLoggedIn).toBe(true);\n"
                "});\n"
            )
            repaired = (
                "then('the account holds a token', async () => {\n"
                "  const stored = await repositories.credentials.load(accountCredentials);\n"
                "  expect(stored?.isLoggedIn).toBe(true);\n"
                "});\n"
            )
            expect(DomainOperationsInlineInSteps().check(story_file(faulty), None)).to(have_len(1))
            expect(DomainOperationsInlineInSteps().check(story_file(repaired), None)).to(equal([]))

        with it("should flag an outline row written by hand and pass the examples loop"):
            faulty = "scenario('Address requirement is unmet: parish', ({ when }) => {});\n"
            repaired = "expectedUnmetAddressOutlines.forEach(({ field }) => {\n  scenario(`Address requirement is unmet: ${field}`, ({ when }) => {});\n});\n"
            expect(OutlineRowsLoopOverExamples().check(story_file(faulty, "PlaywrightSpec"), None)).to(have_len(1))
            expect(OutlineRowsLoopOverExamples().check(story_file(repaired, "PlaywrightSpec"), None)).to(equal([]))

        with it("should leave a screen gesture helper alone"):
            gesture = (
                "async function signInOnScreen(page: Page, email: string): Promise<void> {\n"
                "  await page.getByLabel('Email').fill(email);\n"
                "}\n"
            )
            expect(DomainOperationsInlineInSteps().check(story_file(gesture, "PlaywrightSpec"), None)).to(equal([]))

    with description("no-prototype-swapping (Clean Engineering)"):
        with it("should flag a prototype swap and pass a factory"):
            swapped = {"prototype_swap": prototype_swap_in_text("Object.setPrototypeOf(loaded, XNode.prototype);", 1)}
            factory = {"prototype_swap": prototype_swap_in_text("return this.blank(id);", 1)}
            expect(NoPrototypeSwapping().check(tier_node("XRepositoryNode", "OoadClass", swapped), None)).to(have_len(1))
            expect(NoPrototypeSwapping().check(tier_node("XRepositoryNode", "OoadClass", factory), None)).to(equal([]))
