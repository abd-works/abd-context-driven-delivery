"""
# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""
# =============================================================================
# BDD Behavior Template - Mamba/Python SIGNATURE markers only
# =============================================================================
# Instructions (for skill maintainers - delete this block when generating):
#
#   1. Replace {placeholders} from the sketch hierarchy.
#   2. Single implementation → description / context / it only.
#   3. Same behavior on several implementations → shared_context + included_context;
#      included_context string must match shared_context exactly.
#   4. Every it body is exactly `# BDD: SIGNATURE` — no assertions, imports, or setup.
#   5. Delete this instruction block before committing the file.
# =============================================================================
from mamba import description, context, it, shared_context, included_context

# --- single implementation ---

with description('{DomainEntity}'):
    with context('that has been created'):
        with it('should have {initial property} assigned'):
            # BDD: SIGNATURE

    with context('that is {active state}'):
        with it('should {behavior description}'):
            # BDD: SIGNATURE

# --- same behavior, different implementations ---

with shared_context('{abstract subject}'):
    with it('should {shared behavior}'):
        # BDD: SIGNATURE
    with it('should {second shared behavior}'):
        # BDD: SIGNATURE

with description('{story name}'):
    with context('with {Implementation}'):
        with included_context('{abstract subject}'):
            pass
        with it('should {implementation-specific behavior}'):
            # BDD: SIGNATURE
    # Duplicate `with context('with {Implementation}')` per backend.

# =============================================================================
# BDD Development Template - Mamba/Python Test Implementation
# =============================================================================
# Instructions (for skill maintainers - delete this block when generating):
#
#   1. Replace {placeholders} from the sketch.
#   2. Import only the entity under test (and implementations when needed).
#   3. Add a factory for shared test data (`default_{related_data}`).
#   4. Single implementation → use `with description('{DomainEntity}')` below.
#   5. Same behavior on several implementations → use `shared_context` +
#      `included_context`; name the domain subject in `with context('with …')`.
#      Duplicate the `with context('with {Implementation}')` block per backend.
#   6. One observable outcome per `it`; split unrelated expects. No Arrange / Act / Assert labels.
#   7. Replace `# BDD: SIGNATURE` markers - do not leave any in the final file.
#   8. Delete this instruction block before committing the file.
#   9. Keep the edit/check manifest header above - do not strip it.
# =============================================================================
from mamba import description, context, it, before, shared_context, included_context
from expects import equal, be_none, be_true, expect
from {domain_module} import {DomainEntity}


def default_{related_data}() -> dict:
    """Minimal valid test data - populate only fields tests assert on."""
    return {
        # field: value
    }


# -----------------------------------------------------------------------------
# Single implementation
# -----------------------------------------------------------------------------

with description('{DomainEntity}'):
    with context('that has been created'):
        with it('should have {initial property} assigned'):
            entity = {DomainEntity}(**default_{related_data}())
            expect(entity.{property}).to(equal({expected_value}))

    with context('that is {active state}'):
        with before.each:
            self.entity = {DomainEntity}(**default_{related_data}())

        with it('should {behavior description}'):
            self.entity.{action}({input})
            expect(self.entity.{property}).to(equal({expected_value}))


# -----------------------------------------------------------------------------
# Same behavior, different implementations
# Sketch: {abstract subject} → shared it should lines once
#         with {Implementation} → included_context + implementation-only it should
# -----------------------------------------------------------------------------

with shared_context('{abstract subject}'):
    with it('should {shared behavior}'):
        # BDD: SIGNATURE
        pass

    with it('should {second shared behavior}'):
        # BDD: SIGNATURE
        pass


with description('{story name}'):
    with context('with {Implementation}'):
        with included_context('{abstract subject}'):
            pass

        with it('should {implementation-specific behavior}'):
            # BDD: SIGNATURE
            pass

    # Duplicate `with context('with {Implementation}')` for each backend.
    # Change only: context label and implementation-specific it.


# =============================================================================
# CONCRETE EXAMPLE (illustration — map placeholders above to this shape)
# =============================================================================
#
# Sketch:
#
#   Finish request on agent runtime
#     an agent runtime that has accepted a request
#       it should show the runtime as done
#       it should yield the reply
#       with a SubAgent
#         it should leave the reply on doer.out
#       with a CliAgent
#         it should finish when the transcript stops growing
#
# Code:
#
#   with shared_context('an agent runtime that has accepted a request'):
#       with it('should show the runtime as done'):
#           # BDD: SIGNATURE — assert on domain fixture when filled in
#           pass
#
#   with description('Finish request on agent runtime'):
#       with context('with a SubAgent'):
#           with included_context('an agent runtime that has accepted a request'):
#               pass
#           with it('should leave the reply on doer.out'):
#               pass
#
#       with context('with a CliAgent'):
#           with included_context('an agent runtime that has accepted a request'):
#               pass
#           with it('should finish when the transcript stops growing'):
#               pass
#
# SubAgent and CliAgent both run the TWO shared its. Each branch adds ONE extra it.
# =============================================================================


# Scan fixture pair — mechanical mistake specs use these helpers, not an eval harness.
from context_tools.bdd.spec_helpers import expect_scan_fails, expect_scan_passes

with description('a scan fixture pair'):
    with context('a file that violates the rule'):
        with it('should fail scan'):
            expect_scan_fails({scan}, '{FailFixturePath}', rule='{Rule}')

    with context('a file that satisfies the rule'):
        with it('should pass scan'):
            expect_scan_passes({scan}, '{PassFixturePath}', rule='{Rule}')
