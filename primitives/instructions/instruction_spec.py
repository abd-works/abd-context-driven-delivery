"""BDD spec for instruction.py - Instruction, routing helpers, @instruction slot decorator."""
import sys
from pathlib import Path

from expects import be_none, be_true, contain, equal, expect
from mamba import before, context, description, it

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("primitives", "utilities", "context_tools", "context_tools/actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

_CLEAN_ENGINEERING_DIR = _REPO_ROOT / "context_tools" / "clean_engineering"
_GENERATOR_DIR = _REPO_ROOT / "context_tools" / "base"
_LIFECYCLE_PROSE_DIR = _GENERATOR_DIR  # sections in base_context_tool.md
_REPAIR_DIR = _REPO_ROOT / "context_tools" / "actions" / "improvement"

from primitives.instructions import Instruction
from primitives.instructions import _active_resource, _format_keys, _path_for_name, _path_for_templates
from primitives.instructions import _expand_docstring, _inline, instruction, instruction_slot_names


with description("Instruction"):
    with context("constructed with plain prose"):
        with before.each:
            self.instruction = Instruction("Write clean production code.", _CLEAN_ENGINEERING_DIR)

        with it("should return the prose unchanged when expand is called"):
            expect(self.instruction.expand()).to(equal("Write clean production code."))

        with it("should return False from matches_file_or_folder"):
            expect(self.instruction.matches_file_or_folder()).to(equal(False))

    with context("constructed with a \u00a7 section reference"):
        with before.each:
            self.instruction = Instruction("\u00a7 Contexts", _CLEAN_ENGINEERING_DIR)

        with it("should return True from matches_file_or_folder"):
            expect(self.instruction.matches_file_or_folder()).to(be_true)

        with it("should expand to the Contexts section of clean_engineering.md"):
            result = self.instruction.expand()
            expect("high-cohesion" in result).to(be_true)

    with context("constructed with \u00a7 Contexts on the domain markdown"):
        with before.each:
            self.instruction = Instruction(
                "\u00a7 Contexts", _CLEAN_ENGINEERING_DIR, domain_slug="clean_engineering"
            )

        with it("should return True from matches_file_or_folder"):
            expect(self.instruction.matches_file_or_folder()).to(be_true)

        with it("should expand to non-empty content including modules fidelity"):
            result = self.instruction.expand()
            expect(len(result) > 0).to(be_true)
            expect("## modules" in result.lower() or "modules" in result).to(be_true)

    with context("Instruction.ref built from a host"):
        with before.each:
            class _Host:
                module_dir = _CLEAN_ENGINEERING_DIR
                format = "python"
                toolset_name = "clean_engineering"

            self.ref = Instruction.ref(_Host(), "contexts")

        with it("should expand to non-empty content containing the word Contexts"):
            result = self.ref.expand()
            expect(len(result) > 0).to(be_true)
            expect(result).to(contain("Contexts"))


with description("_path_for_name"):
    with context("when a subfolder with that name exists"):
        with it("should return name with trailing slash"):
            expect(_path_for_name(_CLEAN_ENGINEERING_DIR, "examples")).to(equal("examples/"))

    with context("when a .md file with that name exists"):
        with it("should return the bare name"):
            expect(_path_for_name(_CLEAN_ENGINEERING_DIR, "clean_engineering")).to(
                equal("clean_engineering")
            )

    with context("when neither file nor folder exists"):
        with it("should return a \u00a7 section reference"):
            expect(_path_for_name(_CLEAN_ENGINEERING_DIR, "nonexistent").startswith("\u00a7")).to(
                equal(True)
            )


with description("_path_for_templates"):
    with context("when shared templates/ folder exists"):
        with it("should return a path under templates/ containing clean_engineering-templates"):
            hint = _path_for_templates(_CLEAN_ENGINEERING_DIR, "clean_engineering", "python")
            expect("templates/" in hint or hint == "templates").to(equal(True))
            expect("clean_engineering-templates" in hint or hint == "templates").to(equal(True))

    with context("when active_format is None"):
        with it("should return a non-empty fallback string"):
            expect(
                len(_path_for_templates(_CLEAN_ENGINEERING_DIR, "clean_engineering", None)) > 0
            ).to(equal(True))


with description("_format_keys"):
    with context("a module_dir with no formats/ directory"):
        with it("should return an empty list"):
            expect(_format_keys(_CLEAN_ENGINEERING_DIR)).to(equal([]))
            expect(_format_keys(_REPO_ROOT / "primitives")).to(equal([]))


with description("_active_resource"):
    with context("when key is None"):
        with it("should return None"):
            class _Host:
                format = "python"
            expect(_active_resource(_Host(), None)).to(be_none)

    with context("when key names an existing attribute"):
        with it("should return the string value"):
            class _Host:
                format = "python"
            expect(_active_resource(_Host(), "format")).to(equal("python"))


with description("@instruction decorator"):
    with context("applied to a method"):
        with it("should mark _is_instruction_slot = True"):
            @instruction
            def contexts(self): ...
            expect(getattr(contexts, "_is_instruction_slot", False)).to(be_true)

    with context("applied with collection=True"):
        with it("should mark _instruction_collection = True"):
            @instruction(collection=True)
            def items(self): ...
            expect(items._instruction_collection).to(be_true)


with description("instruction_slot_names"):
    with it("should return names of all @instruction-decorated methods on a class"):
        class _Toolset:
            @instruction
            def contexts(self): ...

            @instruction
            def examples(self): ...

        names = instruction_slot_names(_Toolset)
        expect("contexts" in names).to(be_true)
        expect("examples" in names).to(be_true)


with description("_expand_docstring"):
    with context("a multi-word docstring"):
        with it("should return it unchanged"):
            from primitives.actions.action import agent_instructions

            @agent_instructions
            def my_action(self) -> str:
                """This is literal prose."""
                return ""

            expect(_expand_docstring("This is literal prose.", my_action)).to(
                equal("This is literal prose.")
            )

    with context("an empty docstring"):
        with it("should return an empty string"):
            from primitives.actions.action import agent_instructions

            @agent_instructions
            def empty_action(self) -> str:
                """"""
                return ""

            expect(_expand_docstring("", empty_action)).to(equal(""))

    with context("a single-word framework action name on a generator subclass"):
        with it("should equal the direct load of # Generate in generate.md"):
            from generate.generate import Generate
            kit_dir = _REPO_ROOT / "context_tools" / "actions" / "generate"
            expanded = _expand_docstring(
                "generate", Generate.generate, instance=Generate()
            )
            direct = Instruction(
                _path_for_name(kit_dir, "generate"),
                kit_dir,
            ).expand()
            expect(expanded).to(equal(direct))

    with context("a kit-local path-ref action docstring"):
        with it("should equal the direct load of # Generate in generate.md"):
            from generate.generate import Generate
            kit_dir = _REPO_ROOT / "context_tools" / "actions" / "generate"
            expanded = _expand_docstring(
                "generate", Generate.generate, instance=Generate()
            )
            direct = Instruction(
                _path_for_name(kit_dir, "generate"),
                kit_dir,
            ).expand()
            expect(expanded).to(equal(direct))

    with context("a kit-local repair action docstring"):
        with it("should equal the direct load of context_tools/actions/improvement/repair.md"):
            from context_tools.actions.improvement.improvement import Improvement

            expanded = _expand_docstring(
                "repair", Improvement.repair, instance=Improvement()
            )
            direct = Instruction("repair", _REPAIR_DIR).expand()
            expect(expanded).to(equal(direct))


with description("inline"):
    with context("a host with an @instruction slot named contexts"):
        with it("should return the expanded contexts text"):
            class _Host:
                module_dir = _CLEAN_ENGINEERING_DIR
                format = "python"
                toolset_name = "clean_engineering"

                @instruction
                def contexts(self): ...

            result = _inline(_Host(), "contexts")
            expect(len(result) > 0).to(be_true)
