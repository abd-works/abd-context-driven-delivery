"""The IDE an install is for, named by the person: matched whatever its case, refused when it is none CDD installs into."""
from expects import contain, equal, expect, raise_error
from mamba import context, description, it

from harness.installation.ide_layout import IdeLayout, UnknownIde


with description("the IDE an install names"):
    with context("that is one CDD installs into, written in another case"):
        with it("should be that IDE, under the name CDD writes it with"):
            expect(IdeLayout("claude").ide).to(equal("Claude"))

        with it("should install into that IDE's folder"):
            expect(IdeLayout("vs code").folder_name).to(equal(".github"))

    with context("that is none CDD installs into"):
        with it("should be refused"):
            expect(lambda: IdeLayout("Emacs")).to(raise_error(UnknownIde))

        with it("should be refused with the name given and the names it can be"):
            try:
                IdeLayout("Emacs")
            except UnknownIde as refusal:
                expect(str(refusal)).to(contain("Emacs", "Cursor", "VS Code", "Kilo", "Claude"))

        with it("should keep the name given on the refusal"):
            try:
                IdeLayout("Emacs")
            except UnknownIde as refusal:
                expect(refusal.ide).to(equal("Emacs"))
