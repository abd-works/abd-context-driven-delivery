"""DDD tactical graph rules — python .examples pairs."""

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parents[1]
for path in (_HERE, _REPO):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from expects import equal, expect
from mamba import context, description, it

from harness.graph.ddd_rule_eval_harness import assert_ddd_example_pair, ddd_rule_by_slug, violations_for_ddd_rule

with description("DDD tactical rules (python .examples)"):
    with context("building-blocks-fidelity-requires-tactical-stereotype"):
        with it("should flag Plan without stereotype and accept PlanEntity"):
            assert_ddd_example_pair(
                "building-blocks-fidelity-requires-tactical-stereotype",
                "Plan",
                clean_class="PlanEntity",
            )

        with it("should not require stereotypes on classes in tsx presentation modules"):
            source = """
import type { ComponentType } from 'react';
export class OnboardingStepScreen {
  constructor(readonly View: ComponentType) {}
}
"""
            rule = ddd_rule_by_slug("building-blocks-fidelity-requires-tactical-stereotype")
            hits = violations_for_ddd_rule(
                rule,
                source,
                class_name="OnboardingStepScreen",
                node_type="Entity",
                lang="typescript",
                filename="onboarding-step-screen.tsx",
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
            rule = ddd_rule_by_slug("building-blocks-fidelity-requires-tactical-stereotype")
            hits = violations_for_ddd_rule(
                rule,
                source,
                class_name="CardAuthorization",
                node_type="ValueObject",
                lang="typescript",
                filename="payment.ts",
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
            rule = ddd_rule_by_slug("building-blocks-fidelity-requires-tactical-stereotype")
            hits = violations_for_ddd_rule(
                rule,
                source,
                class_name="PaymentMethod",
                node_type="Entity",
                lang="typescript",
                filename="billing.ts",
            )
            expect(hits).to(equal([]))

    with context("domain-concepts-not-technical-names"):
        with it("should flag CartManager and accept Cart"):
            assert_ddd_example_pair(
                "domain-concepts-not-technical-names",
                "CartManager",
                clean_class="Cart",
            )

    with context("flaccid-data-object-no-behavior"):
        with it("should flag field-only Cart and accept Product with behavior"):
            assert_ddd_example_pair(
                "flaccid-data-object-no-behavior",
                "Cart",
                clean_class="Product",
            )

        with it("should not apply to value objects that carry data only"):
            source = """
export class Identity {
  constructor(public email: string, public name = '') {}
}
"""
            rule = ddd_rule_by_slug("flaccid-data-object-no-behavior")
            hits = violations_for_ddd_rule(
                rule,
                source,
                class_name="Identity",
                node_type="ValueObject",
                lang="typescript",
                filename="identity.ts",
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
            rule = ddd_rule_by_slug("flaccid-data-object-no-behavior")
            hits = violations_for_ddd_rule(
                rule,
                source,
                class_name="Sim",
                node_type="ValueObject",
                lang="typescript",
                filename="sim.ts",
            )
            expect(hits).to(equal([]))

    with context("private-method-naming"):
        with it("should flag cross-type private access on Other"):
            assert_ddd_example_pair(
                "private-method-naming",
                "Other",
                clean_class="Cart",
            )

    with context("service-is-homeless"):
        with it("should flag CheckoutService and accept behavior on Cart"):
            assert_ddd_example_pair(
                "service-is-homeless",
                "CheckoutService",
                clean_class="Cart",
                node_type="DomainService",
            )

    with context("repository-is-collection-lifecycle"):
        with it("should flag persist-only NoteRepository"):
            assert_ddd_example_pair("repository-is-collection-lifecycle", "NoteRepository", node_type="Repository")

    with context("load-with-identity-in-hand"):
        with it("should flag load without identity parameter"):
            assert_ddd_example_pair("load-with-identity-in-hand", "CustomerRepository", node_type="Repository")

    with context("no-orphaned-objects"):
        with it("should flag LonelyType and accept related Cart"):
            assert_ddd_example_pair("no-orphaned-objects", "LonelyType", clean_class="Cart")

    with context("screen-interface-not-a-domain-object"):
        with it("should flag SelectSim and accept Checkout"):
            assert_ddd_example_pair(
                "screen-interface-not-a-domain-object",
                "SelectSim",
                clean_class="Checkout",
            )

    with context("private-method-naming on TypeScript aggregates"):
        with it("should not flag constructor wiring own _fields and validation state"):
            source = """
export class AccountValidation {
  validationCode = '';
  verified = false;
}
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
            rule = ddd_rule_by_slug("private-method-naming")
            hits = violations_for_ddd_rule(
                rule,
                source,
                class_name="AccountCredentials",
                node_type="EntityRoot",
                lang="typescript",
                filename="account.ts",
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
            rule = ddd_rule_by_slug("private-method-naming")
            hits = violations_for_ddd_rule(
                rule,
                source,
                class_name="AccountRepository",
                node_type="Repository",
                lang="typescript",
                filename="account.ts",
            )
            expect(hits).to(equal([]))

        with it("should not flag copyFieldsFrom that mirrors peer fields onto this"):
            source = """
export class Subscription {
  private _plan = null;
  simType = null;
  copyFieldsFrom(source: Subscription): void {
    this._plan = source._plan;
    this.simType = source.simType;
  }
}
"""
            rule = ddd_rule_by_slug("private-method-naming")
            hits = violations_for_ddd_rule(
                rule,
                source,
                class_name="Subscription",
                node_type="EntityRoot",
                lang="typescript",
                filename="subscription.ts",
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
            rule = ddd_rule_by_slug("private-method-naming")
            hits = violations_for_ddd_rule(
                rule,
                source,
                class_name="CustomerProfileRepository",
                node_type="Repository",
                lang="typescript",
                filename="customer-profile.ts",
            )
            expect(hits).to(equal([]))
