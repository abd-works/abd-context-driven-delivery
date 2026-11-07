"""
# Conceptual BDD Reference (Python/Mamba style)
# Refer to cdd_guidance/references/language-tools.md for tool recommendations.
# =============================================================================
# BEHAVIOR (SIGNATURE) — `signature-markers`
# Every `it` body is exactly `pass  # BDD: SIGNATURE` — nothing else. A bare comment is not a Python body.
#
# with description('{DomainEntity}'):
#     with context('that has been created'):
#         with it('should have {initial property} assigned'):
#             pass  # BDD: SIGNATURE
# =============================================================================
# REALIZATION — call graph per `it` (default after behavior unless user opts out)
# Replace `# BDD: SIGNATURE` with `# ->` / `# <-` lines only — same notation as CE model.
#
#         with it('should reject an expired token'):
#             # cart.checkout()
#             #   -> paymentGateway.charge(amount)
#             #   <- receipt
#             pass  # BDD: SIGNATURE
# =============================================================================
# DEVELOPMENT — `no-remaining-signatures`
# Replace each `# BDD: SIGNATURE` with Arrange / Act / Assert. Zero markers when done.
# Instructions:
#   1. Replace {DomainEntity} with the class or module under test.
#   2. Use Arrange / Act / Assert comments in test bodies.
#   3. One assertion per behavior.
# =============================================================================
"""
from mamba import description, context, it, before
from expects import equal, expect
from {domain_module} import {DomainEntity}

with description('{DomainEntity}'):
    with context('that has been created'):
        with it('should have {initial property} assigned'):
            # Arrange / Act
            entity = {DomainEntity}(**default_data())
            # Assert
            expect(entity.property).to(equal(expected_value))

    with context('that is {active state}'):
        with before.each:
            self.entity = {DomainEntity}(**default_{related_data}())

        with it('should {behavior description}'):
            # Act
            self.entity.{action}({input})
            # Assert
            expect(self.entity.{property}).to(equal({expected_value}))

        with it('should {second behavior}'):
            # Arrange
            {local_setup} = {value}
            # Act
            self.entity.{action}({local_setup})
            # Assert
            expect(self.entity.{property}).to(equal({expected_value}))


# Rule example pair — mechanical mistake specs use the practice's example harness in harness/graph
# (assert_rule_pair, assert_bdd_source_pair, assert_ddd_example_pair, assert_stories_example_pair).
from ce_rule_eval_harness import assert_rule_pair

with description('the {Rule} rule'):
    with context('on a failing example and its repaired example'):
        with it('should flag only the failing example'):
            assert_rule_pair('{Rule}', {FailSource}, {PassSource})
