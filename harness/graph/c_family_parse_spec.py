"""C-family parse: module-level functions stay off domain classes."""

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from expects import equal, expect
from mamba import description, it

from cdd_guidance.practices.clean_engineering.model.typescript.typescript_class_model import (
    TypeScriptCleanEngineeringModel,
)


def _class(model, name: str):
    for module in model.modules:
        for oclass in module.classes:
            if oclass.name == name:
                return oclass
    return None


with description("CFamilyParse top-level functions"):
    with it("should keep module functions on _module, not the first class"):
        source = """
export class ValidationCode {
  constructor(public code: string) {}
}

export class AccountCredentials {
  register() {}
}

function accountRepositoryFor(credentials: AccountCredentials) {
  return credentials._repository;
}
"""
        model = TypeScriptCleanEngineeringModel.parse(source)
        validation = _class(model, "ValidationCode")
        module_holder = _class(model, "_module")
        expect([op.name for op in validation.operations]).to(equal(["constructor"]))
        expect([op.name for op in module_holder.operations]).to(equal(["accountRepositoryFor"]))
