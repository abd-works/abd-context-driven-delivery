# @toolset-manifest python -m tools manifest context_tools.clean_engineering.class_model.drawio.drawio:Drawio
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# Do not author behavior from this Python source.
# invoke-new: action render
# invoke-check: action validate | toolset: context_tools.clean_engineering.class_model.drawio.drawio:Drawio
"""Draw.io miniature kit — render class diagrams, scan layout rules, repair on failure.

Not a full context tool: no partition / grill / sketch / fidelities. Composed by
CleanEngineering when ``format`` is ``drawio``. Reuses Scan + Repair kits.
"""

from __future__ import annotations

from pathlib import Path

from primitives.actions.action import action, agentic_toolset
from primitives.instructions import Instruction, instruction
from repair.repair import Repair
from scanners.scan import Scan
from scanners.scanner_collection import ScannerCollection
from sub_agent.sub_agent import sub_agent
from tools.tool import tool

from context_tools.clean_engineering.class_model.drawio.drawio_class_model import (
    DrawIOCleanEngineeringModel,
)


class _DrawioScan(Scan):
    """Scan binding that discovers layout scanners under this package."""

    def __init__(self, module_dir: Path) -> None:
        self._module_dir = Path(module_dir)

    def _scanner_collection(self) -> ScannerCollection:
        return ScannerCollection(
            module_dir=self._module_dir,
            root_path=self._module_dir / "scanners",
        )


@agentic_toolset
class Drawio:
    """# Instructions

    Miniature kit for Clean Engineering Draw.io class diagrams: create →
    validate/scan layout rules → repair (sub-agent) on definitive failures.
    """

    def __init__(self, workspace=None) -> None:
        self.workspace = workspace
        self.scanner = _DrawioScan(self.module_dir)
        self.repairer = Repair(workspace=workspace, scanner=self.scanner)

    @property
    def module_dir(self) -> Path:
        return Path(__file__).resolve().parent

    @property
    def domain_slug(self) -> str:
        return "drawio"

    @instruction
    def contexts(self) -> Instruction: ...

    @instruction
    def examples(self) -> Instruction: ...

    @tool
    def create_diagram(
        self,
        content: str,
        path: str,
        source_format: str = "markdown",
        previous: str = "",
        keep_positioning: bool = False,
    ) -> str:
        """Parse *content* from *source_format*, render Draw.io XML, write *path*.

        When *keep_positioning* is true, look for an existing diagram at *path*
        (or use *previous* XML) and update class contents in place: existing
        classes keep their positions, existing relationships keep their routing,
        and only new classes/relationships are laid out. Returns the written path.
        """
        from context_tools.clean_engineering.class_model.markdown_class_model import (
            MarkdownCleanEngineeringModel,
        )
        from context_tools.clean_engineering.class_model.json_class_model import (
            JsonCleanEngineeringModel,
        )
        from context_tools.clean_engineering.class_model.python_class_model import (
            PythonCleanEngineeringModel,
        )

        parsers: dict[str, type] = {
            "markdown": MarkdownCleanEngineeringModel,
            "json": JsonCleanEngineeringModel,
            "python": PythonCleanEngineeringModel,
            "drawio": DrawIOCleanEngineeringModel,
        }
        if source_format not in parsers:
            raise ValueError(
                f"Unsupported source_format {source_format!r}. "
                f"Choose from: {sorted(parsers)}"
            )
        model = parsers[source_format].parse(content)
        out = Path(path)
        prev = previous
        if keep_positioning and not prev and out.exists():
            prev = out.read_text(encoding="utf-8")
        rendered = DrawIOCleanEngineeringModel.render(
            model,
            previous=prev or None,
            keep_positioning=keep_positioning,
        )
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(rendered, encoding="utf-8")
        return str(out.resolve())

    @tool
    def scan(self, paths: list[str], root: str | None = None, rule: str | None = None) -> str:
        """scan layout rules on `.drawio` paths (drawio.md rule slugs)."""
        scan_root = root if root is not None else str(self.module_dir)
        return self.scanner.scan(paths, root=scan_root, rule=rule)

    @action
    def validate(self) -> str:
        """Judge the diagram against drawio contexts; call scan on the asset paths under review."""
        self.contexts
        self.scan()
        return "Validation report for Draw.io layout rules (see contexts)."

    @sub_agent
    @action
    def repair(self, asset: str, violation: str) -> str:
        """repair"""
        self.scan()
        self.contexts
        self.examples
        self.repairer.repair(asset, violation)
        return "Repair {{asset}} until drawio validate/scan passes. Fix the layout generator — not a one-off diagram edit."

    @action
    def render(
        self,
        content: str = "",
        path: str = "",
        source_format: str = "markdown",
        previous: str = "",
        keep_positioning: bool = False,
    ) -> str:
        """render"""
        self.create_diagram(
            content, path, source_format, previous, keep_positioning
        )
        self.validate()
        self.mode = "tool"
        self.repair()
        return (
            "Rendered {{path}}. After validate/scan: if definitive layout "
            "violations remain, invoke repair as a sub-agent with the scan "
            "report; otherwise done."
        )

    @sub_agent
    @tool
    def verify_regression(self, examples_root: str = "") -> str:
        """Re-scan faultyAsset/repairedAsset pairs under this kit's examples/evals."""
        root = examples_root or str(self.module_dir / "examples" / "evals")
        return self.repairer.verify_regression(root)
