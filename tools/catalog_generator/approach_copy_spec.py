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
from catalog_generator.approach_copy import APPROACH_MARKDOWN
from catalog_generator.foundry_chrome import approach_board_stages, render_hub_board
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


_BOARD_STAGE_MD = """# Approach

Subhead

## Stages

### Discovery

id: discovery
board_key: discovery
items: ZZ-CHIP

ZZ-PARA

### Specification

id: specification
board_key: spec
items: Spec Chip

Spec paragraph

### Implement

id: implementation
board_key: engineer
items: Engineer Chip

Engineer paragraph
"""


with description("approach board stages"):
    with it("reads stage chips and paragraphs from approach markdown"):
        path = Path(tempfile.mkdtemp()) / "cdd-approach.md"
        path.write_text(_BOARD_STAGE_MD, encoding="utf-8")
        stages = approach_board_stages(path)
        expect(stages["discovery"]["items"]).to(equal(("ZZ-CHIP",)))
        expect(stages["discovery"]["paras"][0]).to(equal("ZZ-PARA"))

    with it("renders those chips on the catalog board"):
        path = Path(tempfile.mkdtemp()) / "cdd-approach.md"
        path.write_text(_BOARD_STAGE_MD, encoding="utf-8")
        html = render_hub_board([], [], [], approach_md_path=path)
        expect("ZZ-CHIP" in html).to(equal(True))
        expect("ZZ-PARA" in html).to(equal(True))


with description("Catalog approach markdown folder"):
    with it("reads approach copy from the generator markdown folder"):
        catalog = Catalog(out_root=str(Path(tempfile.mkdtemp()) / "out"))
        source = Path(__file__).resolve().parent / "markdown" / "cdd-approach.md"
        expect(catalog.approach_md_path).to(equal(source))
        expect(source.is_file()).to(equal(True))
        expect("CDD harness" in catalog._approach_copy().subhead).to(equal(True))


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


with description("stage example links"):
    with it("hyperlinks discovery, specification, and implementation on the board"):
        html = render_hub_board([], [], [], approach_md_path=APPROACH_MARKDOWN)
        expect('href="examples/discovery.html"' in html).to(equal(True))
        expect('href="examples/specification.html"' in html).to(equal(True))
        expect('href="examples/implementation.html"' in html).to(equal(True))

    with it("copies those assets and expands them under the Iterate and Learn diagram"):
        tmp = Path(tempfile.mkdtemp())
        catalog = Catalog(out_root=str(tmp / "out"), approach_md_path=APPROACH_MARKDOWN)
        catalog._board_tools = []
        catalog._write_approach_page()
        html = (tmp / "out" / "cdd-approach.html").read_text(encoding="utf-8")
        expect('id="approach-stage-examples"' in html).to(equal(True))
        expect('data-stage-id="discovery"' in html).to(equal(True))
        expect('data-stage-id="specification"' in html).to(equal(True))
        expect('data-stage-id="implementation"' in html).to(equal(True))
        expect("a simple graph is easier to change, compare, and reorganize" in html).to(equal(True))
        expect(
            "<em>a simple graph is easier to change, compare, and reorganize. Humans catch AI Order-of-Magnitude sizing errors.</em>"
            in html
        ).to(equal(True))
        expect("viewer.diagrams.net" in html).to(equal(True))
        expect("approach-stage-drawio-zoom" in html).to(equal(True))
        expect("approach-stage-drawio" in html).to(equal(True))
        expect("approach-stage-column" in html).to(equal(True))
        expect("toggleStageColumn" in html).to(equal(True))
        expect("openNextColumn" in html).to(equal(True))
        expect("Display Create Account" in html).to(equal(True))
        expect('id="catalog-monaco"' in html).to(equal(True))
        expect("&quot;start&quot;:" in html).to(equal(True))
        expect("showStageExample" in html).to(equal(True))
        expect((tmp / "out" / "examples" / "story_map.png").is_file()).to(equal(True))
