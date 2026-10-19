"""Draw.io miniature kit — render class diagrams, scan layout rules, repair on failure.

Not a full context tool: no partition / grill / sketch / fidelities. Composed by
CleanEngineering when ``format`` is ``drawio``. Layout scan lives on DrawioScanner.
"""

from __future__ import annotations

from pathlib import Path

from harness.agent_tools import agent_instructions, agent_toolset, instructions, tools
from harness.markdown import markdown
from harness.agent_tools.agent_tools import agent_tool
from practices.clean_engineering.model.drawio.scanners._drawio_base import DrawioScanner

from practices.clean_engineering.model.drawio.drawio_class_model import (
    DrawIOCleanEngineeringModel,
)


@agent_toolset
class Drawio:
    """# Instructions

    Miniature kit for Clean Engineering Draw.io class diagrams: create →
    validate/scan layout rules → repair (sub-agent) on definitive failures.
    """

    def __init__(self, workspace=None) -> None:
        self.workspace = workspace
        self.source_format = "markdown"
        self.previous = ""
        self.keep_positioning = False
        self.scan_root = None
        self.rule = None

    @property
    def module_dir(self) -> Path:
        return Path(__file__).resolve().parent

    @property
    def domain_slug(self) -> str:
        return "drawio"

    @markdown("overview")
    def contexts(self) -> str: ...

    @markdown
    def examples(self) -> str: ...

    @agent_tool
    def create_diagram(self, content: str, path: str) -> str:
        """Parse *content*, render Draw.io XML, write *path*.

        When *keep_positioning* is true, look for an existing diagram at *path*
        (or use *previous* XML) and update class contents in place: existing
        classes keep their positions, existing relationships keep their routing,
        and only new classes/relationships are laid out. Returns the written path.
        """
        model = self._parse_source(content)
        out = Path(path)
        prev = self._previous_xml(out)
        channel = DrawIOCleanEngineeringModel()
        channel.previous = prev or None
        channel.keep_positioning = self.keep_positioning
        rendered = channel.render(model)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(rendered, encoding="utf-8")
        return str(out.resolve())

    def _parse_source(self, content: str):
        from practices.clean_engineering.model.markdown.markdown_class_model import (
            MarkdownCleanEngineeringModel,
        )
        from practices.clean_engineering.model.json.json_class_model import (
            JsonCleanEngineeringModel,
        )
        from practices.clean_engineering.model.python.python_class_model import (
            PythonCleanEngineeringModel,
        )
        parsers: dict[str, type] = {
            "markdown": MarkdownCleanEngineeringModel,
            "json": JsonCleanEngineeringModel,
            "python": PythonCleanEngineeringModel,
            "drawio": DrawIOCleanEngineeringModel,
        }
        if self.source_format not in parsers:
            raise ValueError(
                f"Unsupported source_format {self.source_format!r}. "
                f"Choose from: {sorted(parsers)}"
            )
        return parsers[self.source_format](name="", sequential_order=1).parse(content)

    def _previous_xml(self, out: Path) -> str:
        prev = self.previous
        if self.keep_positioning and not prev and out.exists():
            return out.read_text(encoding="utf-8")
        return prev

    @agent_tool
    def scan(self, paths: list[str]) -> str:
        """scan layout rules on `.drawio` paths (drawio.md rule slugs)."""
        scan_root = self.scan_root if self.scan_root is not None else str(self.module_dir)
        scanner = DrawioScanner(self.rule)
        scanner.workspace_root = scan_root
        return str(scanner.run_report(paths))

    @agent_instructions
    def validate(self) -> str:
        """Judge the diagram against drawio contexts; call scan on the asset paths under review."""
        tools(self.scan)
        return "Validation report for Draw.io layout rules (see contexts)."

    @agent_instructions
    def repair(self, asset: str, violation: str) -> str:
        """repair"""
        tools(self.scan)
        return "Repair {{asset}} until drawio validate/scan passes. Fix the layout generator — not a one-off diagram edit."

    @agent_instructions
    def render(
        self,
        content: str = "",
        path: str = "",
    ) -> str:
        """render"""
        tools(self.create_diagram(content, path))
        instructions(self.validate)
        self.mode = "tool"
        instructions(self.repair)
        return (
            "Rendered {{path}}. After validate/scan: if definitive layout "
            "violations remain, invoke repair as a sub-agent with the scan "
            "report; otherwise done."
        )

    @agent_tool
    def verify_regression(self, examples_root: str = "") -> str:
        """Regression check after repair (scan before/after + judge)."""
        _ = examples_root
        return (
            "Eval the repair with expect_scan_fails on the before file and "
            "expect_scan_passes on the after file (practices.bdd.spec_helpers)."
        )
