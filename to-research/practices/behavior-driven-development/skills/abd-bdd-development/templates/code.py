# =============================================================================
# BDD Development Template — Python Production Module
# =============================================================================
# Instructions (for skill maintainers — delete this block when generating):
#
#   1. Replace {DomainEntity} with the class name from the test.
#   2. Add only attributes and methods that failing tests demand.
#   3. Start with a function if no state is needed; use a class only when
#      tests require accumulated state.
#   4. No attributes without a test asserting on them.
#   5. No methods without a test calling them.
#   6. Delete this instruction block before committing the file.
# =============================================================================
from dataclasses import dataclass, field
from typing import Optional


class {DomainEntity}:
    """
    {DomainEntity} — brief description of the domain concept.
    Implements only what the failing tests demand.
    """

    def __init__(self, {param_a}: {TypeA}, {param_b}: {TypeB}):
        self.{prop_a} = {param_a}   # assert: entity.{prop_a} == {expected}
        self.{mutable_prop} = 0     # assert: entity.{mutable_prop} == 0 initially

    def {action}(self, amount: {ParamType}) -> None:
        """Perform {action} — makes tests that assert on {mutable_prop} GREEN."""
        self.{mutable_prop} += amount


# -------------------------------------------------------------------------
# Function alternative (prefer functions until state demands a class)
# -------------------------------------------------------------------------
# def create_{domain_entity}({param}: {TypeA}) -> dict:
#     if not {param}.{validation_field}:
#         raise ValueError(f'{DomainEntity}: {field} is required')
#     return {
#         '{prop}': {param}.{prop},
#         # return only what tests assert on
#     }
