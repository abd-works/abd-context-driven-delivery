"""Graph rules — same fault/clean pairs as historical Clean Engineering scanner specs."""

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parents[1]
for path in (_HERE, _REPO):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from expects import be_true, contain, equal, expect
from mamba import context, description, it

from harness.graph.ce_multi_language_fixtures import (
    _ELIMINATE_DUPLICATION_CLEAN,
    _ELIMINATE_DUPLICATION_FAULT,
    _KEEP_OPERATIONS_SMALL_FOCUSED_CLEAN,
    _KEEP_OPERATIONS_SMALL_FOCUSED_FAULT,
    _NEVER_SWALLOW_EXCEPTIONS_CLEAN,
    _NEVER_SWALLOW_EXCEPTIONS_FAULT,
    _SIMPLIFY_CONTROL_FLOW_CLEAN,
    _SIMPLIFY_CONTROL_FLOW_FAULT,
    _USE_CLEAR_FUNCTION_PARAMETERS_CLEAN,
    _USE_CLEAR_FUNCTION_PARAMETERS_FAULT,
    _USE_EXPLICIT_DEPENDENCIES_CLEAN,
    _USE_EXPLICIT_DEPENDENCIES_FAULT,
    _USE_EXCEPTIONS_PROPERLY_CLEAN,
    _USE_EXCEPTIONS_PROPERLY_FAULT,
)
from harness.graph.ce_module_example_harness import assert_module_example_pair
from harness.graph.ce_rule_eval_harness import (
    assert_files_rule_pair,
    assert_python_example_pair,
    practice_from_class_text,
    practice_from_files,
    assert_rule_pair,
    ce_rule_by_slug,
    practice_from_source,
    violations_for_rule,
)

_LANGS = ("python", "typescript", "javascript")

_PYTHON_EXAMPLE_SLUGS = (
    "keep-operations-small-focused",
    "use-explicit-dependencies",
    "eliminate-duplication",
    "avoid-vague-parameter-names",
    "limit-operation-parameters",
    "use-property-not-accessor",
)


def _assert_multilang(slug: str, fault: dict, clean: dict) -> None:
    for lang in _LANGS:
        assert_rule_pair(slug, fault[lang], clean[lang], lang=lang)


def _example_pair(slug: str) -> None:
    assert_python_example_pair(slug)


