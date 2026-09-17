"""Load @agent_toolset classes by module path."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

class ToolsetLoader:
    """Loads @toolset classes by module path. Subclass and replace ``instance()`` to extend."""

    _instance: ToolsetLoader | None = None

    @classmethod
    def instance(cls) -> ToolsetLoader:
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def set_instance(cls, loader: ToolsetLoader | None) -> None:
        cls._instance = loader

    def check_toolset(self, candidate: type) -> bool:
        return isinstance(candidate, type) and (
            getattr(candidate, "_is_agent_toolset", False)
            or getattr(candidate, "_is_context", False)
            or getattr(candidate, "_is_agent_toolset", False)
        )

    def load(self, path: str) -> type:
        module_name, _, class_name = path.partition(":")
        if not class_name:
            raise ValueError(f"expected <module>:<Class>, got {path!r}")
        try:
            module = __import__(module_name, fromlist=[class_name])
        except ModuleNotFoundError:
            module = self._load_hyphenated(module_name)
        loaded = getattr(module, class_name)
        if not self.check_toolset(loaded):
            raise TypeError(f"{path} is not a @toolset class")
        return loaded

    def instantiate(self, item: object) -> object:
        """Instantiate one tools-list entry: toolset ref, mapping, or pass-through instance."""
        if isinstance(item, str):
            return self.load(item)()
        if isinstance(item, dict):
            loaded = self.load(str(item["toolset"]))
            return loaded(**(item.get("context") or {}))
        return item

    def instantiate_all(self, items: list) -> list:
        return [self.instantiate(item) for item in items]

    def _load_hyphenated(self, module_name: str) -> ModuleType:
        """Fallback loader for modules whose directory uses hyphens instead of underscores.

        Translates each package segment's underscores to hyphens when the standard
        import fails, allowing e.g. ``some_domain.some_domain`` to resolve from
        ``<root>/some-domain/some_domain.py`` if the underscore directory is absent.
        """
        parts = module_name.split(".")
        repo = Path(__file__).resolve().parents[2]
        search_roots = [repo] + [
            repo / name for name in ("primitives", "utilities", "practices", "actions")
        ]
        module_file = None
        for root in search_roots:
            search = root
            for part in parts[:-1]:
                hyphenated = part.replace("_", "-")
                candidate = search / hyphenated
                search = candidate if candidate.is_dir() else search / part
            candidate_file = search / f"{parts[-1]}.py"
            if candidate_file.exists():
                module_file = candidate_file
                break
        if module_file is None:
            raise ModuleNotFoundError(
                f"No module named {module_name!r} (also tried under {search_roots})"
            )
        spec = importlib.util.spec_from_file_location(module_name, module_file)
        if spec is None or spec.loader is None:
            raise ModuleNotFoundError(f"Cannot create spec for {module_file}")
        mod = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = mod
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        return mod

