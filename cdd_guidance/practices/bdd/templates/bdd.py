"""
# Conceptual BDD Reference (Python/Mamba style)
# Refer to cdd_guidance/rules/language-tools.md for tool recommendations.
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


# Scan fixture pair — mechanical mistake specs use these helpers, not an eval harness.
from cdd_guidance.practices.bdd.spec_helpers import expect_scan_fails, expect_scan_passes

with description('a scan fixture pair'):
    with context('a file that violates the rule'):
        with it('should fail scan'):
            expect_scan_fails({scan}, '{FailFixturePath}', rule='{Rule}')

    with context('a file that satisfies the rule'):
        with it('should pass scan'):
            expect_scan_passes({scan}, '{PassFixturePath}', rule='{Rule}')