with description("Clean Engineering graph rules (python .examples pairs)"):
    with context("keep-operations-small-focused"):
        with it("should flag faultyAsset and accept repairedAsset"):
            _example_pair("keep-operations-small-focused")
    with context("use-explicit-dependencies"):
        with it("should flag faultyAsset and accept repairedAsset"):
            _example_pair("use-explicit-dependencies")
    with context("eliminate-duplication"):
        with it("should flag faultyAsset and accept repairedAsset"):
            _example_pair("eliminate-duplication")
    with context("avoid-vague-parameter-names"):
        with it("should flag faultyAsset and accept repairedAsset"):
            _example_pair("avoid-vague-parameter-names")
    with context("limit-operation-parameters"):
        with it("should flag faultyAsset and accept repairedAsset"):
            _example_pair("limit-operation-parameters")
        with it("should allow three domain parameters and flag a fourth"):
            rule = ce_rule_by_slug("limit-operation-parameters")
            ok = """
export class Api {
  send(a: string, b: string, c: string): void {
    void a; void b; void c;
  }
}
"""
            bad = """
export class Api {
  send(a: string, b: string, c: string, d: string): void {
    void a; void b; void c; void d;
  }
}
"""
            for source, expect_hits in ((ok, 0), (bad, 1)):
                practice, root = practice_from_source(
                    source,
                    lang="typescript",
                    filename="api.ts",
                )
                hits = violations_for_rule(rule, practice, root)
                if expect_hits == 0:
                    expect(hits).to(equal([]))
                else:
                    expect(len(hits)).to(equal(1))
                    expect(hits[0]).to(contain("maximum 3, excluding self"))
        with it("should not flag create factories that take many parameters"):
            rule = ce_rule_by_slug("limit-operation-parameters")
            source = """
export class Porting {
  create(a: string, b: string, c: string, d: string, e: string, f: string, g: string) {
    void a; void b; void c; void d; void e; void f; void g;
  }
}
"""
            practice, root = practice_from_source(
                source,
                lang="typescript",
                filename="porting.ts",
            )
            expect(violations_for_rule(rule, practice, root)).to(equal([]))
        with it("should not flag fromFields mapping factories"):
            rule = ce_rule_by_slug("limit-operation-parameters")
            source = """
export class NumberInventorySearch {
  static fromFields(body: { a: string; b: string; c: string; d: string }) {
    void body;
  }
}
"""
            practice, root = practice_from_source(
                source,
                lang="typescript",
                filename="numbers.ts",
            )
            expect(violations_for_rule(rule, practice, root)).to(equal([]))
    with context("use-property-not-accessor"):
        with it("should flag faultyAsset and accept repairedAsset"):
            _example_pair("use-property-not-accessor")
    with context("use-consistent-naming"):
        with it("should flag faultyAsset and accept repairedAsset"):
            _example_pair("use-consistent-naming")
        with it("should not flag constructor or single-word methods as snake_case on a TypeScript class"):
            rule = ce_rule_by_slug("use-consistent-naming")
            source = """
export class AccountCredentialsNode {
  constructor(response?: unknown, cookieHeader?: string) {
    void response;
    void cookieHeader;
  }

  async register(): Promise<void> {}

  async authenticateAccount(): Promise<void> {}

  async signOut(): Promise<void> {}
}
"""
            practice, root = practice_from_source(
                source,
                lang="typescript",
                filename="account-node.ts",
            )
            hits = violations_for_rule(rule, practice, root)
            expect(hits).to(equal([]))
        with it(
            "should not flag a TypeScript repository with single-word lifecycle verbs and camelCase bulk import/export"
        ):
            rule = ce_rule_by_slug("use-consistent-naming")
            source = """
export class AccountRepository {
  new(): void {}
  create(): void {}
  load(): void {}
  find(): void {}
  update(): void {}
  importStoredAccounts(): void {}
  exportStoredAccounts(): void {}
  protected _afterAccountSaved(): void {}
  private saveSnapshot(): void {
    this.accounts.set("x", { email: "a@b.c" });
  }
}
"""
            practice, root = practice_from_source(
                source,
                lang="typescript",
                filename="account.ts",
            )
            repo = next(n for n in practice.nodes.get("OoadClass", []) if n.name == "AccountRepository")
            from harness.graph.rule_context import RuleCheckContext

            context = RuleCheckContext(practice, root)
            expect(rule.check(repo, context)).to(equal([]))
    with context("state-change-returns-record-or-named-failure"):
        with it("should not flag signOut with one property assignment after a post helper"):
            rule = ce_rule_by_slug("state-change-returns-record-or-named-failure")
            source = """
export class AccountCredentialsClient {
  async signOut(): Promise<void> {
    await this._postOperation('/api/account/sign-out', {}, 0, 'Sign-in failed');
    this.token = null;
    this._goToDestination();
  }
}
"""
            practice, root = practice_from_source(
                source,
                lang="typescript",
                filename="account-client.ts",
            )
            hits = violations_for_rule(rule, practice, root)
            expect(hits).to(equal([]))
        with it("should flag verify when two property assignments lack a returned record"):
            rule = ce_rule_by_slug("state-change-returns-record-or-named-failure")
            source = """
export class AccountCredentialsClient {
  async verify(code: string): Promise<void> {
    this.validation.validationCode = code;
    await this._postOperation('/api/account/verify', { code }, 0, 'Mismatch');
    this.validation.verified = true;
  }
}
"""
            practice, root = practice_from_source(
                source,
                lang="typescript",
                filename="account-client.ts",
            )
            hits = violations_for_rule(rule, practice, root)
            expect(len(hits)).to(equal(1))
            expect(hits[0]).to(contain("verify"))
    with context("use-intention-revealing-names"):
        with it("should allow value on a TypeScript property setter"):
            rule = ce_rule_by_slug("use-intention-revealing-names")
            source = """
export class AccountCredentialsClient {
  override set email(value: string) {
    super.email = value;
  }
}
"""
            practice, root = practice_from_source(
                source,
                lang="typescript",
                filename="account-client.ts",
            )
            hits = violations_for_rule(rule, practice, root)
            expect(hits).to(equal([]))
        with it("should still flag value on an ordinary method parameter"):
            rule = ce_rule_by_slug("use-intention-revealing-names")
            source = """
export class AccountCredentialsClient {
  apply(value: string): void {
    this.email = value;
  }
}
"""
            practice, root = practice_from_source(
                source,
                lang="typescript",
                filename="account-client.ts",
            )
            hits = violations_for_rule(rule, practice, root)
            expect(hits).not_to(equal([]))
    with context("prefer-instance-operations"):
        with it("should flag faultyAsset and accept repairedAsset"):
            _example_pair("prefer-instance-operations")
    with context("keep-classes-single-responsibility"):
        with it("should flag faultyAsset and accept repairedAsset"):
            _example_pair("keep-classes-single-responsibility")
    with context("use-typed-signatures"):
        with it("should flag faultyAsset and accept repairedAsset"):
            _example_pair("use-typed-signatures")
        with it("should not flag defaults inside a typed destructured parameter"):
            rule = ce_rule_by_slug("use-typed-signatures")
            source = """
type FieldProps = { label: string; invalid?: boolean };

export function CredentialField({ label, invalid = false }: FieldProps) {
  return invalid ? label : '';
}

export class SubscriptionNode {
  load(id: string, { allowVisitor = false }: { allowVisitor?: boolean } = {}): boolean {
    return Boolean(id) && allowVisitor;
  }
}
"""
            practice, root = practice_from_source(source, lang="typescript", filename="credentials.tsx")
            expect(violations_for_rule(rule, practice, root)).to(equal([]))
        with it("should still flag an untyped parameter with a default"):
            rule = ce_rule_by_slug("use-typed-signatures")
            source = """
export class Billing {
  enterCardAuthorization(maxAttempts = 1, retry: Record<string, number> = {}): number {
    return maxAttempts + Object.keys(retry).length;
  }
}
"""
            practice, root = practice_from_source(source, lang="typescript", filename="billing.ts")
            hits = violations_for_rule(rule, practice, root)
            expect(hits).to(contain("Parameter 'maxAttempts' is missing a type annotation."))
            expect(" ".join(hits)).not_to(contain("retry"))
        with it("should treat withXxx client field changes as properties"):
            rule = ce_rule_by_slug("use-typed-signatures")
            source = """
export class SimClient {
  iccid = '';
  withIccid(iccid = ''): SimClient {
    const next = new SimClient();
    next.iccid = iccid;
    return next;
  }
}
"""
            practice, root = practice_from_source(source, lang="typescript", filename="sim-client.tsx")
            expect(violations_for_rule(rule, practice, root)).to(equal([]))
        with it("should not check test code"):
            rule = ce_rule_by_slug("use-typed-signatures")
            source = """
export class NumberExamples {
  availableMsisdnPool(length = 30): string[] {
    return Array.from({ length }, () => '');
  }
}
"""
            for test_file in ("tests/get-number/number.examples.ts", "src/number.spec.ts", "harness/number_spec.py"):
                text = source if test_file.endswith(".ts") else "class NumberExamples:\n    def pool(self, length=30):\n        return length\n"
                practice, root = practice_from_files({test_file: text})
                expect(violations_for_rule(rule, practice, root)).to(equal([]))
    with context("limit-comments"):
        with it("should flag faultyAsset and accept repairedAsset"):
            _example_pair("limit-comments")
    with context("prefer-class-operations"):
        with it("should flag faultyAsset and accept repairedAsset"):
            _example_pair("prefer-class-operations")
    with context("hide-inner-details"):
        with it("should flag faultyAsset and accept repairedAsset"):
            _example_pair("hide-inner-details")
    with context("do-not-invent-parallel-object-models"):
        with it("should flag faultyAsset and accept repairedAsset"):
            _example_pair("do-not-invent-parallel-object-models")
    with context("shape-classes-around-resources"):
        with it("should flag faultyAsset and accept repairedAsset"):
            _example_pair("shape-classes-around-resources")
    with context("layer-separation"):
        with it("should flag faultyAsset and accept repairedAsset"):
            _example_pair("layer-separation")
    with context("missing-module-context"):
        with it("should flag a folder without module-context.md"):
            assert_module_example_pair("missing-module-context")
    with context("language-modules-one-section"):
        with it("should flag a Modules heading in module-context"):
            assert_module_example_pair("language-modules-one-section")
    with context("modules-not-model-blocks"):
        with it("should flag model dump blocks in module-context"):
            assert_module_example_pair("modules-not-model-blocks")

    with context("named-seam-and-constraint"):
        with it("should accept a bounded context that only has bounded-context.md"):
            import tempfile

            from cdd_guidance.practices.clean_engineering.rules.module_graph_rules import NamedSeamAndConstraint
            from harness.graph.graph import Node, PracticeGraph, Source
            from harness.graph.rule_context import RuleCheckContext

            temp = tempfile.TemporaryDirectory()
            root = Path(temp.name)
            context_dir = root / "src" / "customer" / ".context"
            context_dir.mkdir(parents=True)
            (context_dir / "bounded-context.md").write_text(
                "# Customer\n\nAccount, Customer Profile, Identity verification\n",
                encoding="utf-8",
            )
            practice = PracticeGraph("ddd")
            practice.source_root = str(root)
            practice._temp_dir = temp  # type: ignore[attr-defined]
            rel = "src/customer/.context/bounded-context.md"
            node = Node(
                practice,
                "BoundedContext",
                "ddd:BoundedContext:src/customer:Customer",
                "Customer",
                Source(rel, 1, 3),
            )
            rule = NamedSeamAndConstraint()
            context = RuleCheckContext(practice, root)
            expect(rule.check(node, context)).to(equal([]))

        with it("should accept a DDD aggregate folder with module-context.md"):
            import tempfile

            from cdd_guidance.practices.clean_engineering.rules.module_graph_rules import NamedSeamAndConstraint
            from harness.graph.graph import Node, PracticeGraph, Source
            from harness.graph.rule_context import RuleCheckContext

            temp = tempfile.TemporaryDirectory()
            root = Path(temp.name)
            context_dir = root / "src" / "inventory" / "numbers" / ".context"
            context_dir.mkdir(parents=True)
            (context_dir / "module-context.md").write_text(
                "# numbers\n\n- **Seam (terms):** NumberInventory\n\n## Constraint\n\nUse search flows.\n",
                encoding="utf-8",
            )
            practice = PracticeGraph("ddd")
            practice.source_root = str(root)
            practice._temp_dir = temp  # type: ignore[attr-defined]
            rel = "src/inventory/numbers"
            node = Node(
                practice,
                "Aggregate",
                "ddd:Aggregate:src/inventory/numbers",
                "numbers",
                Source(rel, 1, 1),
            )
            rule = NamedSeamAndConstraint()
            context = RuleCheckContext(practice, root)
            expect(rule.check(node, context)).to(equal([]))


