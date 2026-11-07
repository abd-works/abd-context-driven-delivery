"""The practice catalogue: the one list of practices, and the toolset an action lists for a practice's or fidelity's slug."""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import be_none, equal, expect
from mamba import description, it

from harness.guidance.practice_catalogue import PracticeCatalogue

_STORIES = "cdd_guidance.practices.stories.stories:Stories"


with description("the practice catalogue"):
    with it("should list the practices in the order the approach walks them"):
        expect(PracticeCatalogue.keys()).to(equal(("stories", "ddd", "ux", "clean_engineering", "bdd")))

    with description("that is asked for the toolset a slug names"):
        with it("should name the practice's toolset for the practice's slug"):
            expect(PracticeCatalogue.toolset_ref("stories")).to(equal(_STORIES))

        with it("should name the practice's toolset and the fidelity for a fidelity's slug"):
            expect(PracticeCatalogue.toolset_ref("stories-story-map")).to(
                equal({"toolset": _STORIES, "fidelity": "story_map"})
            )

        with it("should name the fidelity for its bare name in kebab case"):
            expect(PracticeCatalogue.toolset_ref("story-map")).to(equal({"toolset": _STORIES, "fidelity": "story_map"}))

        with it("should name the fidelity for its bare name in snake case"):
            expect(PracticeCatalogue.toolset_ref("story_map")).to(equal({"toolset": _STORIES, "fidelity": "story_map"}))

        with it("should name nothing for a slug no practice goes by"):
            expect(PracticeCatalogue.toolset_ref("astrology")).to(be_none)
