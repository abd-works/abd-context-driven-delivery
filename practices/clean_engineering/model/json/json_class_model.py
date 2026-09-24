"""JSON channel for the CleanEngineering model."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import List, Optional

_repo = Path(__file__).resolve().parents[3]
if str(_repo) not in sys.path:
    sys.path.insert(0, str(_repo))

from practices.clean_engineering.model.base_class_model import (
    CleanEngineeringModel,
    Module,
    OoadClass,
    OoadNode,
)
from practices.clean_engineering.model.field_types import OperationField, PropertyField, Relationship
from practices.clean_engineering.model.update_report import ChildCollectionPair, UpdateReport


class JsonParseError(ValueError):
    pass


class JsonProperty(PropertyField):
    @classmethod
    def from_record(cls, record: dict) -> "JsonProperty":
        loaded = cls(
            name=record["name"],
            type_hint=record.get("typeHint", ""),
            description=record.get("description", ""),
        )
        return loaded


class JsonOperation(OperationField):
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
    def load_property_field(self, source: PropertyField) -> JsonProperty:
        loaded = JsonProperty(name=source.name)
        loaded.update_self(source)
        return loaded

    def load_operation_field(self, source: OperationField) -> JsonOperation:
        loaded = JsonOperation(name=source.name)
        loaded.update_self(source)
        return loaded

    def load_relationship(self, source: Relationship) -> JsonRelationship:
        loaded = JsonRelationship(target=source.target)
        loaded.update_self(source)
        return loaded

    def child_collections(self, source: OoadNode) -> List[ChildCollectionPair]:
        assert isinstance(source, OoadClass)
        return [
            ChildCollectionPair(self.properties, source.properties, self.load_property_field),
            ChildCollectionPair(self.operations, source.operations, self.load_operation_field),
            ChildCollectionPair(self.relationships, source.relationships, self.load_relationship),
        ]

    def update_self(self, source: OoadNode) -> None:
        assert isinstance(source, OoadClass)
        self.intent = source.intent
        self.collaborators = list(source.collaborators)

    @classmethod
    def from_record(cls, record: dict, sequential_order: int) -> "JsonOoadClass":
        loaded = cls(
            name=record["name"],
            sequential_order=record.get("sequentialOrder", sequential_order),
            intent=record.get("intent", ""),
            collaborators=record.get("collaborators", []),
        )
        loaded.properties = [JsonProperty.from_record(item) for item in record.get("properties", [])]
        loaded.operations = [JsonOperation.from_record(item) for item in record.get("operations", [])]
        loaded.relationships = [JsonRelationship.from_record(item) for item in record.get("relationships", [])]
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
        model = type(self)(name=data.get("name", ""))
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

    def render(self, canonical: Optional[CleanEngineeringModel] = None, previous: Optional[str] = None) -> str:
        if canonical is not None:
            self.translate_from(canonical)
        return json.dumps(self.as_record(), indent=2)

    def sync(self, text: str, canonical: CleanEngineeringModel) -> UpdateReport:
        return canonical.translate_from(self.parse(text))

    @classmethod
    def from_workspace(cls, root: Path) -> Optional["JsonCleanEngineeringModel"]:
        candidates = list(root.glob("**/CleanEngineering-model.json")) + list(
            root.glob("**/*.CleanEngineering.json")
        )
        for path in sorted(candidates):
            try:
                return cls().parse(path.read_text(encoding="utf-8"))
            except (JsonParseError, KeyError):
                continue
        return None