with description("Clean Engineering graph rules (multi-language scanner fixtures)"):
    with context("keep-operations-small-focused"):
        with it("should flag fault snippets in python, typescript, and javascript"):
            _assert_multilang(
                "keep-operations-small-focused",
                _KEEP_OPERATIONS_SMALL_FOCUSED_FAULT,
                _KEEP_OPERATIONS_SMALL_FOCUSED_CLEAN,
            )

    with context("simplify-control-flow"):
        with it("should flag fault snippets in python, typescript, and javascript"):
            _assert_multilang(
                "simplify-control-flow",
                _SIMPLIFY_CONTROL_FLOW_FAULT,
                _SIMPLIFY_CONTROL_FLOW_CLEAN,
            )
        with it("should not count JSX, object literal or arrow-body braces as control flow"):
            rule = ce_rule_by_slug("simplify-control-flow")
            source = """
export function SelectField({ open, options, locked }: { open: boolean; options: string[]; locked: boolean }) {
  const style = { menu: { width: 10 } };
  return (
    <div className="field">
      <div onClick={() => { if (!locked) { choose(style); } }}>{options[0]}</div>
      {open && (
        <ul>
          {options.map(option => (
            <li key={option} onClick={() => { choose({ option }); }}>{`${option}`}</li>
          ))}
        </ul>
      )}
    </div>
  );
}
"""
            practice, root = practice_from_source(source, lang="typescript", filename="select-field.tsx")
            expect(violations_for_rule(rule, practice, root)).to(equal([]))
        with it("should still count control flow nested inside a callback"):
            rule = ce_rule_by_slug("simplify-control-flow")
            source = """
export class Gate {
  decide(items: number[]): void {
    items.forEach(item => {
      for (const step of [item]) {
        while (step > 0) {
          try { if (step > 1) { record(step); } } catch (error) { throw error; }
        }
      }
    });
  }
}
"""
            practice, root = practice_from_source(source, lang="typescript", filename="gate.ts")
            expect(violations_for_rule(rule, practice, root)).to(equal(["Operation 'decide' nests control flow 4 levels deep (max 3)."]))

    with context("eliminate-duplication"):
        with it("should flag fault snippets in python, typescript, and javascript"):
            _assert_multilang(
                "eliminate-duplication",
                _ELIMINATE_DUPLICATION_FAULT,
                _ELIMINATE_DUPLICATION_CLEAN,
            )

    with context("limit-operation-parameters"):
        with it("should flag too many parameters (historical use-clear-function-parameters fault)"):
            _assert_multilang(
                "limit-operation-parameters",
                _USE_CLEAR_FUNCTION_PARAMETERS_FAULT,
                _USE_CLEAR_FUNCTION_PARAMETERS_CLEAN,
            )

    with context("use-explicit-dependencies"):
        with it("should flag constructor `new` in python, typescript, and javascript"):
            _assert_multilang(
                "use-explicit-dependencies",
                _USE_EXPLICIT_DEPENDENCIES_FAULT,
                _USE_EXPLICIT_DEPENDENCIES_CLEAN,
            )
        with it("should allow an Entity aggregate to construct peer types in the same module"):
            rule = ce_rule_by_slug("use-explicit-dependencies")
            source = """
/** <<Value Object>> */
export class Identity {
  constructor(public email: string) {}
}

/** <<Aggregate Root>> <<Entity>> */
export class CustomerProfile {
  constructor(email: string, identity?: Identity) {
    this.identity = identity ?? new Identity(email);
  }
  identity: Identity;
}
"""
            practice, root = practice_from_source(
                source,
                lang="typescript",
                filename="customer-profile.ts",
            )
            hits = violations_for_rule(rule, practice, root)
            expect(hits).to(equal([]))

    with context("use-exceptions-properly"):
        with it("should flag a bare except in python"):
            assert_rule_pair(
                "use-exceptions-properly",
                _USE_EXCEPTIONS_PROPERLY_FAULT["python"],
                _USE_EXCEPTIONS_PROPERLY_CLEAN["python"],
                lang="python",
            )

        with it("should accept the optional catch binding in typescript and javascript"):
            rule = ce_rule_by_slug("use-exceptions-properly")
            for lang in ("typescript", "javascript"):
                source = _USE_EXCEPTIONS_PROPERLY_FAULT[lang]
                expect(violations_for_rule(rule, *practice_from_source(source, lang=lang))).to(equal([]))

    with context("never-swallow-exceptions"):
        with it("should flag empty catch in python, typescript, and javascript"):
            _assert_multilang(
                "never-swallow-exceptions",
                _NEVER_SWALLOW_EXCEPTIONS_FAULT,
                _NEVER_SWALLOW_EXCEPTIONS_CLEAN,
            )


