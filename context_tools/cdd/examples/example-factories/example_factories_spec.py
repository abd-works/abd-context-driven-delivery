"""BDD spec for example factory seams — I{Type} contracts and factory modes.
# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""
import inspect
import sys
from abc import ABC
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from expects import be_true, equal, expect, raise_error
from mamba import context, description, it

from example_factories import ICart, ICartExampleFactory, IProduct, IType


with description("an example factory seam"):
    with context("that exposes domain interfaces"):
        with it("should define IType as an abstract base"):
            expect(issubclass(IType, ABC)).to(be_true)
            expect(inspect.isabstract(IType)).to(be_true)

        with it("should define ICart as an abstract base"):
            expect(issubclass(ICart, ABC)).to(be_true)
            expect(inspect.isabstract(ICart)).to(be_true)

        with it("should define IProduct as an abstract base"):
            expect(issubclass(IProduct, ABC)).to(be_true)
            expect(inspect.isabstract(IProduct)).to(be_true)

        with it("should define ICartExampleFactory as an abstract base"):
            expect(issubclass(ICartExampleFactory, ABC)).to(be_true)
            expect(inspect.isabstract(ICartExampleFactory)).to(be_true)

    with context("whose cart factory method is inspected"):
        with it("should accept a mode parameter defaulting to fake"):
            params = inspect.signature(ICartExampleFactory.cart_with_items).parameters
            expect("mode" in params).to(be_true)
            expect(params["mode"].default).to(equal("fake"))

        with it("should refuse concrete instantiation without cart_with_items"):
            expect(lambda: ICartExampleFactory()).to(raise_error(TypeError))
