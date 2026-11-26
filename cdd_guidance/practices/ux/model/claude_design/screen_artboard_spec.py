"""A screen's artboard on a story canvas, read for the UX graph rules: whether it is only a picture, the props it
declares and reads, and the scenarios it names."""

from expects import equal, expect
from mamba import description, it

from cdd_guidance.practices.ux.model.claude_design.screen_artboard import ScreenArtboard


def _artboard(template: str, logic: str = "class Component extends DCLogic { renderVals() { return {}; } }",
              props: str = '{"story":{"editor":null},"scenario":{"editor":null},"step":{"editor":null},"go":{"editor":null}}') -> ScreenArtboard:
    return ScreenArtboard(f"""<!doctype html>
<html><head><title>Cart</title></head><body>
<x-dc>
<helmet><style>body{{margin:0}}</style></helmet>
{template}
</x-dc>
<script type="text/x-dc" data-dc-script data-props='{props}'>
{logic}
</script>
</body></html>""")


with description("a screen's artboard") as self:
    with it("should be only a picture when it shows a screenshot and nothing else"):
        expect(_artboard('<div style="width: 100%"><img src="../shots/cart.png" alt="Cart"></div>').shows_only_a_picture).to(equal(True))

    with it("should be only a picture when a screenshot is its background"):
        expect(_artboard('<div style="background-image: url(../shots/cart.png); height: 844px"></div>').shows_only_a_picture).to(equal(True))

    with it("should be more than a picture when it draws the product's components"):
        expect(_artboard('<img src="../logo.png"><x-import component-from-global-scope="Shop.Cart" lines="{{lines}}"></x-import>').shows_only_a_picture).to(equal(False))

    with it("should be more than a picture when it shows text of its own"):
        expect(_artboard('<img src="../logo.png"><h1>Your cart</h1>').shows_only_a_picture).to(equal(False))

    with it("should declare the props its data-props names"):
        expect(_artboard("<p>Cart</p>", props='{"story":{"editor":null},"go":{"editor":null},"$preview":{"width":390}}').declared_props).to(equal({"story", "go", "$preview"}))

    with it("should read a prop its logic reads from this.props"):
        expect(_artboard("<p/>", "class Component extends DCLogic { renderVals() { return { s: this.props.scenario }; } }").reads_prop("scenario")).to(equal(True))

    with it("should read a prop its logic takes apart from the props"):
        expect(_artboard("<p/>", "class Component extends DCLogic { renderVals() { const { scenario, step } = this.props; return {}; } }").reads_prop("step")).to(equal(True))

    with it("should not read a prop its logic never reads"):
        expect(_artboard("<p/>", "class Component extends DCLogic { renderVals() { return { demoLines: 3 }; } }").reads_prop("scenario")).to(equal(False))

    with it("should name a scenario its logic keys a state by"):
        expect(_artboard("<p/>", 'class Component extends DCLogic { scenarioStates() { return {"Add one more line": {"given": {}}}; } }').names("Add one more line")).to(equal(True))

    with it("should name a scenario written with quotes the way JavaScript escapes them"):
        expect(_artboard("<p/>", 'class Component extends DCLogic { scenarioStates() { return {"Pick \\"Ace\\"": {}}; } }').names('Pick "Ace"')).to(equal(True))

    with it("should load its states from the fixtures when it builds them from a fixture"):
        expect(_artboard("<p/>", "class Component extends DCLogic { fromFixture(repositories, scenario) { return {}; } }").loads_fixtures).to(equal(True))
