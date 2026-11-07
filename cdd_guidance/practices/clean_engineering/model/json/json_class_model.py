"""JSON channel for the CleanEngineering model."""
from __future__ import annotations

import json
from typing import Optional

from cdd_guidance.practices.clean_engineering.model.base_class_model import (
    CleanEngineeringModel,
    Module,
    OoadClass,
)
from cdd_guidance.practices.clean_engineering.model.field_types import Relationship
from cdd_guidance.practices.clean_engineering.model.operation import Operation
from cdd_guidance.practices.clean_engineering.model.property import Property


class JsonParseError(ValueError):
    pass


class JsonProperty(Property):
    @classmethod
    def from_record(cls, record: dict) -> "JsonProperty":
        loaded = cls(
            name=record["name"],
            type_hint=record.get("typeHint", ""),
            description=record.get("description", ""),
        )
        return loaded


class JsonOperation(Operation):
    @classmethod
    def from_record(cls, record: dict) -> "JsonOperation":
        return cls(
            name=record["name"],
            parameters=record.get("parameters", []),
            return_type=record.get("returnType", ""),
            description=record.get("description", ""),
        )


class JsonRelationship(Relationship):
    @classmethod
    def from_record(cls, record: dict) -> "JsonRelationship":
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

    def load_relationship(self, source: Relationship) -> JsonRelationship:
        loaded = JsonRelationship(target=source.target)
        loaded.update_self(source)
        return loaded

    @classmethod
    def from_record(cls, record: dict, sequential_order: int) -> "JsonOoadClass":
        loaded = cls(
            name=record["name"],
            sequential_order=record.get("sequentialOrder", sequential_order),
            intent=record.get("intent", ""),
            collaborators=record.get("collaborators", []),
        )
        loaded.stereotypes = list(record.get("stereotypes", []))
        loaded.bases = list(record.get("bases", []))
        loaded.properties = [JsonProperty.from_record(item) for item in record.get("properties", [])]
        loaded.operations = [JsonOperation.from_record(item) for item in record.get("operations", [])]
        for item in record.get("relationships", []):
            loaded.place_relationship(JsonRelationship.from_record(item))
        return loaded

    def render(self) -> str:
        return json.dumps(self.as_record(), indent=2)


class JsonModule(Module):
    def load_class(self, source: OoadClass) -> JsonOoadClass:
        loaded = JsonOoadClass(name=source.name, sequential_order=source.sequential_order)
        loaded.update_self(source)
        return loaded

    @classmethod
    def from_record(cls, record: dict, sequential_order: int) -> "JsonModule":
        seam_terms = record.get("seamTerms") or record.get("seam_terms") or []
        dependencies = record.get("dependencies") or []
        if isinstance(seam_terms, str):
            seam_terms = [term.strip() for term in seam_terms.split(",") if term.strip()]
        if isinstance(dependencies, str):
            dependencies = [term.strip() for term in dependencies.split(",") if term.strip()]
        loaded = cls(
            name=record.get("name", ""),
            sequential_order=record.get("sequentialOrder", sequential_order),
            description=record.get("description", ""),
            seam=record.get("seam", ""),
            constraint=record.get("constraint", ""),
            seam_terms=list(seam_terms),
            dependencies=list(dependencies),
        )
        for index, class_record in enumerate(record.get("classes", []), 1):
            loaded.classes.append(JsonOoadClass.from_record(class_record, index))
        return loaded

    def render(self) -> str:
        return json.dumps(self.as_record(), indent=2)


class JsonCleanEngineeringModel(CleanEngineeringModel):
    def load_module(self, source: Module) -> JsonModule:
        loaded = JsonModule(name=source.name, sequential_order=source.sequential_order)
        loaded.update_self(source)
        return loaded

    def parse(self, text: str) -> "JsonCleanEngineeringModel":
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            raise JsonParseError(f"Invalid JSON: {exc}") from exc
        model = self
        model.name = data.get("name", "")
        model.modules = []
        if "modules" in data:
            for index, record in enumerate(data["modules"], 1):
                model.modules.append(JsonModule.from_record(record, index))
        elif "classes" in data:
            module = JsonModule(name="", sequential_order=1)
            for index, record in enumerate(data["classes"], 1):
                module.classes.append(JsonOoadClass.from_record(record, index))
            if module.classes:
                model.modules.append(module)
        else:
            raise JsonParseError("JSON must contain a 'modules' or 'classes' key")
        return model

    def render(self, canonical: Optional[CleanEngineeringModel] = None) -> str:
        if canonical is not None and canonical is not self:
            self.translate_from(canonical)
        return json.dumps(self.as_record(), indent=2)

