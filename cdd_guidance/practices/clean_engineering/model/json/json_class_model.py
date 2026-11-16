"""JSON channel for the CleanEngineering model."""
from __future__ import annotations

import json
from typing import Any, Dict, Optional

from cdd_guidance.practices.clean_engineering.model.base_class_model import (
    CleanEngineeringModel,
    Module,
    OoadClass,
    UnreadableSource,
)
from cdd_guidance.practices.clean_engineering.model.field_types import Relationship
from cdd_guidance.practices.clean_engineering.model.operation import Operation
from cdd_guidance.practices.clean_engineering.model.property import Property

# One object of a JSON model document as the decoder gives it: the model, a module, a class, a member, or a
# relationship, each keyed by the names `as_record` writes.
JsonRecord = Dict[str, Any]


class JsonProperty(Property):
    @classmethod
    def from_record(cls, record: JsonRecord) -> "JsonProperty":
        loaded = cls(record["name"], type_hint=record.get("typeHint", ""))
        loaded.description = record.get("description", "")
        return loaded


class JsonOperation(Operation):
    @classmethod
    def from_record(cls, record: JsonRecord) -> "JsonOperation":
        loaded = cls(record["name"], return_type=record.get("returnType", ""))
        loaded.take_parameters(record.get("parameters", []))
        loaded.description = record.get("description", "")
        return loaded


class JsonRelationship(Relationship):
    @classmethod
    def from_record(cls, record: JsonRecord) -> "JsonRelationship":
        return cls(
            target=record["target"],
            kind=record.get("kind", ""),
            cardinality=record.get("cardinality", ""),
            description=record.get("description", ""),
        )


class JsonOoadClass(OoadClass):
    def load_property(self, source: Property) -> JsonProperty:
        loaded = JsonProperty(name=source.name)
        loaded.update_self(source)
        return loaded

    def load_operation(self, source: Operation) -> JsonOperation:
        loaded = JsonOperation(name=source.name)
        loaded.update_self(source)
        return loaded

    @classmethod
    def from_record(cls, record: JsonRecord, sequential_order: int) -> "JsonOoadClass":
        loaded = cls(record["name"], record.get("sequentialOrder", sequential_order), record.get("intent", ""))
        loaded.collaborators = list(record.get("collaborators", []))
        loaded.stereotypes = list(record.get("stereotypes", []))
        loaded.bases = list(record.get("bases", []))
        loaded.properties = [JsonProperty.from_record(item) for item in record.get("properties", [])]
        loaded.operations = [JsonOperation.from_record(item) for item in record.get("operations", [])]
        for item in record.get("relationships", []):
            loaded.arrows.place(JsonRelationship.from_record(item))
        return loaded

    def render(self) -> str:
        return json.dumps(self.as_record(), indent=2)


class JsonModule(Module):
    class_type = JsonOoadClass

    @classmethod
    def from_record(cls, record: JsonRecord, sequential_order: int) -> "JsonModule":
        seam_terms = record.get("seamTerms") or record.get("seam_terms") or []
        dependencies = record.get("dependencies") or []
        if isinstance(seam_terms, str):
            seam_terms = [term.strip() for term in seam_terms.split(",") if term.strip()]
        if isinstance(dependencies, str):
            dependencies = [term.strip() for term in dependencies.split(",") if term.strip()]
        loaded = cls(record.get("name", ""), record.get("sequentialOrder", sequential_order))
        loaded.description = record.get("description", "")
        loaded.seam = record.get("seam", "")
        loaded.constraint = record.get("constraint", "")
        loaded.seam_terms = list(seam_terms)
        loaded.dependencies = list(dependencies)
        for index, class_record in enumerate(record.get("classes", []), 1):
            loaded.classes.append(JsonOoadClass.from_record(class_record, index))
        return loaded

    def render(self) -> str:
        return json.dumps(self.as_record(), indent=2)


class JsonCleanEngineeringModel(CleanEngineeringModel):
    module_type = JsonModule

    def parse(self, text: str) -> "JsonCleanEngineeringModel":
        """Read a JSON model document into this model's own modules, and return it."""
        return self.take_record(self._decoded(text))

    def _decoded(self, text: str) -> JsonRecord:
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise UnreadableSource(f"Invalid JSON: {exc}") from exc

    def take_record(self, record: JsonRecord) -> "JsonCleanEngineeringModel":
        """Become the model a JSON model document holds: its modules, or one unnamed module of its classes."""
        self.name = record.get("name", "")
        self.modules = []
        if "modules" in record:
            self.modules = [JsonModule.from_record(module, index) for index, module in enumerate(record["modules"], 1)]
        elif "classes" in record:
            module = JsonModule(name="", sequential_order=1)
            module.classes = [JsonOoadClass.from_record(oclass, index) for index, oclass in enumerate(record["classes"], 1)]
            self.modules = [module] if module.classes else []
        else:
            raise UnreadableSource("JSON must contain a 'modules' or 'classes' key")
        return self

    def render(self, canonical: Optional[CleanEngineeringModel] = None) -> str:
        if canonical is not None and canonical is not self:
            self.translate_from(canonical)
        return json.dumps(self.as_record(), indent=2)

