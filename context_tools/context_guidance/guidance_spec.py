"""BDD spec — guidance resource model layer 1 (co-located markdown extract).
# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("context_tools", "primitives", "utilities"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import contain, equal, expect, not_
from mamba import context, description, it

from context_tools.context_guidance.fixtures.other_tool.other_tool_host import OtherToolHost
from context_tools.context_guidance.fixtures.sample_tool.sample_tool_host import SampleToolHost

_FIXTURES = Path(__file__).resolve().parent / "fixtures"
_SAMPLE_DIR = _FIXTURES / "sample_tool"
_OTHER_DIR = _FIXTURES / "other_tool"


with description("a co-located markdown file beside a host module"):
    with context("with a section heading that matches a property label"):
        with context("with a string property on the host backed by that section"):
            with it("should return the section body when the property is read"):
                host = SampleToolHost(_SAMPLE_DIR)
                text = host.guidance
                expect(text).to(contain("known prose for guidance in sample tool"))
                expect(text).not_to(contain("sample preamble"))

    with context("with known prose written in the module markdown file for that label"):
        with context("with the property read on the host in that module"):
            with it("should return that prose"):
                host = SampleToolHost(_SAMPLE_DIR)
                expect(host.guidance).to(contain("known prose for guidance in sample tool"))

        with context("with an identically named section in a different module folder"):
            with it(
                "should not return prose from the other module file when the host belongs to this module"
            ):
                host = SampleToolHost(_SAMPLE_DIR)
                other = OtherToolHost(_OTHER_DIR)
                expect(host.guidance).to(contain("known prose for guidance in sample tool"))
                expect(host.guidance).not_to(contain("prose from the other module only"))
                expect(other.guidance).to(contain("prose from the other module only"))
                expect(other.guidance).not_to(contain("known prose for guidance in sample tool"))

    with context("with markdown read through the Markdown extract seam"):
        with it("should resolve under context guidance module dir for this host only"):
            host = SampleToolHost(_SAMPLE_DIR)
            expect(host.read_guidance_via_markdown()).to(equal(host.guidance))
