"""Unit spec: the names a repository's Python calls or imports, checked against what still exists.

One small repository, written once into a temporary folder, holds a file for each case; it is checked once, with the
names Python reports for its built-in types and not the standard library's source, and each example reads what was
found in its own file. The whole repository, and TypeScript through its compiler, are checked by
names_exist_heavy_spec.py.
"""
import shutil
import sys
import tempfile
from pathlib import Path

from expects import be_empty, equal, expect
from mamba import after, before, description, it

sys.path.insert(0, str(Path(__file__).resolve().parent))

from names_exist import MissingName, PythonNames  # noqa: E402

_FILES = {
    "holder.py": "from contextvars import ContextVar\n\n\n@contextmanager\ndef answering():\n    yield ContextVar('call')\n",
    "session.py": "class Session:\n    def __init__(self):\n        self.practices = []\n\n    def session_practices(self):\n        return self.practices\n",
    "old_caller.py": "def outputs(session):\n    return session.practice_outputs()\n",
    "new_caller.py": "def outputs(session):\n    return session.session_practices()\n",
    "shop/__init__.py": "from .cart import *\n",
    "shop/cart.py": "class Cart:\n    pass\n",
    "renamed_import.py": "from shop.cart import Basket\n",
    "moved_module.py": "from shop.basket import Cart\n",
    "star_import.py": "from shop import Cart\n",
    "cart_spec.py": "with description('a cart'):\n    with it('should be empty'):\n        assert _empty(self)\n\n\ndef _empty(spec):\n    return True\n",
    "broken_spec.py": "def read(toolset):\n    return toolset.missing_flag  # noqa: names-exist\n",
    "options.py": "def chosen(arguments, parser):\n    parser.add_argument('--from-latest')\n    return arguments.from_latest\n",
}


def _found_in(spec, file: str) -> list[MissingName]:
    return [found for found in spec.missing if found.file == file]


with description("the names a repository's Python code uses"):
    with before.all:
        self.root = Path(tempfile.mkdtemp(prefix="names-exist-"))
        for name, text in _FILES.items():
            (self.root / name).parent.mkdir(parents=True, exist_ok=True)
            (self.root / name).write_text(text, encoding="utf-8")
        self.missing = PythonNames(self.root, sorted(_FILES), reads_outside=False).missing()

    with after.all:
        shutil.rmtree(self.root, ignore_errors=True)

    with description("with a file that uses a name a merge dropped from its imports"):
        with it("should name the file, the line and the name"):
            expect(_found_in(self, "holder.py")).to(equal([MissingName("holder.py", 4, "contextmanager", "undefined name")]))

    with description("with a member renamed on its class while another file still calls the old name"):
        with it("should name the old member where it is still called"):
            expect(_found_in(self, "old_caller.py")).to(equal([MissingName("old_caller.py", 2, "practice_outputs", "member nothing defines")]))

    with description("with every caller moved to the member's new name"):
        with it("should name nothing"):
            expect(_found_in(self, "new_caller.py")).to(be_empty)

    with description("with an import of a name its own module of the repository no longer defines"):
        with it("should name the module and the name"):
            expect(_found_in(self, "renamed_import.py")).to(equal([MissingName("renamed_import.py", 1, "shop.cart.Basket", "name its module does not define")]))

    with description("with an import of a module the repository's package no longer holds"):
        with it("should name the module"):
            expect(_found_in(self, "moved_module.py")).to(equal([MissingName("moved_module.py", 1, "shop.basket", "module the repository does not hold")]))

    with description("with an import a package offers through a star import of its own module"):
        with it("should name nothing"):
            expect(_found_in(self, "star_import.py")).to(be_empty)

    with description("with a spec whose blocks use Mamba's names and a helper written at the end of the file"):
        with it("should name nothing"):
            expect(_found_in(self, "cart_spec.py")).to(be_empty)

    with description("with a spec that reads a missing member on purpose and says so on its line"):
        with it("should name nothing"):
            expect(_found_in(self, "broken_spec.py")).to(be_empty)

    with description("with an argparse option read from the parsed arguments"):
        with it("should name only the parser's own members, which the standard library defines"):
            expect([found.name for found in _found_in(self, "options.py")]).to(equal(["add_argument"]))
