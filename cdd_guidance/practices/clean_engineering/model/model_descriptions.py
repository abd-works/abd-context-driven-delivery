"""The members the Clean Engineering model documents beside the code describe."""

from __future__ import annotations

from typing import Dict, List, Union

from cdd_guidance.practices.clean_engineering.model.base_class_model import CleanEngineeringModel
from cdd_guidance.practices.clean_engineering.model.operation import Operation
from cdd_guidance.practices.clean_engineering.model.property import Property

Member = Union[Operation, Property]


class ModelDescriptions:
    """Every member the model documents describe, by ``Class.member``, with the document that describes it.

    A realization follows an interaction into a class the load left out, so the members that have no code are kept
    too. A later document's description of the same member replaces an earlier one. The graph keeps them as the
    Clean Engineering practice root's ``model_members`` fact.
    """

    def __init__(self) -> None:
        self._members: Dict[str, Member] = {}
        self._files: Dict[str, str] = {}

    def read(self, model: CleanEngineeringModel, file: str) -> None:
        """Take the members ``model``, read from the document at ``file``, describes."""
        for module in model.modules:
            for oclass in module.classes:
                for member in [*oclass.properties, *oclass.operations]:
                    key = f"{oclass.name}.{member.name}"
                    self._members[key] = member
                    self._files[key] = file

    @property
    def is_empty(self) -> bool:
        return not self._members

    @property
    def model_members(self) -> Dict[str, dict]:
        """Each described member as ``graph.json`` saves it: its kind, interactions, parameters, return type, and document."""
        return {key: self._saved(key, member) for key, member in self._members.items()}

    def _saved(self, key: str, member: Member) -> dict:
        is_operation = isinstance(member, Operation)
        return {
            "kind": "Operation" if is_operation else "Property",
            "interactions": list(member.callees),
            "model_parameters": self._parameters(member) if is_operation else [],
            "model_returns": ((member.return_type if is_operation else member.type_hint) or "").strip(),
            "model_file": self._files[key],
        }

    def _parameters(self, operation: Operation) -> List[list]:
        return [[parameter.name, (parameter.type_hint or "").strip()] for parameter in operation.parameters]
