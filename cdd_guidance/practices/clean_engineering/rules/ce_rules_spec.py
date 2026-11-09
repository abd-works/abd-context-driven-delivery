"""Graph rules — same fault/clean pairs as historical Clean Engineering scanner specs."""

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[4]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from expects import be_true, contain, equal, expect, have_len
from mamba import context, description, it

from harness.graph.rule_fixture import SchemaRuleRun

from cdd_guidance.practices.clean_engineering.rules.fixtures.multi_language_examples import (
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
from cdd_guidance.practices.clean_engineering.rules.rule_examples import assert_module_example_pair
from cdd_guidance.practices.clean_engineering.rules.rule_examples import (
    assert_files_rule_pair,
    assert_python_example_pair,
    practice_from_class_text,
    practice_from_files,
    assert_rule_pair,
    ce_rule_by_slug,
    practice_from_source,
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
                fixture = practice_from_source(
                    source,
                    lang="typescript",
                    filename="api.ts",
                )
                hits = fixture.hits(rule)
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
            fixture = practice_from_source(
                source,
                lang="typescript",
                filename="porting.ts",
            )
            expect(fixture.hits(rule)).to(equal([]))
        with it("should not flag fromFields mapping factories"):
            rule = ce_rule_by_slug("limit-operation-parameters")
            source = """
export class NumberInventorySearch {
  static fromFields(body: { a: string; b: string; c: string; d: string }) {
    void body;
  }
}
"""
            fixture = practice_from_source(
                source,
                lang="typescript",
                filename="numbers.ts",
            )
            expect(fixture.hits(rule)).to(equal([]))
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
            fixture = practice_from_source(
                source,
                lang="typescript",
                filename="account-node.ts",
            )
            hits = fixture.hits(rule)
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
            fixture = practice_from_source(
                source,
                lang="typescript",
                filename="account.ts",
            )
            repo = next(n for n in fixture.practice.in_graph.nodes("OoadClass") if n.name == "AccountRepository")
            context = fixture.context
            expect(SchemaRuleRun(rule, context).node_hits(repo)).to(equal([]))
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
            fixture = practice_from_source(
                source,
                lang="typescript",
                filename="account-client.ts",
            )
            hits = fixture.hits(rule)
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
            fixture = practice_from_source(
                source,
                lang="typescript",
                filename="account-client.ts",
            )
            hits = fixture.hits(rule)
            expect(len(hits)).to(equal(1))
            expect(hits[0]).to(contain("verify"))

        with it("should not flag a TypeScript constructor that sets several fields"):
            source = """
export class AccountCredentialsClient {
  constructor(store: Store) {
    this.validation.validationCode = '';
    this.store.client = store;
    this.validation.verified = false;
  }
}
"""
            fixture = practice_from_source(source, lang="typescript", filename="account-client.ts")
            expect(fixture.hits(ce_rule_by_slug("state-change-returns-record-or-named-failure"))).to(equal([]))

        with it("should not flag a Python __init__ that sets several nested fields"):
            source = """
class Client:
    def __init__(self, store):
        self.validation.code = ''
        self.store.client = store
        self.validation.verified = False
"""
            fixture = practice_from_source(source, filename="client.py")
            expect(fixture.hits(ce_rule_by_slug("state-change-returns-record-or-named-failure"))).to(equal([]))

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
            fixture = practice_from_source(
                source,
                lang="typescript",
                filename="account-client.ts",
            )
            hits = fixture.hits(rule)
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
            fixture = practice_from_source(
                source,
                lang="typescript",
                filename="account-client.ts",
            )
            hits = fixture.hits(rule)
            expect(hits).not_to(equal([]))
        # A Claude Code mod hands every hook its engine as $, the name the mod API documents.
        with it("should allow the engine a Claude Code mod hands its hooks as $"):
            rule = ce_rule_by_slug("use-intention-revealing-names")
            source = """
export function refreshChatBar($: EngineInterface): void {}
"""
            fixture = practice_from_source(
                source,
                lang="typescript",
                filename="chat-bar-client.ts",
            )
            hits = fixture.hits(rule)
            expect(hits).to(equal([]))
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
            fixture = practice_from_source(source, lang="typescript", filename="credentials.tsx")
            expect(fixture.hits(rule)).to(equal([]))
        with it("should still flag an untyped parameter with a default"):
            rule = ce_rule_by_slug("use-typed-signatures")
            source = """
export class Billing {
  enterCardAuthorization(maxAttempts = 1, retry: Record<string, number> = {}): number {
    return maxAttempts + Object.keys(retry).length;
  }
}
"""
            fixture = practice_from_source(source, lang="typescript", filename="billing.ts")
            hits = fixture.hits(rule)
            expect(hits).to(contain("Parameter 'maxAttempts' is missing a type annotation."))
            expect(" ".join(hits)).not_to(contain("retry"))
        with it("should not judge plain JavaScript, which has no syntax for a parameter's type"):
            source = "export class Tree {\n  draw(root, keys) {\n    return root.append(keys);\n  }\n}\n"
            fixture = practice_from_source(source, lang="javascript", filename="screen-tree.js")
            expect(fixture.hits(ce_rule_by_slug("use-typed-signatures"))).to(equal([]))
        with it("should still judge the same parameters in TypeScript"):
            source = "export class Tree {\n  draw(root, keys) {\n    return root.append(keys);\n  }\n}\n"
            fixture = practice_from_source(source, lang="typescript", filename="screen-tree.ts")
            expect(fixture.hits(ce_rule_by_slug("use-typed-signatures"))).to(have_len(2))
        with it("should not flag the cls of a Python classmethod"):
            rule = ce_rule_by_slug("use-typed-signatures")
            source = "class Ticket:\n    @classmethod\n    def load(cls, ticket: str) -> 'Ticket':\n        return cls()\n"
            fixture = practice_from_files({"ticket.py": source})
            expect(fixture.hits(rule)).to(equal([]))
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
            fixture = practice_from_source(source, lang="typescript", filename="sim-client.tsx")
            expect(fixture.hits(rule)).to(equal([]))
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
                fixture = practice_from_files({test_file: text})
                expect(fixture.hits(rule)).to(equal([]))
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

    with context("the examples each rule's guidance shows"):
        with it("should flag a module card that names neither its seam nor its constraint"):
            assert_module_example_pair("named-seam-and-constraint")

        with it("should flag a module importing from more than eight sibling modules"):
            assert_module_example_pair("low-coupling")

        with it("should flag a domain extension kept in the framework package"):
            assert_module_example_pair("extensions-live-with-the-domain")

    with context("named-seam-and-constraint"):
        with it("should accept a bounded context that only has bounded-context.md"):
            import tempfile

            from cdd_guidance.practices.clean_engineering.rules.module_graph_rules import NamedSeamAndConstraint
            from harness.graph.graph import Graph, Node, Source
            from harness.graph.rule_context import RuleCheckContext

            temp = tempfile.TemporaryDirectory()
            root = Path(temp.name)
            context_dir = root / "src" / "customer" / ".context"
            context_dir.mkdir(parents=True)
            (context_dir / "bounded-context.md").write_text(
                "# Customer\n\nAccount, Customer Profile, Identity verification\n",
                encoding="utf-8",
            )
            graph = Graph()
            graph.open(Path(str(root)))
            practice = graph.practice("ddd")
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
            expect(SchemaRuleRun(rule, context).node_hits(node)).to(equal([]))

        with it("should accept a DDD aggregate folder with module-context.md"):
            import tempfile

            from cdd_guidance.practices.clean_engineering.rules.module_graph_rules import NamedSeamAndConstraint
            from harness.graph.graph import Graph, Node, Source
            from harness.graph.rule_context import RuleCheckContext

            temp = tempfile.TemporaryDirectory()
            root = Path(temp.name)
            context_dir = root / "src" / "inventory" / "numbers" / ".context"
            context_dir.mkdir(parents=True)
            (context_dir / "module-context.md").write_text(
                "# numbers\n\n- **Seam (terms):** NumberInventory\n\n## Constraint\n\nUse search flows.\n",
                encoding="utf-8",
            )
            graph = Graph()
            graph.open(Path(str(root)))
            practice = graph.practice("ddd")
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
            expect(SchemaRuleRun(rule, context).node_hits(node)).to(equal([]))


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
            fixture = practice_from_source(source, lang="typescript", filename="select-field.tsx")
            expect(fixture.hits(rule)).to(equal([]))
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
            fixture = practice_from_source(source, lang="typescript", filename="gate.ts")
            expect(fixture.hits(rule)).to(equal(["Operation 'decide' nests control flow 4 levels deep (max 3)."]))

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
        with it("should flag a file built from nothing and accept the file of its own path, named with its failure"):
            assert_rule_pair(
                "use-explicit-dependencies",
                "class CddHome:\n    def __init__(self, folder):\n        self.folder = folder\n        self.state_file = JsonFile()\n",
                (
                    "class CddHome:\n    def __init__(self, folder):\n        self.folder = folder\n"
                    "        self.state_file = JsonFile(self.folder / 'server.json', ServerStateUnreadable)\n"
                ),
            )

        with it("should flag a TypeScript file built from nothing and accept the file of its own path"):
            assert_rule_pair(
                "use-explicit-dependencies",
                "export class CddHome {\n  constructor(private folder: string) {\n    this.stateFile = new JsonFile();\n  }\n}\n",
                (
                    "export class CddHome {\n  constructor(private folder: string) {\n"
                    "    this.stateFile = new JsonFile(folder + '/server.json', ServerStateUnreadable);\n  }\n}\n"
                ),
                lang="typescript",
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
            fixture = practice_from_source(
                source,
                lang="typescript",
                filename="customer-profile.ts",
            )
            hits = fixture.hits(rule)
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
                expect(practice_from_source(source, lang=lang).hits(rule)).to(equal([]))

    with context("never-swallow-exceptions"):
        with it("should flag empty catch in python, typescript, and javascript"):
            _assert_multilang(
                "never-swallow-exceptions",
                _NEVER_SWALLOW_EXCEPTIONS_FAULT,
                _NEVER_SWALLOW_EXCEPTIONS_CLEAN,
            )

        with it("should flag a TypeScript class of many operations and accept a file of as many module functions"):
            functions = "".join(f"  step{index}(): number {{\n    return {index};\n  }}\n" for index in range(11))
            loose = "".join(f"export function step{index}(): number {{\n  return {index};\n}}\n" for index in range(11))
            assert_rule_pair(
                "keep-classes-single-responsibility", f"export class Steps {{\n{functions}}}\n", loose, lang="typescript"
            )

        with it("should flag a handler that drops the failure and accept one that keeps it on its object"):
            for slug in ("never-swallow-exceptions", "use-exceptions-properly"):
                assert_rule_pair(
                    slug,
                    "class Attempt:\n    def run(self):\n        try:\n            self.result = self.work()\n        except Exception:\n            return None\n",
                    (
                        "class Attempt:\n    def run(self):\n        try:\n            self.result = self.work()\n"
                        "        except BaseException as error:\n            self._error = error\n\n"
                        "    def read(self):\n        try:\n            self.lines = self.stream.read()\n"
                        "        except Exception as error:\n            self.thread_errors.append(f'stdout: {error}')\n"
                    ),
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


def _markdown_class_hits(markdown: str) -> list[str]:
    rule = ce_rule_by_slug("write-interactions")
    return practice_from_class_text("Order", markdown, "order.md").hits(rule)


with description("Clean Engineering graph rules (inline fault and clean fixtures)"):
    with context("hide-inner-details"):
        with it("should flag reading another object's private field and accept asking it"):
            assert_rule_pair(
                "hide-inner-details",
                "class Invoice:\n    def total(self, order):\n        return sum(item.price for item in order._items)\n",
                "class Invoice:\n    def total(self, order):\n        return order.total()\n",
            )

        with it("should flag a private member of another class read off a local and accept one its own class declares"):
            assert_rule_pair(
                "hide-inner-details",
                "class Ticket:\n    def move(self, name):\n        moved = self._board.ticket_of(name)\n        return moved._column\n",
                (
                    "import copy\n\n\nclass Ticket:\n"
                    "    def __init__(self, board):\n        self._board = board\n        self._column = ''\n\n"
                    "    def _enter(self, column):\n        self._column = column\n\n"
                    "    def move(self, name, column):\n        moved = self._board.ticket_of(name)\n        moved._enter(column)\n\n"
                    "    def copied(self):\n        made = copy.copy(self)\n        made._column = self._column\n        return made\n\n"
                    "    def alias(self):\n        node = self\n        return node._column\n"
                ),
            )

        with it("should flag a TypeScript method reading another class's private member and accept its own class's"):
            assert_rule_pair(
                "hide-inner-details",
                "export class Ticket {\n  move(board: Board): string {\n    const moved = board.ticketOf();\n    return moved._column;\n  }\n}\n",
                (
                    "export class Ticket {\n  private _column = '';\n\n  _enter(column: string): void {\n    this._column = column;\n  }\n\n"
                    "  move(board: Board): void {\n    const moved = board.ticketOf();\n    moved._enter('done');\n  }\n}\n"
                ),
                lang="typescript",
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

        with it("should flag an ordinary empty case and accept a refused construction and a closed connection"):
            assert_rule_pair(
                "errors-out-of-existence",
                "class Hooks:\n    def find(self, event):\n        if not event:\n            raise ValueError('event is missing')\n        return event\n",
                (
                    "class Hook:\n    def __new__(cls, event=None):\n        if not event:\n"
                    "            raise ValueError('Hook requires an event: @Hook(\"sessionStart\")')\n        return object.__new__(cls)\n\n\n"
                    "class Wire:\n    def received(self, size):\n        chunk = self.conn.recv(size)\n        if not chunk:\n"
                    "            raise OSError('hook daemon closed')\n        return chunk\n"
                ),
            )

    with context("domain-exception-carries-context"):
        with it("should flag a domain exception without a message and accept one that names the rule"):
            assert_rule_pair(
                "domain-exception-carries-context",
                "class Cart:\n    def checkout(self):\n        if self.checked_out:\n            raise CartError()\n        self.checked_out = True\n",
                "class Cart:\n    def checkout(self):\n        if self.checked_out:\n            raise CartError('cart already checked out')\n        self.checked_out = True\n",
            )

        with it("should flag a raise in the body and accept the same raise shown in a docstring"):
            assert_rule_pair(
                "domain-exception-carries-context",
                "class Measure:\n    def refuse(self, paths):\n        if not paths:\n            raise PathsError()\n        return paths\n",
                (
                    'class Measure:\n    def refuse(self, paths):\n        """A missing path is refused, as in\n'
                    '        ``raise PathsError()``."""\n        return paths\n'
                ),
            )

        with it("should flag a failure that writes no message and accept one whose constructor writes its own"):
            raising = "\n\nclass Repo:\n    def commit(self, paths):\n        if not paths:\n            raise CommitPathsRequiredError()\n        return paths\n"
            assert_rule_pair(
                "domain-exception-carries-context",
                "class CommitPathsRequiredError(Exception):\n    pass\n" + raising,
                (
                    "class CommitPathsRequiredError(Exception):\n    def __init__(self) -> None:\n"
                    "        super().__init__('a commit needs the paths it records')\n" + raising
                ),
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
        with it("should accept a domain extension that joins a framework type beside the domain class it extends"):
            expect(
                practice_from_files(
                    {
                        "framework/node.py": "class Node:\n    pass\n",
                        "domain/epic.py": "class Epic:\n    pass\n\n\nclass GraphEpic(Epic, Node):\n    pass\n",
                    }
                ).hits(ce_rule_by_slug("extensions-live-with-the-domain"))
            ).to(equal([]))

        with it("should accept a format class in a package nested under the domain it extends"):
            expect(
                practice_from_files(
                    {
                        "ddd/model/nodes.py": "class Aggregate:\n    pass\n",
                        "ddd/model/markdown/nodes.py": (
                            "from ddd.model.nodes import Aggregate\n\n\nclass MarkdownNode:\n    pass\n\n\n"
                            "class MarkdownAggregate(Aggregate, MarkdownNode):\n    pass\n"
                        ),
                    }
                ).hits(ce_rule_by_slug("extensions-live-with-the-domain"))
            ).to(equal([]))

        with it("should flag a framework holding a domain's extension and accept a format built on the package it extends"):
            assert_files_rule_pair(
                "extensions-live-with-the-domain",
                {
                    "framework/node.py": "class Node:\n    pass\n\n\nclass GraphEpic(Epic, Node):\n    pass\n",
                    "domain/epic.py": "class Epic:\n    pass\n",
                },
                {
                    "model/diagram/nodes.py": "class DiagramClass:\n    pass\n\n\nclass ImportedClass:\n    pass\n",
                    "model/drawio/nodes.py": (
                        "class DrawIOClass(DiagramClass):\n    pass\n\n\n"
                        "class DrawIOImportedClass(ImportedClass, DrawIOClass):\n    pass\n"
                    ),
                },
            )

        with it("should still flag an extension kept in the framework package beside the domain"):
            expect(
                practice_from_files(
                    {
                        "framework/node.py": "class Node:\n    pass\n\n\nclass GraphEpic(Epic, Node):\n    pass\n",
                        "domain/epic.py": "class Epic:\n    pass\n",
                    }
                ).hits(ce_rule_by_slug("extensions-live-with-the-domain"))
            ).to(have_len(1))

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
