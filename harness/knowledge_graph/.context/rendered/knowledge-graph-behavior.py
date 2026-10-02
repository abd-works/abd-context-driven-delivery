from mamba import description, context, it
from expects import expect

with description("a story map"):
    with context("from a channel"):
        with context("to knowledge graph"):
            with it("behaves like a story map saved through a channel"):
                # BDD: SIGNATURE


from mamba import description, context, it
from expects import expect

with description("a class model"):
    with context("from a channel"):
        with context("to knowledge graph"):
            with it("behaves like a class model saved through a channel"):
                # BDD: SIGNATURE


from mamba import description, context, it
from expects import expect

with description("a domain driven design model"):
    with context("from a channel"):
        with context("to knowledge graph"):
            with it("behaves like a domain driven design model saved through a channel"):
                # BDD: SIGNATURE


from mamba import description, context, it
from expects import expect

with description("a knowledge graph"):
    with context("that has been saved"):
        with it("should write the knowledge graph models"):
            # BDD: SIGNATURE
    with context("that has been loaded from a path"):
        with it("should rebuild the nodes from that document"):
            # BDD: SIGNATURE
    with context("that has created a database"):
        with it("should write master"):
            # BDD: SIGNATURE
        with it("should copy master to the working copy"):
            # BDD: SIGNATURE
    with context("that has refreshed the master"):
        with it("should be the document that was just saved"):
            # BDD: SIGNATURE
    with context("that has reloaded the working copy"):
        with it("should be the document that was just saved"):
            # BDD: SIGNATURE
    with context("that has updated the working copy"):
        with context("with dirty paths"):
            with it("should be the document that was just saved"):
                # BDD: SIGNATURE
    with context("with selected practices"):
        with it("should fill available stages from those practices"):
            # BDD: SIGNATURE
        with it("should fill available node types from those practices and stages"):
            # BDD: SIGNATURE
        with context("with selected node types"):
            with it("should fill available relationships from those nodes"):
                # BDD: SIGNATURE
            with it("should fill available rules from those nodes"):
                # BDD: SIGNATURE
        with context("with a rule set"):
            with it("should offer base and project"):
                # BDD: SIGNATURE
    with context("with a chosen node"):
        with it("should hold that node as selected"):
            # BDD: SIGNATURE
    with context("with open branches"):
        with it("should hold those nodes as expanded"):
            # BDD: SIGNATURE


from mamba import description, context, it
from expects import expect

with description("an operation"):
    with context("that has source"):
        with it("should load each call at its line and order"):
            # BDD: SIGNATURE
        with it("should insert those calls into the text"):
            # BDD: SIGNATURE
        with it("should fold each inserted call"):
            # BDD: SIGNATURE
    with context("that calls another class's operation"):
        with it("should use the call glyph"):
            # BDD: SIGNATURE


from mamba import description, context, it
from expects import expect

with description("a property"):
    with context("that has source"):
        with it("behaves like an operation that has source"):
            # BDD: SIGNATURE
