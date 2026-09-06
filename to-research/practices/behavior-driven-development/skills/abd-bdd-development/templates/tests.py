# =============================================================================
# BDD Development Template — Mamba/Python Test Implementation
# =============================================================================
# Instructions (for skill maintainers — delete this block when generating):
#
#   1. Replace {DomainEntity} with the class or module under test.
#   2. Import only the entity under test.
#   3. Add a factory function for shared test-data objects.
#   4. Use `with before.each:` for shared object setup when 3+ siblings need it.
#   5. Each `with it():` body uses # Arrange / # Act / # Assert comments.
#   6. One assertion per behavior.
#   7. Replace `# BDD: SIGNATURE` markers — do not leave any in the final file.
#   8. Delete this instruction block before committing the file.
# =============================================================================
from mamba import description, context, it, before
from expects import equal, be_none, be_true, expect
from {domain_module} import {DomainEntity}


def default_{related_data}() -> dict:
    """Minimal valid test data — populate only fields tests assert on."""
    return {
        # field: value
    }


with description('{DomainEntity}'):
    with context('that has been created'):
        with it('should have {initial property} assigned'):
            # Arrange / Act
            entity = {DomainEntity}(**default_{related_data}())
            # Assert
            expect(entity.{property}).to(equal({expected_value}))

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
