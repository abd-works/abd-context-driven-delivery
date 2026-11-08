"""The Draw.io toolset: render a class or modules diagram, scan its layout rules, repair the generator on failure.

It has no partition, grill, sketch, or fidelities of its own; CleanEngineering composes it when ``format`` is
``drawio``. Each layout rule is a scanner under ``scanners/``.
"""

from __future__ import annotations

from pathlib import Path

from harness.agent_tools import agent_instructions, agent_toolset, instructions, tools
from harness.markdown import markdown
from harness.agent_tools.agent_tools import agent_tool
from cdd_guidance.practices.clean_engineering.model.drawio.scanners._drawio_base import DrawioScanner
from cdd_guidance.practices.clean_engineering.model.drawio.drawio_class_model import (
    DrawIOCleanEngineeringModel,
)
from cdd_guidance.practices.clean_engineering.model.markdown.markdown_class_model import MarkdownCleanEngineeringModel


@agent_toolset
class Drawio:
    """# Instructions

    The Draw.io toolset for Clean Engineering diagrams: create →
    validate/scan layout rules → repair (sub-agent) on definitive failures.
    """

    def __init__(self) -> None:
        # The markdown class model the source a diagram is drawn from is read with. The toolset keeps its own, so reading
        # a diagram's source never changes a model the Clean Engineering practice renders with, and it never needs the
        # practice itself.
        self.source = MarkdownCleanEngineeringModel()
        # The one Draw.io model this toolset writes; its `previous` and `keep_positioning` are the layout policy.
        self.channel = DrawIOCleanEngineeringModel()
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
        model = self.source.parse(content)
        out = Path(path)
        if self.channel.keep_positioning and not self.channel.previous and out.exists():
            self.channel.previous = out.read_text(encoding="utf-8")
        rendered = self.channel.render(model)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(rendered, encoding="utf-8")
        return str(out.resolve())

    @agent_tool
    def scan(self, paths: list[str]) -> str:
        """scan layout rules on `.drawio` paths (drawio.md rule slugs)."""
        scan_root = self.scan_root if self.scan_root is not None else str(self.module_dir)
        scanner = DrawioScanner(self.rule, scan_root=scan_root)
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
            "Check the repair with assert_files_rule_pair (cdd_guidance/practices/clean_engineering/rules/rule_examples.py): "
            "the before files must break the rule and the after files must not."
        )
