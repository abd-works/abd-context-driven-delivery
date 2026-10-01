"""Approach page copy lives in markdown so it can be hand-edited."""
import sys
import tempfile
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("practices", "tools"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import equal, expect
from mamba import description, it

from catalog_generator.approach_copy import load_approach_copy
from catalog_generator.catalog_generator import Catalog
from installation.installer import Installer  # noqa: F401

_MINIMAL_MD = """# Approach

HAND-EDITABLE-SUBHEAD

## Stages

### Context

id: context
shape: square
scope_name: Context
scope_width: square
items: Business Model | User Traction | Operating Benchmarks

HAND-EDITABLE-STAGE-COPY

## Context Driven Delivery Practices

### Product Engineering

slug: product-engineering
kind: descriptions

- HAND-EDITABLE-BULLET

## Library

HAND-EDITABLE-LIBRARY
"""


with description("load_approach_copy"):
    with it("reads subhead, stages, practices, and library from markdown"):
        path = Path(tempfile.mkdtemp()) / "cdd-approach.md"
        path.write_text(_MINIMAL_MD, encoding="utf-8")
        copy = load_approach_copy(path)
        expect(copy.subhead).to(equal("HAND-EDITABLE-SUBHEAD"))
        expect(copy.principles_heading).to(equal("Context Driven Delivery Practices"))
        expect(copy.library_heading).to(equal("HAND-EDITABLE-LIBRARY"))
        expect(copy.stages[0]["id"]).to(equal("context"))
        expect(copy.stages[0]["paras"][0]).to(equal("HAND-EDITABLE-STAGE-COPY"))
        expect(copy.practices[0]["slug"]).to(equal("product-engineering"))
        expect(copy.practices[0]["bullets"][0]).to(equal("HAND-EDITABLE-BULLET"))


with description("Catalog approach page"):
    with it("renders copy from the approach markdown file"):
        tmp = Path(tempfile.mkdtemp())
        md = tmp / "cdd-approach.md"
        md.write_text(_MINIMAL_MD, encoding="utf-8")
        catalog = Catalog(out_root=str(tmp / "out"), approach_md_path=md)
        catalog._board_tools = []
        catalog._write_approach_page()
        html = (tmp / "out" / "cdd-approach.html").read_text(encoding="utf-8")
        expect("HAND-EDITABLE-SUBHEAD" in html).to(equal(True))
        expect("HAND-EDITABLE-STAGE-COPY" in html).to(equal(True))
        expect("HAND-EDITABLE-BULLET" in html).to(equal(True))
        expect("HAND-EDITABLE-LIBRARY" in html).to(equal(True))
