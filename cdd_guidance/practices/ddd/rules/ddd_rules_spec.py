"""DDD tactical graph rules — python .examples pairs and sources read by the graph, each rule run as validate runs it."""

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[4]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from expects import equal, expect, have_len
from mamba import before, context, description, it

from cdd_guidance.practices.ddd.rules.rule_examples import DddExamplePair, ddd_fixture, ddd_rule_by_slug, violations_for_ddd_rule
from harness.graph.rule_fixture import SchemaRuleRun

# A toolkit folder with no DDD model, shaped like the harness folders the scanner once misread: a class whose name ends
# in a value object's word, and a class beside a peer named as its repository.
_TOOLKIT = {
    "markdown.py": "class Markdown:\n    def read(self):\n        return ''\n\n\nclass MarkdownRepository:\n    def find(self, name):\n        return name\n",
    "agent_operation.py": "class AgentOperation:\n    def run(self):\n        return None\n\n\nclass Installer:\n    def install(self):\n        return None\n",
}

_ONBOARDING_ROOT = """
/** <<Aggregate Root>> <<Entity>> */
export class Onboarding {
  start(): void {}
}
"""

with description("DDD tactical rules (python .examples)") as self:
    # The first fixture loads the practices' guidance and readers; it is read here once, so no example pays for it.
    with before.all:
        ddd_fixture({"example.py": "class Warm:\n    pass\n"})

    with context("every-class-carries-ddd-stereotype"):
        # The pair's two fixtures are read once; the example checks what the rule reported on them.
        with before.all:
            self.pair = DddExamplePair("every-class-carries-ddd-stereotype")

        with it("should flag a bare Plan beside its aggregate root and accept Plan as a value object"):
            self.pair.check()

        with it("should name the bare class on its aggregate"):
            source = "# <<Aggregate Root>> <<Entity>>\nclass Subscription:\n    pass\n\n\nclass Plan:\n    pass\n"
            expect(violations_for_ddd_rule(ddd_rule_by_slug("every-class-carries-ddd-stereotype"), source)).to(equal(
                ["Class 'Plan' in aggregate 'example' lacks a DDD stereotype (<<Entity>>, <<Repository>>, or code @entity / @repository on the class)."]
            ))

        with it("should keep the bare class as a fact of its aggregate, which a saved graph keeps"):
            fixture = ddd_fixture({"example.py": "# <<Aggregate Root>> <<Entity>>\nclass Subscription:\n    pass\n\n\nclass Plan:\n    pass\n"})
            aggregate = next(node for node in fixture.context.nodes() if node.type == "Aggregate")
            expect(aggregate.facts.get("bare_classes")).to(equal(["Plan"]))

        with context("in a folder no bounded context marks and no class's DDD stereotype models"):
            with it("should make no building block of a class whose name only ends like one"):
                fixture = ddd_fixture(_TOOLKIT, in_bounded_context=False)
                expect([node.name for node in fixture.context.nodes() if node.type != "BoundedContext"]).to(equal([]))

            with it("should report no bare class"):
                fixture = ddd_fixture(_TOOLKIT, in_bounded_context=False)
                expect(SchemaRuleRun(ddd_rule_by_slug("every-class-carries-ddd-stereotype"), fixture.context).hits()).to(equal([]))

        with context("in a folder whose classes carry a DDD stereotype, with no bounded context marked"):
            with it("should still make a building block of a class its name's convention names"):
                files = {"subscription.py": "# <<Aggregate Root>> <<Entity>>\nclass Subscription:\n    pass\n", "plan_code.py": "class PlanCode:\n    pass\n"}
                fixture = ddd_fixture(files, in_bounded_context=False)
                expect(sorted((node.type, node.name) for node in fixture.context.nodes() if node.name in ("Subscription", "PlanCode"))).to(
                    equal([("EntityRoot", "Subscription"), ("ValueObject", "PlanCode")])
                )

        with it("should not require stereotypes on classes in tsx presentation modules"):
            source = """
import type { ComponentType } from 'react';
export class OnboardingStepScreen {
  constructor(readonly View: ComponentType) {}
}
"""
            hits = violations_for_ddd_rule(
                ddd_rule_by_slug("every-class-carries-ddd-stereotype"),
                source,
                filename="onboarding-step-screen.tsx",
                beside={"onboarding.ts": _ONBOARDING_ROOT},
            )
            expect(hits).to(equal([]))

        with it("should accept a value object when the class doc names <<Value Object>>"):
            source = """
/** <<Value Object>> Processor authorization fields for onboarding. */
export class CardAuthorization {
  constructor(
    public readonly transactionIdentifier: string,
    public readonly totalAmount: number,
  ) {}
}
"""
            hits = violations_for_ddd_rule(
                ddd_rule_by_slug("every-class-carries-ddd-stereotype"), source, lang="typescript", filename="payment.ts", beside={"onboarding.ts": _ONBOARDING_ROOT}
            )
            expect(hits).to(equal([]))

        with it("should accept a child entity when the class doc names <<Entity>>"):
            source = """
/** <<Entity>> Tokenized card metadata on the billing account. */
export class PaymentMethod {
  constructor(
    public readonly id: string,
    public readonly brand: string,
  ) {}
}
"""
            hits = violations_for_ddd_rule(
                ddd_rule_by_slug("every-class-carries-ddd-stereotype"), source, lang="typescript", filename="billing.ts", beside={"onboarding.ts": _ONBOARDING_ROOT}
            )
            expect(hits).to(equal([]))

    with context("domain-concepts-not-technical-names"):
        # The pair's two fixtures are read once; the example checks what the rule reported on them.
        with before.all:
            self.pair = DddExamplePair("domain-concepts-not-technical-names", "CartManager", clean_class="Cart")

        with it("should flag CartManager and accept Cart"):
            self.pair.check()

        with it("should flag an aggregate whose folder is named for a manager"):
            hits = violations_for_ddd_rule(
                ddd_rule_by_slug("domain-concepts-not-technical-names"),
                "# <<Entity>>\nclass Cart:\n    pass\n",
                class_name="cart_manager",
                filename="cart_manager/cart.py",
            )
            expect(hits).to(have_len(1))

    with context("flaccid-data-object-no-behavior"):
        # The pair's two fixtures are read once; the example checks what the rule reported on them.
        with before.all:
            self.pair = DddExamplePair("flaccid-data-object-no-behavior", "Cart", clean_class="Product")

        with it("should flag field-only Cart and accept Product with behavior"):
            self.pair.check()

        with it("should not apply to value objects that carry data only"):
            source = """
/** <<Value Object>> */
export class Identity {
  constructor(public email: string, public name = '') {}
}
"""
            hits = violations_for_ddd_rule(
                ddd_rule_by_slug("flaccid-data-object-no-behavior"), source, class_name="Identity", lang="typescript", filename="identity.ts"
            )
            expect(hits).to(equal([]))

        with it("should not apply to a Sim-style value object with only fields"):
            source = """
export const SimType = { Esim: 'eSIM', Psim: 'pSIM' } as const;
export type SimType = (typeof SimType)[keyof typeof SimType];

/** <<Value Object>> */
export class Sim {
  simType: SimType | null;
  iccid: string | null;

  constructor(simType: SimType | null = null, iccid: string | null = null) {
    this.simType = simType;
    this.iccid = iccid;
  }
}
"""
            hits = violations_for_ddd_rule(ddd_rule_by_slug("flaccid-data-object-no-behavior"), source, class_name="Sim", lang="typescript", filename="sim.ts")
            expect(hits).to(equal([]))

    with context("private-method-naming"):
        # The pair's two fixtures are read once; the example checks what the rule reported on them.
        with before.all:
            self.pair = DddExamplePair("private-method-naming", "Other", clean_class="Cart")

        with it("should flag cross-type private access on Other"):
            self.pair.check()

    with context("service-is-homeless"):
        # The pair's two fixtures are read once; the example checks what the rule reported on them.
        with before.all:
            self.pair = DddExamplePair("service-is-homeless", "CheckoutService", clean_class="PricingService")

        with it("should flag CheckoutService and accept a PricingService that does its own work"):
            self.pair.check()

    with context("repository-is-collection-lifecycle"):
        # The pair's two fixtures are read once; the example checks what the rule reported on them.
        with before.all:
            self.pair = DddExamplePair("repository-is-collection-lifecycle", "NoteRepository")

        with it("should flag persist-only NoteRepository"):
            self.pair.check()

    with context("load-with-identity-in-hand"):
        # The pair's two fixtures are read once; the example checks what the rule reported on them.
        with before.all:
            self.pair = DddExamplePair("load-with-identity-in-hand", "CustomerRepository")

        with it("should flag load without identity parameter"):
            self.pair.check()

        with it("should accept a repository that loads the one record it holds"):
            source = """
export class DeviceWalletMerchantCredentialRepository {
  protected credential: DeviceWalletMerchantCredential | null = null;

  load(): DeviceWalletMerchantCredential | null {
    return this.credential;
  }
}
"""
            hits = violations_for_ddd_rule(
                ddd_rule_by_slug("load-with-identity-in-hand"),
                source,
                class_name="DeviceWalletMerchantCredentialRepository",
                lang="typescript",
                filename="payment.ts",
            )
            expect(hits).to(equal([]))

    with context("no-orphaned-objects"):
        # The pair's two fixtures are read once; the example checks what the rule reported on them.
        with before.all:
            self.pair = DddExamplePair("no-orphaned-objects", "LonelyType", clean_class="Cart")

        with it("should flag LonelyType and accept related Cart"):
            self.pair.check()

    with context("screen-interface-not-a-domain-object"):
        # The pair's two fixtures are read once; the example checks what the rule reported on them.
        with before.all:
            self.pair = DddExamplePair("screen-interface-not-a-domain-object", "SelectSim", clean_class="Checkout")

        with it("should flag SelectSim and accept Checkout"):
            self.pair.check()

        with it("should flag a domain service that opens and shows like a screen"):
            source = "# <<Domain Service>>\nclass SimPickerService:\n    def open(self):\n        return None\n\n    def isShowing(self):\n        return True\n"
            hits = violations_for_ddd_rule(ddd_rule_by_slug("screen-interface-not-a-domain-object"), source, class_name="SimPickerService")
            expect(hits).to(have_len(1))

    with context("private-method-naming on TypeScript aggregates"):
        with it("should not flag constructor wiring own _fields and validation state"):
            source = """
export class AccountValidation {
  validationCode = '';
  verified = false;
}
/** <<Aggregate Root>> <<Entity>> */
export class AccountCredentials {
  readonly validation = new AccountValidation();
  protected _email = '';
  constructor(email = '', validationCode = '', verified = false) {
    this._email = email;
    this.validation.validationCode = validationCode;
    this.validation.verified = verified;
  }
  register() {}
}
"""
            hits = violations_for_ddd_rule(
                ddd_rule_by_slug("private-method-naming"), source, class_name="AccountCredentials", lang="typescript", filename="account.ts"
            )
            expect([message for message in hits if "constructor" in message]).to(equal([]))

        with it("should not flag repository lifecycle that delegates snapshot to the aggregate"):
            source = """
export class AccountValidation {
  validationCode = '';
  verified = false;
  _validationCodeSentAt: Date | null = null;
  expectedValidationCode: string | null = null;
  readonly validationCodeMessages = [];
  persistenceSnapshot() { return { validationCode: '', verified: false, _validationCodeSentAt: null, expectedValidationCode: null, validationCodeMessages: [] }; }
  restorePersistenceSnapshot() {}
}
export class AccountCredentials {
  readonly validation = new AccountValidation();
  constructor(email = '', password = '', confirmPassword = '', validationCode = '', verified = false, repository) {
    this._repository = repository;
  }
  _repository;
  get email() { return ''; }
  get password() { return ''; }
  get confirmPassword() { return ''; }
  token = null;
  toStoredAccount() { return { email: '', password: '', confirmPassword: '', validationCode: '', verified: false, token: null, _validationCodeSentAt: null, expectedValidationCode: null, validationCodeMessages: [] }; }
  static fromStored(stored, repository) { return new AccountCredentials('', '', '', '', false, repository); }
}
export class AccountRepository {
  accounts = new Map();
  new() { return new AccountCredentials('', '', '', '', false, this); }
  saveSnapshot(accountCredentials) { this.accounts.set(accountCredentials.email, accountCredentials.toStoredAccount()); }
  hydrate(stored) { return AccountCredentials.fromStored(stored, this); }
}
"""
            hits = violations_for_ddd_rule(
                ddd_rule_by_slug("private-method-naming"), source, class_name="AccountRepository", lang="typescript", filename="account.ts"
            )
            expect(hits).to(equal([]))

        with it("should not flag copyFieldsFrom that mirrors peer fields onto this"):
            source = """
/** <<Aggregate Root>> <<Entity>> */
export class Subscription {
  private _plan = null;
  simType = null;
  copyFieldsFrom(source: Subscription): void {
    this._plan = source._plan;
    this.simType = source.simType;
  }
}
"""
            hits = violations_for_ddd_rule(
                ddd_rule_by_slug("private-method-naming"), source, class_name="Subscription", lang="typescript", filename="subscription.ts"
            )
            expect(hits).to(equal([]))

        with it("should not flag repository attach that wires _repository on the aggregate"):
            source = """
export class CustomerProfile {
  _repository;
}
export class CustomerProfileRepository {
  attach(customerProfile) {
    customerProfile._repository = this;
    return customerProfile;
  }
}
"""
            hits = violations_for_ddd_rule(
                ddd_rule_by_slug("private-method-naming"), source, class_name="CustomerProfileRepository", lang="typescript", filename="customer-profile.ts"
            )
            expect(hits).to(equal([]))
