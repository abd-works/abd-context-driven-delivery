# =============================================================================
# BDD Signature Template — Mamba/Python
# =============================================================================
# Instructions (for skill maintainers — delete this block when generating):
#
#   1. Replace {ConceptName} with the top-level domain concept (noun).
#   2. Replace {state description} with the lifecycle state (linking-word phrase).
#   3. Replace {behavior description} with the "should ..." behavior from the scaffold.
#   4. Use `with description()` for top-level concepts and sub-concepts.
#   5. Use `with context()` for state blocks (lifecycle or condition states).
#   6. Use `with it()` for each behavior.
#   7. Every `with it()` body must contain exactly `# BDD: SIGNATURE` and nothing else.
#   8. Delete this instruction block before committing the file.
# =============================================================================
from mamba import description, context, it

with description('{ConceptName}'):
    with context('that has been {state description}'):
        with it('should {behavior description}'):
            # BDD: SIGNATURE
        with it('should {second behavior description}'):
            # BDD: SIGNATURE

    with context('that is {active state description}'):
        with it('should {behavior description}'):
            # BDD: SIGNATURE

    with description('{SubConceptName}'):
        with context('that has {sub-concept state}'):
            with it('should {sub-concept behavior}'):
                # BDD: SIGNATURE

    with context('that has been {completed state}'):
        with it('should {outcome behavior}'):
            # BDD: SIGNATURE
