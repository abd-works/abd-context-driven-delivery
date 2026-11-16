"""The classes one source file names, each with the module it names it from."""

from pathlib import Path
import sys

_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import contain, equal, expect
from mamba import description, context, it

from cdd_guidance.practices.clean_engineering.model.script_imports import ClassReference, ScriptImports

_ROOT = Path("/repo")


def _references(relative: str, text: str) -> list[ClassReference]:
    return ScriptImports(text).class_references(_ROOT / relative, _ROOT)


with description("script imports"):
    with context("with a Python file"):
        with it("should name each class a from-import brings in with the module, its alias dropped"):
            text = "from harness.graph.graph import Node, Edge as Link\n"
            expect(_references("shop/checkout.py", text)).to(equal([ClassReference("harness/graph/graph", "Node"), ClassReference("harness/graph/graph", "Edge")]))

        with it("should read a parenthesised list with comments"):
            text = "from cart.cart import (\n    Cart,  # the basket\n    Line,\n)\n"
            expect(_references("shop/checkout.py", text)).to(equal([ClassReference("cart/cart", "Cart"), ClassReference("cart/cart", "Line")]))

        with it("should resolve a relative import against the file's package"):
            expect(_references("shop/till/checkout.py", "from ..cart import Cart\n")).to(equal([ClassReference("shop/cart", "Cart")]))

        with it("should name a class reached through a module imported with an alias"):
            text = "import harness.graph.graph as g\n\nnode = g.Node()\n"
            expect(_references("shop/checkout.py", text)).to(equal([ClassReference("harness/graph/graph", "Node")]))

        with it("should name a class reached through a module imported from its package"):
            text = "from harness.graph import graph\n\nnode = graph.Node()\n"
            expect(_references("shop/checkout.py", text)).to(contain(ClassReference("harness/graph/graph", "Node")))

        with it("should keep a star import as a star"):
            expect(_references("shop/checkout.py", "from cart.cart import *\n")).to(equal([ClassReference("cart/cart", "*")]))

    with context("with a TypeScript file"):
        with it("should name the default and braced names with the path from the source root"):
            text = "import Board, { Ticket, type Lane as Row } from '../kanban/board';\n"
            expected = [ClassReference("app/kanban/board", name) for name in ("Board", "Ticket", "Lane")]
            expect(_references("app/ui/view.ts", text)).to(equal(expected))

        with it("should name a class reached through a namespace import"):
            text = "import * as board from './board';\n\nconst made = new board.Ticket();\n"
            expect(_references("app/kanban/view.ts", text)).to(equal([ClassReference("app/kanban/board", "Ticket")]))

        with it("should name what a re-export passes on, and keep an export of everything as a star"):
            text = "export { Ticket } from './ticket';\nexport * from './lane';\n"
            expect(_references("app/kanban/index.ts", text)).to(equal([ClassReference("app/kanban/ticket", "Ticket"), ClassReference("app/kanban/lane", "*")]))

        with it("should keep a package's name as the import spells it"):
            expect(_references("app/ui/view.ts", "import { useState } from 'react';\n")).to(equal([ClassReference("react", "useState")]))
