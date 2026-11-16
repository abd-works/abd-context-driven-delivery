"""The practice catalogue: the one list of practices, and the toolset an action lists for a practice's or fidelity's slug."""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import be, be_none, contain, equal, expect, raise_error
from mamba import before, description, it

from harness.guidance.practice_catalogue import PRACTICE_CATALOGUE, UnknownPractice
import cdd_guidance.practices  # noqa: F401 - registers the practices with the practice catalogue
import cdd_guidance.actions  # noqa: F401 - registers the actions with the action catalogue



with description("the practice catalogue"):
    with it("should list the practices in the order the approach walks them"):
        expect(PRACTICE_CATALOGUE.names).to(equal(("stories", "ddd", "ux", "clean_engineering", "bdd")))

    with it("should name a practice key it does not hold as an unknown practice"):
        expect(lambda: PRACTICE_CATALOGUE.create("clean-engineering")).to(raise_error(UnknownPractice))

    with description("whose practice is asked for the guidance a slug names"):
        with before.all:
            self.stories = PRACTICE_CATALOGUE.create("stories")

        with it("should answer itself for the practice's slug"):
            expect(self.stories.answers_to("stories")).to(be(self.stories))

        with it("should answer its own fidelity for a fidelity's slug"):
            expect(self.stories.answers_to("stories-story-map")).to(be(self.stories.fidelities["story_map"]))

        with it("should answer its own fidelity for the fidelity's bare name in kebab case"):
            expect(self.stories.fidelities.called("story-map")).to(be(self.stories.fidelities["story_map"]))

        with it("should answer its own fidelity for the fidelity's bare name in snake case"):
            expect(self.stories.fidelities.called("story_map")).to(be(self.stories.fidelities["story_map"]))

        with it("should answer nothing for a slug it does not go by"):
            expect(self.stories.answers_to("astrology")).to(be_none)

    with description("whose practice is made at a fidelity"):
        with it("should hold that fidelity as its current one"):
            expect(PRACTICE_CATALOGUE.create("stories", fidelity="scenarios").fidelities.current.name).to(equal("scenarios"))

        with it("should refuse a fidelity the practice does not have"):
            expect(lambda: PRACTICE_CATALOGUE.create("stories", fidelity="model")).to(raise_error(ValueError))

    with description("whose practices two readers make"):
        with before.all:
            self.first = PRACTICE_CATALOGUE.create_all()
            self.second = PRACTICE_CATALOGUE.create_all()

        with it("should give each reader practices of its own"):
            expect(self.first[0]).not_to(be(self.second[0]))

        with it("should leave one reader's fidelity format as it was when the other's changes"):
            self.first[0].fidelities["story_map"].format = "drawio"
            expect(self.second[0].fidelities["story_map"].format).not_to(equal("drawio"))

    with description("that makes a set of practices together"):
        with before.all:
            self.made = {practice.key: practice for practice in PRACTICE_CATALOGUE.create_all()}
            self.companion = self.made["stories"].fidelities["acceptance_tests"].clean_engineering

        with it("should give a fidelity's companion from the Clean Engineering practice of the same set"):
            expect(self.companion.practice_guidance).to(be(self.made["clean_engineering"]))

        with it("should hold the practice an extending practice builds on from the same set"):
            expect(self.made["ddd"].working_set.extended).to(be(self.made["clean_engineering"]))

    with description("whose set of practices is asked what a slug names"):
        with before.all:
            self.set = PRACTICE_CATALOGUE.create_all()
            self.stories = self.set[0]

        with it("should answer the fidelity whose slug it is"):
            expect(self.set.answering("stories-story-map")).to(be(self.stories.fidelities["story_map"]))

        with it("should answer the practice that slug names, for a fidelity's slug"):
            expect(self.set.practice_answering("stories-story-map")).to(be(self.stories))

        with it("should answer a fidelity by its bare name"):
            expect(self.set.named("story-map")).to(be(self.stories.fidelities["story_map"]))

        with it("should answer nothing for a slug no practice goes by"):
            expect(self.set.answering("astrology")).to(be_none)

        with it("should list every slug its practices and fidelities go by"):
            expect(self.set.slugs).to(contain("stories", "stories-story-map", "clean-engineering-code"))