_MODULE_CONTEXT = "# module\n"


def _module(folder: str, files: dict[str, str]) -> dict[str, str]:
    """A module folder: its own module-context.md plus the given source files."""
    tree = {f"{folder}/.context/module-context.md": _MODULE_CONTEXT}
    tree.update({f"{folder}/{name}": text for name, text in files.items()})
    return tree


def _sibling_modules(imported: int) -> dict[str, str]:
    tree = _module("pkg/core", {"core.py": "".join(f"import pkg.part{index}\n" for index in range(imported))})
    for index in range(10):
        tree.update(_module(f"pkg/part{index}", {"part.py": "PART = 1\n"}))
    return tree


def _classes_with_methods(method_count: int) -> str:
    methods = "".join(f"    def act{index}(self):\n        return {index}\n" for index in range(method_count))
    return "".join(f"class Part{index}:\n{methods}\n" for index in range(6))


def _markdown_class_hits(markdown: str) -> list[str]:
    rule = ce_rule_by_slug("write-interactions")
    return violations_for_rule(rule, *practice_from_class_text("Order", markdown, "order.md"))


with description("Clean Engineering graph rules (inline fault and clean fixtures)"):
    with context("put-logic-on-the-owning-resource"):
        with it("should flag reading another object's private field and accept asking it"):
            assert_rule_pair(
                "put-logic-on-the-owning-resource",
                "class Invoice:\n    def total(self, order):\n        return sum(item.price for item in order._items)\n",
                "class Invoice:\n    def total(self, order):\n        return order.total()\n",
            )

    with context("provide-meaningful-context"):
        with it("should flag an unnamed number and accept a named constant"):
            assert_rule_pair(
                "provide-meaningful-context",
                "class Lease:\n    def expiry(self, start):\n        return start + 86400\n",
                "SECONDS_PER_DAY = 86400\n\n\nclass Lease:\n    def expiry(self, start):\n        return start + SECONDS_PER_DAY\n",
            )

    with context("keep-operations-single-responsibility"):
        with it("should flag reading a file and calculating in one operation and accept calculation alone"):
            assert_rule_pair(
                "keep-operations-single-responsibility",
                "class Report:\n    def publish(self, path):\n        rows = open(path).readlines()\n        return calculate_totals(rows)\n",
                "class Report:\n    def publish(self, rows):\n        summary = calculate_totals(rows)\n        return summary.headline\n",
            )

    with context("errors-out-of-existence"):
        with it("should flag raising on an empty input and accept returning a quiet result"):
            assert_rule_pair(
                "errors-out-of-existence",
                "class Cart:\n    def total(self, items):\n        if not items:\n            raise ValueError('cart is empty')\n        return sum(items)\n",
                "class Cart:\n    def total(self, items):\n        if not items:\n            return 0\n        return sum(items)\n",
            )

    with context("domain-exception-carries-context"):
        with it("should flag a domain exception without a message and accept one that names the rule"):
            assert_rule_pair(
                "domain-exception-carries-context",
                "class Cart:\n    def checkout(self):\n        if self.checked_out:\n            raise CartError()\n        self.checked_out = True\n",
                "class Cart:\n    def checkout(self):\n        if self.checked_out:\n            raise CartError('cart already checked out')\n        self.checked_out = True\n",
            )

    with context("no-prototype-swapping"):
        with it("should flag Object.setPrototypeOf on a TypeScript class and accept building the new class"):
            assert_rule_pair(
                "no-prototype-swapping",
                "export class Draft {\n  publish(): void {\n    Object.setPrototypeOf(this, Published.prototype);\n  }\n}\n",
                "export class Draft {\n  publish(): Published {\n    return new Published(this.title);\n  }\n}\n",
                lang="typescript",
            )

    with context("extensions-live-with-the-domain"):
        with it("should flag a Graph epic that stands alone and accept one that extends Epic"):
            assert_rule_pair(
                "extensions-live-with-the-domain",
                "class GraphStoriesEpic:\n    def children(self):\n        return self.stories\n",
                "class GraphStoriesEpic(Epic):\n    def children(self):\n        return self.stories\n",
            )

    with context("write-interactions"):
        with it("should flag a bold Interaction bullet in a markdown class"):
            expect(_markdown_class_hits("# Order\n\n- **Interaction:** Order asks Payment to charge\n")).not_to(equal([]))
        with it("should accept arrow notation in a markdown class"):
            expect(_markdown_class_hits("# Order\n\n- checkout\n  -> payment.charge\n")).to(equal([]))

    with context("one-way-deps"):
        with it("should flag two modules that import each other and accept a one-way import"):
            assert_files_rule_pair(
                "one-way-deps",
                {"orders/order.py": "import billing.invoice\n", "billing/invoice.py": "import orders.order\n"},
                {"orders/order.py": "import billing.invoice\n", "billing/invoice.py": "TAX_RATE = 1\n"},
            )

    with context("low-coupling"):
        with it("should flag a module importing more than eight siblings and accept a narrow fan-out"):
            assert_files_rule_pair("low-coupling", _sibling_modules(9), _sibling_modules(2))

    with context("deep-module"):
        with it("should flag a module of many one-method classes and accept classes with real surface"):
            assert_files_rule_pair(
                "deep-module",
                _module("shapes", {"shapes.py": _classes_with_methods(1)}),
                _module("shapes", {"shapes.py": _classes_with_methods(2)}),
            )

    with context("domain-nouns-only"):
        with it("should flag a verb-named module and accept a domain noun"):
            assert_files_rule_pair(
                "domain-nouns-only",
                _module("process_orders", {"orders.py": "ORDERS = 1\n"}),
                _module("orders", {"orders.py": "ORDERS = 1\n"}),
            )

    with context("no-module-per-class"):
        with it("should flag a module holding one class in one file and accept a cohesive group"):
            assert_files_rule_pair(
                "no-module-per-class",
                _module("orders", {"order.py": "class Order:\n    pass\n"}),
                _module("orders", {"order.py": "class Order:\n    pass\n\n\nclass OrderLine:\n    pass\n"}),
            )
