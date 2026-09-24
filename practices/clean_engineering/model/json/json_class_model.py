"""JSON channel for the CleanEngineering model.

Schema (module-first):
{
  "name": "Model Name",
  "modules": [
    {
      "name": "ModuleName",
      "sequentialOrder": 1,
      "description": "...",
      "seam": "...",
      "seamTerms": ["TermA", "TermB"],
      "dependencies": ["other_module"],
      "constraint": "...",
      "classes": [
        {
          "name": "ClassName",
          "sequentialOrder": 1,
          "intent": "...",
          "properties": [{"name": "...", "typeHint": "...", "description": ""}],
          "operations": [{"name": "...", "parameters": ["..."], "returnType": "...", "description": ""}],
          "relationships": [{"target": "...", "kind": "...", "cardinality": "...", "description": ""}],
          "collaborators": []
        }
      ]
    }
  ]
}

Legacy schema with top-level "classes" is still accepted on parse for backward compatibility.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import List, Optional

_repo = Path(__file__).resolve().parents[3]
if str(_repo) not in sys.path:
    sys.path.insert(0, str(_repo))

from practices.clean_engineering.model.base_class_model import OoadNode
from practices.clean_engineering.model.base_class_model import (
    CleanEngineeringModel,
    Module,
    OoadClass,
    Operation,
    Property,
    Relationship,
)
from practices.clean_engineering.model.update_report import UpdateReport


class JsonParseError(ValueError):
    pass


class JsonOoadClass(OoadClass):
    pass


class JsonModule(Module):
    def load_class(self, source: OoadClass) -> JsonOoadClass:
        return JsonOoadClass(name=source.name, sequential_order=source.sequential_order)


class JsonCleanEngineeringModel(CleanEngineeringModel):

    def load_module(self, source: Module) -> JsonModule:
        return JsonModule(name=source.name, sequential_order=source.sequential_order)

    # ------------------------------------------------------------------
    # Uniform callable surface
    # ------------------------------------------------------------------

    def parse(self, text: str) -> "JsonCleanEngineeringModel":
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            raise JsonParseError(f"Invalid JSON: {exc}") from exc
        model = type(self)(name=data.get("name", ""))
        if "modules" in data:
            self._load_modules(model, data["modules"])
        elif "classes" in data:
            self._load_legacy_classes(model, data["classes"])
        else:
            raise JsonParseError("JSON must contain a 'modules' or 'classes' key")
        return model

    def _load_modules(self, model: "JsonCleanEngineeringModel", modules: list) -> None:
        for i, md in enumerate(modules, 1):
            module = self._module_from_dict(md, i)
            for j, cd in enumerate(md.get("classes", []), 1):
                module.classes.append(self._class_from_dict(cd, j))
            model.modules.append(module)

    def _load_legacy_classes(self, model: "JsonCleanEngineeringModel", classes: list) -> None:
        module = JsonModule(name="", sequential_order=1)
        for i, cd in enumerate(classes, 1):
            module.classes.append(self._class_from_dict(cd, i))
        if module.classes:
            model.modules.append(module)

    def _module_from_dict(self, md: dict, sequential_order: int) -> JsonModule:
        seam_terms = md.get("seamTerms") or md.get("seam_terms") or []
        dependencies = md.get("dependencies") or []
        if isinstance(seam_terms, str):
            seam_terms = [t.strip() for t in seam_terms.split(",") if t.strip()]
        if isinstance(dependencies, str):
            dependencies = [t.strip() for t in dependencies.split(",") if t.strip()]
        return JsonModule(
            name=md.get("name", ""),
            sequential_order=md.get("sequentialOrder", sequential_order),
            description=md.get("description", ""),
            seam=md.get("seam", ""),
            constraint=md.get("constraint", ""),
            seam_terms=list(seam_terms),
            dependencies=list(dependencies),
        )

    def _class_from_dict(self, d: dict, sequential_order: int) -> JsonOoadClass:
        props = [
            Property(
                name=p["name"],
                type_hint=p.get("typeHint", ""),
                description=p.get("description", ""),
            )
            for p in d.get("properties", [])
        ]
        ops = [
            Operation(
                name=o["name"],
                parameters=o.get("parameters", []),
                return_type=o.get("returnType", ""),
                description=o.get("description", ""),
            )
            for o in d.get("operations", [])
        ]
        rels = [
            Relationship(
                target=r["target"],
                kind=r.get("kind", ""),
                cardinality=r.get("cardinality", ""),
                description=r.get("description", ""),
            )
            for r in d.get("relationships", [])
        ]
        return JsonOoadClass(
            name=d["name"],
            sequential_order=d.get("sequentialOrder", sequential_order),
            intent=d.get("intent", ""),
            properties=props,
            operations=ops,
            relationships=rels,
            collaborators=d.get("collaborators", []),
        )

    def render(self, canonical: CleanEngineeringModel, previous: Optional[str] = None) -> str:
        if canonical.modules:
            data = {
                "name": canonical.name,
                "modules": [self._module_to_dict(m) for m in canonical.modules],
            }
        else:
            data = {
                "name": canonical.name,
                "classes": [self._class_to_dict(c) for c in canonical.classes],
            }
        return json.dumps(data, indent=2)

    def _module_to_dict(self, module: Module) -> dict:
        return {
            "name": module.name,
            "sequentialOrder": module.sequential_order,
            "description": module.description,
            "seam": module.seam,
            "seamTerms": list(module.seam_terms),
            "dependencies": list(module.dependencies),
            "constraint": module.constraint,
            "classes": [self._class_to_dict(c) for c in module.classes],
        }

    def _class_to_dict(self, oclass: OoadClass) -> dict:
        return {
            "name": oclass.name,
            "sequentialOrder": oclass.sequential_order,
            "intent": oclass.intent,
            "properties": [
                {"name": p.name, "typeHint": p.type_hint, "description": p.description}
                for p in oclass.properties
            ],
            "operations": [
                {
                    "name": o.name,
                    "parameters": o.parameters,
                    "returnType": o.return_type,
                    "description": o.description,
                }
                for o in oclass.operations
            ],
            "relationships": [
                {
                    "target": r.target,
                    "kind": r.kind,
                    "cardinality": r.cardinality,
                    "description": r.description,
                }
                for r in oclass.relationships
            ],
            "collaborators": oclass.collaborators,
        }

    def sync(self, text: str, canonical: CleanEngineeringModel) -> UpdateReport:
        return canonical.translate_from(self.parse(text))

    @classmethod
    def from_workspace(cls, root: Path) -> Optional["JsonCleanEngineeringModel"]:
        candidates = list(root.glob("**/CleanEngineering-model.json")) + list(root.glob("**/*.CleanEngineering.json"))
        for path in sorted(candidates):
            try:
                return cls().parse(path.read_text(encoding="utf-8"))
            except (JsonParseError, KeyError):
                continue
        return None
