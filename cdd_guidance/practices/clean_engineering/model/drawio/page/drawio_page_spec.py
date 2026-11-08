"""A class card's title on a draw.io page: the class name, read once for the class model and the layout scanners."""

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[6]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from expects import equal, expect
from mamba import context, description, it

from cdd_guidance.practices.clean_engineering.model.drawio.page.drawio_page import class_name_in

_STEREOTYPED = (
    '<p><i style="font-size:9px;">&lt;&lt;Aggregate Root&gt;&gt;</i><br/><b>Cart</b></p><hr size="1"/>'
)


with description("a class card's title"):
    with context("with its stereotypes on a line above the name"):
        with it("should name the class without the line break"):
            expect(class_name_in(_STEREOTYPED)).to(equal("Cart"))

    with context("with its base written after the name"):
        with it("should name the class without the base"):
            expect(class_name_in("<b>Cart : Basket</b>")).to(equal("Cart"))
