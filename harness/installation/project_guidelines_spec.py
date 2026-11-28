"""The guidelines one project works with: the patterns CDD ships, and those the project keeps in its own guidelines
folder, each left out when its .context/config.json disables it, and never reaching another project."""

import json
import shutil
import tempfile
from pathlib import Path

from expects import be_empty, contain, equal, expect
from mamba import after, before, context, description, it

from harness.installation.project_guidelines import HeldProjectGuidelines


class ShippedLern:
    """A pattern CDD ships, as the installer finds it among the repository's toolsets."""

    pattern = "lern_domain_driven"


class ShippedMern:
    pattern = "mern_domain_driven"


class Echo:
    """A toolset that is no guideline."""


_OWN_PATTERN = '''
class Acme:
    pattern = "acme_domain_driven"


class Helper:
    """Defined beside the pattern, but no guideline of this folder."""
'''


def _project(guidelines: dict[str, str], folder: str | None = "guidelines", own: tuple[str, ...] = ("acme_domain_driven",)) -> Path:
    """A project whose config marks guidelines and names folder, which holds a pattern module for each of own."""
    root = Path(tempfile.mkdtemp(prefix="cdd-project-guidelines-"))
    config = {"guidelines": guidelines, **({"guidelines_folder": folder} if folder else {})}
    (root / ".context").mkdir()
    (root / ".context" / "config.json").write_text(json.dumps(config), encoding="utf-8")
    for name in own:
        pattern = root / (folder or "guidelines") / name
        pattern.mkdir(parents=True)
        (pattern / f"{name}.py").write_text(_OWN_PATTERN.replace("acme_domain_driven", name), encoding="utf-8")
    return root


with description("a project's guidelines"):
    with before.each:
        self.held = HeldProjectGuidelines()
        self.roots: list[Path] = []

    with after.each:
        for root in self.roots:
            shutil.rmtree(root, ignore_errors=True)

    with context("that keeps a pattern in its own guidelines folder and disables the LERN pattern CDD ships"):
        with before.each:
            self.root = _project({"lern_domain_driven": "disabled", "acme_domain_driven": "enabled"})
            self.roots.append(self.root)
            self.guidelines = self.held.of(self.root)

        with it("should find its own pattern by the folder's name"):
            expect([each.pattern for each in self.guidelines.own_classes]).to(equal(["acme_domain_driven"]))

        with it("should leave out a class beside the pattern that is no guideline of that folder"):
            expect([each.__name__ for each in self.guidelines.own_classes]).to(equal(["Acme"]))

        with it("should choose its own pattern and the shipped patterns it does not disable"):
            chosen = self.guidelines.chosen([ShippedLern, ShippedMern])
            expect([each.pattern for each in chosen]).to(equal(["mern_domain_driven", "acme_domain_driven"]))

        with it("should install every toolset that is no guideline, the shipped patterns it keeps, and its own"):
            installed = self.guidelines.toolsets([Echo, ShippedLern, ShippedMern])
            expect([each.__name__ for each in installed]).to(equal(["Echo", "ShippedMern", "Acme"]))

        with it("should import its own pattern under a package named for its folder"):
            expect(self.guidelines.own_classes[0].__module__).to(equal(f"{self.guidelines.folder.package}.acme_domain_driven.acme_domain_driven"))

        with context("with another project the same process serves"):
            with before.each:
                self.other = _project({}, folder=None, own=())
                self.roots.append(self.other)

            with it("should give the other project none of its own patterns"):
                expect(self.held.of(self.other).own_classes).to(be_empty)

            with it("should keep every shipped pattern for the other project"):
                chosen = self.held.of(self.other).chosen([ShippedLern, ShippedMern])
                expect([each.pattern for each in chosen]).to(equal(["lern_domain_driven", "mern_domain_driven"]))

        with context("with another project that keeps a pattern of the same name"):
            with before.each:
                self.other = _project({})
                self.roots.append(self.other)

            with it("should import each project's pattern as a class of its own"):
                expect(self.held.of(self.other).own_classes[0]).not_to(equal(self.guidelines.own_classes[0]))

    with context("that disables its own pattern"):
        with before.each:
            self.root = _project({"acme_domain_driven": "disabled"})
            self.roots.append(self.root)

        with it("should not choose it"):
            expect(self.held.of(self.root).chosen([ShippedLern])).not_to(contain(self.held.of(self.root).own_classes[0]))

        with it("should not install it"):
            expect([each.__name__ for each in self.held.of(self.root).toolsets([Echo, ShippedLern])]).to(equal(["Echo", "ShippedLern"]))

    with context("that keeps a pattern named as one CDD ships"):
        with before.each:
            self.root = _project({}, own=("lern_domain_driven",))
            self.roots.append(self.root)

        with it("should choose its own in place of the shipped one"):
            chosen = self.held.of(self.root).chosen([ShippedLern])
            expect([each.__name__ for each in chosen]).to(equal(["Acme"]))

        with it("should install its own in place of the shipped one"):
            expect([each.__name__ for each in self.held.of(self.root).toolsets([ShippedLern])]).to(equal(["Acme"]))

    with context("that names no guidelines folder"):
        with it("should keep no patterns of its own"):
            root = _project({}, folder=None, own=())
            self.roots.append(root)
            expect(self.held.of(root).own_classes).to(be_empty)
