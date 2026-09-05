"""
# Story acceptance GWT (Python/Mamba) — same runner as BDD development specs.
# Refer to context_tools/bdd/gwt.py for the story-test.ts → Mamba mapping.
# =============================================================================
# Instructions:
#   1. Top level: with description('{Story Verb-Noun}')
#   2. Boot/teardown: with before.all / with after.all (not in given contexts)
#   3. Shared Given: with context('given …') + with before.each
#   4. Each outcome branch: with context('{scenario}') + when in before.each + it for Then
#   5. Chain When steps in one before.each; chain Then as sibling it blocks
# =============================================================================
"""
from expects import be_above, be_none, equal, expect
from mamba import after, before, context, description, it

from {domain_module} import {DomainEntity}


with description('{Story Verb-Noun}'):
    with before.all:
        self.{app_camel} = {AppFactory}.initialize({config})

    with after.all:
        if getattr(self, '{app_camel}', None) is not None:
            self.{app_camel}.close()

    with context('given {background given step}'):
        with before.each:
            self.{app_camel}.{background_operation}()

        with context('{surface check — e.g. rules visible}'):
            with before.each:
                self.{aggregate_camel} = self.{app_camel}.{primary_when_operation}()

            with it('should {observable surface outcome}'):
                self.{aggregate_camel}.{field} = {invalid_value}
                self.{aggregate_camel}.validate()
                expect(len(self.{aggregate_camel}.errors.{field})).to(be_above(0))

        with context('{validation branch while typing}'):
            with before.each:
                self.{aggregate_camel} = self.{app_camel}.{primary_when_operation}()
                self.{aggregate_camel}.{field} = {invalid_value}
                self.{aggregate_camel}.validate()

            with it('should {validation message on domain object}'):
                expect(self.{aggregate_camel}.errors.{field}).to(equal({ERROR_CONSTANT}_MESSAGE))

        with context('{validation clears when input conforms}'):
            with before.each:
                self.{aggregate_camel} = self.{app_camel}.{primary_when_operation}()
                self.{aggregate_camel}.{field} = {invalid_value}
                self.{aggregate_camel}.validate()
                self.{aggregate_camel}.{field} = {valid_value}
                self.{aggregate_camel}.validate()

            with it('should {error cleared on domain object}'):
                expect(self.{aggregate_camel}.errors.{field}).to(be_none)

        with context('{main-flow outcome}'):
            with before.each:
                self.{aggregate_camel} = self.{app_camel}.{primary_when_operation}()
                self.{aggregate_camel}.{field} = {valid_aggregate_value}
                self.{aggregate_camel}.{operation}()

            with it('should {post-condition on loaded aggregate}'):
                {entity_camel} = self.{app_camel}.{repository}().load(self.{aggregate_camel})
                expect({entity_camel}.is_at_{state}('{StateName}')).to(equal(True))
