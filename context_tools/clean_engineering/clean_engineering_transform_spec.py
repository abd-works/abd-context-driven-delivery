"""BDD spec for CleanEngineering transform tool — sideways format conversion."""

import sys
from pathlib import Path
from typing import Any

from expects import be_true, contain, equal, expect, have_len, have_key
from mamba import before, context, description, it

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("primitives", "utilities", "context_tools"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

import context_tools  # noqa: F401
from tools.tool import _ToolsetLoader

_OOAD_TOOLSET = "context_tools.clean_engineering.clean_engineering:CleanEngineering"


def _load_clean_engineering(*, fidelity: str = "modules", format: str = "markdown"):
    toolset_cls = _ToolsetLoader.instance().load(_OOAD_TOOLSET)
    return toolset_cls(fidelity=fidelity, format=format)


def _invoke_transform(instance, source_format: str, target_format: str, content: str) -> dict:
    return instance.transform(
        source_format=source_format,
        target_format=target_format,
        content=content,
    )


_SAMPLE_MARKDOWN = """\
# Shop

*Shop* is the cart module.

## Cart

*Cart* holds line items and places orders.

Cart(owner: str)
------
owner: str
----
place_order(): Order
"""

_SAMPLE_PYTHON = """\
class Cart:
    \"\"\"Cart holds line items and places orders.\"\"\"

    def __init__(self, owner: str) -> None:
        self.owner = owner

    def place_order(self) -> "Order": ...
"""

_SAMPLE_TYPESCRIPT = """\
class Cart {
    placeOrder(): Order {}
}
"""

_SAMPLE_JAVA = """\
class Cart {
    public Order placeOrder() {}
}
"""

_SAMPLE_JSON = """\
{
  "name": "model",
  "classes": [
    {"name": "Cart", "sequentialOrder": 1, "intent": "A shopping cart.", "properties": [], "operations": [], "relationships": [], "collaborators": []}
  ]
}
"""

_SAMPLE_JAVASCRIPT = """\
class Cart {
  constructor(owner) {
    this.owner = owner;
  }
  placeOrder() {}
}
"""

_SAMPLE_MODULES_MARKDOWN = """\
# checks

Resolve d20 checks.

- **Purpose:** Resolve d20 + trait against difficulty.
- **Seam (terms):** Trait, Check, CheckResult
- **Dependencies (one-way):** *(none)*

# character

Character sheet ownership.

- **Purpose:** Owns the hero sheet and ISource.
- **Seam (terms):** Character, Ability, ISource
- **Dependencies (one-way):** checks
"""


with description("OoadAnalysis transform tool"):
    with context("transform called with unrecognised source_format"):
        with before.each:
            self.CleanEngineering = _load_clean_engineering()

        with it("should raise ValueError"):
            from expects import raise_error
            expect(
                lambda: _invoke_transform(self.CleanEngineering, "xml", "python", "content")
            ).to(raise_error(ValueError))

    with context("transform called with unrecognised target_format"):
        with before.each:
            self.CleanEngineering = _load_clean_engineering()

        with it("should raise ValueError"):
            from expects import raise_error
            expect(
                lambda: _invoke_transform(self.CleanEngineering, "markdown", "xml", "content")
            ).to(raise_error(ValueError))

    with context("transform from markdown to python"):
        with before.each:
            self.CleanEngineering = _load_clean_engineering(fidelity="modules", format="markdown")
            self.result = _invoke_transform(
                self.CleanEngineering, "markdown", "python", _SAMPLE_MARKDOWN
            )

        with it("should return a dict"):
            expect(isinstance(self.result, dict)).to(be_true)

        with it("should include a content key"):
            expect(self.result).to(have_key("content"))

        with it("should preserve the class name Cart in the output"):
            expect(self.result["content"]).to(contain("Cart"))

        with it("should include format in the result"):
            expect(self.result["format"]).to(equal("python"))

    with context("transform from python to markdown"):
        with before.each:
            self.CleanEngineering = _load_clean_engineering(fidelity="modules", format="python")
            self.result = _invoke_transform(
                self.CleanEngineering, "python", "markdown", _SAMPLE_PYTHON
            )

        with it("should preserve the class name Cart in the output"):
            expect(self.result["content"]).to(contain("Cart"))

        with it("should include format in the result"):
            expect(self.result["format"]).to(equal("markdown"))

    with context("transform from markdown to typescript"):
        with before.each:
            self.CleanEngineering = _load_clean_engineering(fidelity="modules", format="markdown")
            self.result = _invoke_transform(
                self.CleanEngineering, "markdown", "typescript", _SAMPLE_MARKDOWN
            )

        with it("should preserve the class name Cart in the output"):
            expect(self.result["content"]).to(contain("Cart"))

        with it("should include format in the result"):
            expect(self.result["format"]).to(equal("typescript"))

    with context("transform from typescript to markdown"):
        with before.each:
            self.CleanEngineering = _load_clean_engineering(fidelity="modules", format="markdown")
            self.result = _invoke_transform(
                self.CleanEngineering, "typescript", "markdown", _SAMPLE_TYPESCRIPT
            )

        with it("should preserve the class name Cart in the output"):
            expect(self.result["content"]).to(contain("Cart"))

        with it("should include format in the result"):
            expect(self.result["format"]).to(equal("markdown"))

    with context("transform from markdown to java"):
        with before.each:
            self.CleanEngineering = _load_clean_engineering(fidelity="modules", format="markdown")
            self.result = _invoke_transform(
                self.CleanEngineering, "markdown", "java", _SAMPLE_MARKDOWN
            )

        with it("should preserve the class name Cart in the output"):
            expect(self.result["content"]).to(contain("Cart"))

        with it("should include format in the result"):
            expect(self.result["format"]).to(equal("java"))

    with context("transform from java to markdown"):
        with before.each:
            self.CleanEngineering = _load_clean_engineering(fidelity="modules", format="markdown")
            self.result = _invoke_transform(
                self.CleanEngineering, "java", "markdown", _SAMPLE_JAVA
            )

        with it("should preserve the class name Cart in the output"):
            expect(self.result["content"]).to(contain("Cart"))

        with it("should include format in the result"):
            expect(self.result["format"]).to(equal("markdown"))

    with context("transform from markdown to json"):
        with before.each:
            self.CleanEngineering = _load_clean_engineering(fidelity="modules", format="markdown")
            self.result = _invoke_transform(
                self.CleanEngineering, "markdown", "json", _SAMPLE_MARKDOWN
            )

        with it("should preserve the class name Cart in the output"):
            expect(self.result["content"]).to(contain("Cart"))

        with it("should include format in the result"):
            expect(self.result["format"]).to(equal("json"))

    with context("transform from json to markdown"):
        with before.each:
            self.CleanEngineering = _load_clean_engineering(fidelity="modules", format="markdown")
            self.result = _invoke_transform(
                self.CleanEngineering, "json", "markdown", _SAMPLE_JSON
            )

        with it("should preserve the class name Cart in the output"):
            expect(self.result["content"]).to(contain("Cart"))

        with it("should include format in the result"):
            expect(self.result["format"]).to(equal("markdown"))

    with context("transform from markdown to javascript"):
        with before.each:
            self.CleanEngineering = _load_clean_engineering(fidelity="modules", format="markdown")
            self.result = _invoke_transform(
                self.CleanEngineering, "markdown", "javascript", _SAMPLE_MARKDOWN
            )

        with it("should preserve the class name Cart in the output"):
            expect(self.result["content"]).to(contain("Cart"))

        with it("should include format in the result"):
            expect(self.result["format"]).to(equal("javascript"))

    with context("transform from javascript to markdown"):
        with before.each:
            self.CleanEngineering = _load_clean_engineering(fidelity="modules", format="markdown")
            self.result = _invoke_transform(
                self.CleanEngineering, "javascript", "markdown", _SAMPLE_JAVASCRIPT
            )

        with it("should preserve the class name Cart in the output"):
            expect(self.result["content"]).to(contain("Cart"))

        with it("should include format in the result"):
            expect(self.result["format"]).to(equal("markdown"))

    with context("transform from markdown to drawio"):
        with before.each:
            self.CleanEngineering = _load_clean_engineering(fidelity="modules", format="markdown")
            self.result = _invoke_transform(
                self.CleanEngineering, "markdown", "drawio", _SAMPLE_MARKDOWN
            )

        with it("should preserve the class name Cart in the output"):
            expect(self.result["content"]).to(contain("Cart"))

        with it("should render UML class diagram for typed classes"):
            expect(self.result["content"]).to(contain('id="CleanEngineering-model"'))

        with it("should include format in the result"):
            expect(self.result["format"]).to(equal("drawio"))

    with context("transform modules markdown to drawio modules view"):
        with before.each:
            self.CleanEngineering = _load_clean_engineering(fidelity="modules", format="markdown")
            self.result = _invoke_transform(
                self.CleanEngineering, "markdown", "drawio", _SAMPLE_MODULES_MARKDOWN
            )

        with it("should include format in the result"):
            expect(self.result["format"]).to(equal("drawio"))

        with it("should render Modules Context diagram"):
            expect(self.result["content"]).to(contain('id="modules-context"'))

        with it("should render seam-term bullets"):
            expect(self.result["content"]).to(contain("\u2022 Trait"))
            expect(self.result["content"]).to(contain("\u2022 ISource"))

        with it("should not include stack/tech callouts"):
            expect("stack / tech" in self.result["content"]).to(equal(False))

        with it("should draw character → checks dependency"):
            expect(self.result["content"]).to(contain('source="character"'))
            expect(self.result["content"]).to(contain('target="checks"'))

    with context("transform modules drawio back to markdown"):
        with before.each:
            self.CleanEngineering = _load_clean_engineering(fidelity="modules", format="markdown")
            drawio = _invoke_transform(
                self.CleanEngineering, "markdown", "drawio", _SAMPLE_MODULES_MARKDOWN
            )["content"]
            self.result = _invoke_transform(
                self.CleanEngineering, "drawio", "markdown", drawio
            )

        with it("should include format in the result"):
            expect(self.result["format"]).to(equal("markdown"))

        with it("should recover module headings"):
            expect(self.result["content"]).to(contain("# checks"))
            expect(self.result["content"]).to(contain("# character"))

        with it("should recover seam terms"):
            expect(self.result["content"]).to(contain("Trait"))
            expect(self.result["content"]).to(contain("ISource"))

        with it("should recover one-way dependencies"):
            expect(self.result["content"]).to(contain("checks"))

    with context("transform raises ValueError for unrecognised new formats"):
        with before.each:
            self.CleanEngineering = _load_clean_engineering()

        with it("should raise ValueError listing all supported formats"):
            from expects import raise_error
            expect(
                lambda: _invoke_transform(self.CleanEngineering, "yaml", "markdown", "content")
            ).to(raise_error(ValueError))
