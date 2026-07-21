"""BDD spec for declared.py — DeclaredMember, DeclaredOperation, DeclaredProperty."""
import sys
from pathlib import Path

from expects import be_none, be_true, contain, equal, expect
from mamba import before, context, description, it

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("primitives", "utilities", "contexts"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

_CLEAN_CODE_DIR = _REPO_ROOT / "contexts" / "clean_engineering"
_BDD_DIR = _REPO_ROOT / "contexts" / "bdd"

from primitives.declared import DeclaredMember, DeclaredOperation, DeclaredProperty


class _OperationHost:
    def generate_code(self) -> str:
        """Generates code for the domain."""
        return "generated"


class _PropertyHost:
    module_dir = _CLEAN_CODE_DIR
    format = "python"
    toolset_name = "clean_engineering"


class _BddFormatsHost:
    module_dir = _BDD_DIR
    format = "python"
    toolset_name = "bdd"


with description("DeclaredMember"):
    with context("constructed with name only"):
        with it("should store the name"):
            # Arrange / Act
            member = DeclaredMember(name="contexts")
            # Assert
            expect(member.name).to(equal("contexts"))

        with it("should have label as None"):
            expect(DeclaredMember(name="contexts").label).to(be_none)

        with it("should have target as None"):
            expect(DeclaredMember(name="contexts").target).to(be_none)

    with context("constructed with name and label"):
        with it("should store both"):
            member = DeclaredMember(name="templates", label="formats")
            expect(member.name).to(equal("templates"))
            expect(member.label).to(equal("formats"))

    with context("equality"):
        with it("should equal another DeclaredMember with the same fields"):
            # Arrange
            a = DeclaredMember(name="contexts", label="contexts")
            b = DeclaredMember(name="contexts", label="contexts")
            # Assert
            expect(a).to(equal(b))


with description("DeclaredOperation"):
    with context("with a wired target on the host"):
        with before.each:
            self.op = DeclaredOperation(target="generate_code")
            object.__setattr__(self.op, "name", "generate_output")
            self.host = _OperationHost()

        with it("should return the target callable when route is called"):
            # Act / Assert
            expect(self.op.route(self.host)).to(equal(self.host.generate_code))

    with context("with no target"):
        with before.each:
            self.op = DeclaredOperation()
            object.__setattr__(self.op, "name", "generate_output")
            self.host = _OperationHost()

        with it("should return None when route is called"):
            expect(self.op.route(self.host)).to(be_none)

    with context("accessed via descriptor protocol on an instance"):
        with before.each:
            class _Container:
                generate_output = DeclaredOperation(target="generate_code")

                def generate_code(self) -> str:
                    """Docstring for generate_code."""
                    return "generated"

            self.container = _Container()

        with it("should return a callable when accessed on an instance"):
            expect(callable(self.container.generate_output)).to(equal(True))

        with it("should return the target docstring when invoked"):
            expect(self.container.generate_output()).to(equal("Docstring for generate_code."))

    with context("name inferred via __set_name__"):
        with it("should assign the attribute name when name is None"):
            class _Container:
                generate_output = DeclaredOperation()

            expect(_Container.generate_output.name).to(equal("generate_output"))


with description("DeclaredProperty"):
    with context("examples property on a clean-code host"):
        with before.each:
            self.prop = DeclaredProperty("examples")
            self.host = _PropertyHost()

        with it("should route to an Instruction that expands to non-empty content"):
            expect(len(self.prop.route(self.host).expand()) > 0).to(be_true)

    with context("contexts property on a clean-code host"):
        with before.each:
            self.prop = DeclaredProperty("contexts")
            self.host = _PropertyHost()

        with it("should route to an Instruction whose expand contains Contexts"):
            expect(self.prop.route(self.host).expand()).to(contain("Contexts"))

    with context("templates property with active_key format"):
        with before.each:
            self.prop = DeclaredProperty("templates", active_key="format")
            self.host = _PropertyHost()

        with it("should route to a non-empty python templates file"):
            expect(len(self.prop.route(self.host).expand()) > 0).to(be_true)

    with context("formats property discover_keys"):
        with before.each:
            self.prop = DeclaredProperty("formats")
            self.host = _BddFormatsHost()

        with it("should return a list including python"):
            keys = self.prop.discover_keys(self.host)
            expect("python" in keys).to(be_true)

    with context("name inferred via __set_name__"):
        with it("should use the attribute name when name is None"):
            class _Container:
                contexts = DeclaredProperty()

            expect(_Container.contexts.name).to(equal("contexts"))
