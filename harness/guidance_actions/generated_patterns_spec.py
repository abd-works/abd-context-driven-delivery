"""Specs for the patterns content is generated with, recorded where it is written and read back where it is judged."""
import tempfile
from pathlib import Path

from expects import contain, equal, expect
from mamba import description, it

from harness.graph.pattern_overlays import PatternOverlays
from harness.guidance_actions.generated_patterns import GeneratedPatterns
import cdd_guidance.patterns  # noqa: F401 - registers the patterns with the graph's overlays


with description("the patterns content is generated with") as self:
    with it("should name the patterns recorded for content where it was generated"):
        root = Path(tempfile.mkdtemp())
        app = root / "app"
        (app / "src").mkdir(parents=True)
        GeneratedPatterns(PatternOverlays(["lern_domain_driven", "cdd_web_domain_access"])).record_content([app])
        expect(GeneratedPatterns(PatternOverlays()).recorded_for([app / "src" / "board.tsx"], root)).to(equal(["lern_domain_driven", "cdd_web_domain_access"]))

    with it("should tell the agent how to record them in any other folder, with each pattern's roles"):
        root = Path(tempfile.mkdtemp())
        told = GeneratedPatterns(PatternOverlays(["cdd_web_domain_access"])).record_content([root])
        expect(told).to(contain("- cdd_web_domain_access: Domain, Tool, Contract"))

    with it("should tell nothing when no pattern is applied"):
        expect(GeneratedPatterns(PatternOverlays()).record_content([Path(tempfile.mkdtemp())])).to(equal(""))

    with it("should name none for content no folder records"):
        root = Path(tempfile.mkdtemp())
        expect(GeneratedPatterns(PatternOverlays()).recorded_for([root / "board.tsx"], root)).to(equal([]))
