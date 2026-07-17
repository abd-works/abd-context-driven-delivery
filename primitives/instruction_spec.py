"""BDD spec for instruction.py — Instruction, routing helpers, @instruction slot decorator."""
import sys
from pathlib import Path

from expects import be_none, be_true, contain, equal, expect
from mamba import before, context, description, it

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

_CLEAN_ENGINEERING_DIR = _REPO_ROOT / "clean_engineering"
_GENERATOR_DIR = _REPO_ROOT / "generator"

from primitives.instruction import Instruction
from primitives.instruction_routing import active_resource, format_keys, path_for_name, path_for_templates
from primitives.instruction_slot import expand_docstring, inline, instruction, instruction_slot_names


with description("Instruction"):
    with context("constructed with plain prose"):
        with before.each:
            self.instruction = Instruction("Write clean production code.", _CLEAN_ENGINEERING_DIR)

        with it("should return the prose unchanged when expand is called"):
            expect(self.instruction.expand()).to(equal("Write clean production code."))

        with it("should return False from matches_file_or_folder"):
            expect(self.instruction.matches_file_or_folder()).to(equal(False))

    with context("constructed with a § section reference"):
        with before.each:
            self.instruction = Instruction("§ Concepts", _CLEAN_ENGINEERING_DIR)

        with it("should return True from matches_file_or_folder"):
            expect(self.instruction.matches_file_or_folder()).to(be_true)

        with it("should expand to the Concepts section of clean_engineering.md"):
            result = self.instruction.expand()
            expect("Concepts" in result).to(be_true)

    with context("constructed with a relative file path"):
        with before.each:
            self.instruction = Instruction(
                "fidelities/language/concepts.md", _CLEAN_ENGINEERING_DIR
            )

        with it("should return True from matches_file_or_folder"):
            expect(self.instruction.matches_file_or_folder()).to(be_true)

        with it("should expand to non-empty content"):
            expect(len(self.instruction.expand()) > 0).to(be_true)

    with context("Instruction.ref built from a host"):
        with before.each:
            class _Host:
                module_dir = _CLEAN_ENGINEERING_DIR
                format = "python"
                toolset_name = "clean_engineering"

            self.ref = Instruction.ref(_Host(), "concepts")

        with it("should expand to non-empty content containing the word Concepts"):
            result = self.ref.expand()
            expect(len(result) > 0).to(be_true)
            expect(result).to(contain("Concepts"))


with description("path_for_name"):
    with context("when a subfolder with that name exists"):
        with it("should return name with trailing slash"):
            expect(path_for_name(_CLEAN_ENGINEERING_DIR, "fidelities")).to(equal("fidelities/"))

    with context("when a .md file with that name exists"):
        with it("should return the bare name"):
            expect(path_for_name(_CLEAN_ENGINEERING_DIR, "clean_engineering")).to(
                equal("clean_engineering")
            )

    with context("when neither file nor folder exists"):
        with it("should return a § section reference"):
            expect(path_for_name(_CLEAN_ENGINEERING_DIR, "nonexistent").startswith("§")).to(
                equal(True)
            )


with description("path_for_templates"):
    with context("when shared templates/ folder exists"):
        with it("should return a path under templates/ containing clean_engineering-templates"):
            hint = path_for_templates(_CLEAN_ENGINEERING_DIR, "clean_engineering", "python")
            expect("templates/" in hint or hint == "templates").to(equal(True))
            expect("clean_engineering-templates" in hint or hint == "templates").to(equal(True))

    with context("when active_format is None"):
        with it("should return a non-empty fallback string"):
            expect(
                len(path_for_templates(_CLEAN_ENGINEERING_DIR, "clean_engineering", None)) > 0
            ).to(equal(True))


with description("format_keys"):
    with context("a module_dir with a formats/ directory"):
        with it("should return a sorted list including python"):
            keys = format_keys(_CLEAN_ENGINEERING_DIR)
            expect("python" in keys).to(be_true)

    with context("a module_dir with no formats/ directory"):
        with it("should return an empty list"):
            expect(format_keys(_REPO_ROOT / "primitives")).to(equal([]))


with description("active_resource"):
    with context("when key is None"):
        with it("should return None"):
            class _Host:
                format = "python"
            expect(active_resource(_Host(), None)).to(be_none)

    with context("when key names an existing attribute"):
        with it("should return the string value"):
            class _Host:
                format = "python"
            expect(active_resource(_Host(), "format")).to(equal("python"))


with description("@instruction decorator"):
    with context("applied to a method"):
        with it("should mark _is_instruction_slot = True"):
            @instruction
            def concepts(self): ...
            expect(getattr(concepts, "_is_instruction_slot", False)).to(be_true)

    with context("applied with collection=True"):
        with it("should mark _instruction_collection = True"):
            @instruction(collection=True)
            def rules(self): ...
            expect(rules._instruction_collection).to(be_true)


with description("instruction_slot_names"):
    with it("should return names of all @instruction-decorated methods on a class"):
        class _Toolset:
            @instruction
            def concepts(self): ...

            @instruction
            def examples(self): ...

        names = instruction_slot_names(_Toolset)
        expect("concepts" in names).to(be_true)
        expect("examples" in names).to(be_true)


with description("expand_docstring"):
    with context("a multi-word docstring"):
        with it("should return it unchanged"):
            from action.action import action

            @action
            def my_action(self) -> str:
                """This is literal prose."""
                return ""

            expect(expand_docstring("This is literal prose.", my_action)).to(
                equal("This is literal prose.")
            )

    with context("an empty docstring"):
        with it("should return an empty string"):
            from action.action import action

            @action
            def empty_action(self) -> str:
                """"""
                return ""

            expect(expand_docstring("", empty_action)).to(equal(""))

    with context("a single-word framework action name on a generator subclass"):
        with it("should equal the direct load of base-generator/generate.md"):
            from generator.generator import Generator
            expanded = expand_docstring(
                "generate", Generator.generate, instance=Generator()
            )
            direct = Instruction("base-generator/generate", _GENERATOR_DIR).expand()
            expect(expanded).to(equal(direct))

    with context("a path-ref action docstring on the generator module"):
        with it("should equal the direct load of base-generator/generate.md"):
            from generator.generator import Generator
            expanded = expand_docstring("base-generator/generate", Generator.generate)
            direct = Instruction("base-generator/generate", _GENERATOR_DIR).expand()
            expect(expanded).to(equal(direct))

    with context("a path-ref action docstring that resolves to base-generator/repair.md"):
        with it("should equal the direct load of base-generator/repair.md"):
            from generator.generator import Generator
            expanded = expand_docstring("base-generator/repair", Generator.repair)
            direct = Instruction("base-generator/repair", _GENERATOR_DIR).expand()
            expect(expanded).to(equal(direct))


with description("inline"):
    with context("a host with an @instruction slot named concepts"):
        with it("should return the expanded concepts text"):
            class _Host:
                module_dir = _CLEAN_ENGINEERING_DIR
                format = "python"
                toolset_name = "clean_engineering"

                @instruction
                def concepts(self): ...

            result = inline(_Host(), "concepts")
            expect(len(result) > 0).to(be_true)
