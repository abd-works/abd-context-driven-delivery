"""BDD specs for a Draw.io modules diagram and a Draw.io class diagram."""
import re
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Tuple

from expects import be_false, be_true, contain, equal, expect, have_len
from mamba import before, context, description, it

from cdd_guidance.practices.clean_engineering.model.base_class_model import (
    CleanEngineeringModel,
    Module,
    OoadClass,
)
from cdd_guidance.practices.clean_engineering.model.field_types import Relationship
from cdd_guidance.practices.clean_engineering.model.operation import Operation
from cdd_guidance.practices.clean_engineering.model.property import Property
from cdd_guidance.practices.clean_engineering.clean_engineering import CleanEngineering
from cdd_guidance.practices.clean_engineering.model.drawio.drawio_class_model import (
    DrawIOCleanEngineeringModel,
)
from cdd_guidance.practices.clean_engineering.model.markdown.markdown_class_model import (
    MarkdownCleanEngineeringModel,
)

_MODULES_MD = '# checks\n\nFoundation check resolution.\n\n- **Purpose:** Resolve d20 + trait against difficulty.\n- **Seam (terms):** Trait, Check, CheckResult\n- **Dependencies (one-way):** *(none)*\n\n# character\n\nOwns the hero sheet and ISource.\n\n- **Purpose:** Character sheet ownership and ISource.\n- **Seam (terms):** Character, Ability, ISource\n- **Dependencies (one-way):** checks\n'
_NESTED_POWERS_MD = '# powers\n\nOwns Effect shared base.\n\n- **Purpose:** Shared Effect seam on the parent.\n- **Seam (terms):** Effect\n- **Dependencies (one-way):** character, checks\n\n# powers/attack\n\nAttack-typed effects.\n\n- **Purpose:** Specialize Effect for attack-type powers.\n- **Seam (terms):** AttackEffect\n- **Dependencies (one-way):** powers, checks\n\n# checks\n\nFoundation.\n\n- **Purpose:** Resolve checks.\n- **Seam (terms):** Trait, Check\n- **Dependencies (one-way):** *(none)*\n\n# character\n\nSheet.\n\n- **Purpose:** Sheet ownership.\n- **Seam (terms):** Character, ISource\n- **Dependencies (one-way):** checks\n'
_NESTED_MODULE_CONTEXT_MD = '# powers/effect\n\nShared base for all power effects.\n\n## Modules fidelity\n\n### Module `powers/effect`\n\n- **Purpose:** Own the shared Effect seam.\n- **Seam (terms):** Effect\n- **Dependencies (one-way):** `character`, `checks`\n- **Build order:** see module-build-order.md\n'


_TEMPLATES = Path(__file__).resolve().parents[2] / 'templates'

# A class cell is named for the module that owns it, so two modules can both hold a Cart.
_CART = 'shop--cart'
_ORDER = 'shop--order'
_INVOICE = 'shop--invoice'


def _shop_model(extra_properties=None, extra_class=None, extra_relationship=None) -> CleanEngineeringModel:
    model = CleanEngineeringModel(name='Shop', sequential_order=1)
    module = Module(name='Shop', sequential_order=1)
    cart_props = [Property(name='owner', type_hint='str')]
    if extra_properties:
        cart_props.extend(extra_properties)
    cart_rels = [Relationship(target='Order', kind='association')]
    if extra_relationship:
        cart_rels.append(extra_relationship)
    class_name = 'Cart'
    for rel in cart_rels:
        if (rel.kind or '').lower() == 'inheritance':
            class_name = f'Cart extends {rel.target}'
            continue
        cart_props.append(Property(name=rel.target[:1].lower() + rel.target[1:], type_hint=rel.target))
    module.classes.append(
        OoadClass(
            name=class_name,
            sequential_order=1,
            properties=cart_props,
            operations=[Operation(name='place_order', return_type='Order')],
            relationships=cart_rels,
        )
    )
    module.classes.append(OoadClass(name='Order', sequential_order=2, properties=[Property(name='total', type_hint='int')]))
    if extra_class is not None:
        module.classes.append(extra_class)
    model.modules.append(module)
    return model


def _cell_xy(xml: str, cell_id: str) -> Tuple[float, float]:
    root = ET.fromstring(xml)
    for cell in root.iter('mxCell'):
        if cell.get('id') == cell_id:
            geo = cell.find('mxGeometry')
            if geo is None:
                break
            return (float(geo.get('x', '0')), float(geo.get('y', '0')))
    raise AssertionError(f'no vertex {cell_id!r}')


def _set_cell_xy(xml, cell_id, x, y) -> str:
    root = ET.fromstring(xml)
    for cell in root.iter('mxCell'):
        if cell.get('id') == cell_id:
            geo = cell.find('mxGeometry')
            if geo is None:
                continue
            geo.set('x', str(int(x)))
            geo.set('y', str(int(y)))
    return ET.tostring(root, encoding='unicode')


def _edge_cell(xml, src, tgt) -> ET.Element:
    root = ET.fromstring(xml)
    for cell in root.iter('mxCell'):
        if cell.get('edge') == '1' and cell.get('source') == src and cell.get('target') == tgt:
            return cell
    raise AssertionError(f'no edge {src} -> {tgt}')


def _set_edge_waypoint(xml, src, tgt, x, y) -> str:
    root = ET.fromstring(xml)
    for cell in root.iter('mxCell'):
        if cell.get('edge') != '1':
            continue
        if cell.get('source') != src or cell.get('target') != tgt:
            continue
        geo = cell.find('mxGeometry')
        if geo is None:
            continue
        arr = geo.find('Array')
        if arr is None:
            arr = ET.SubElement(geo, 'Array')
            arr.set('as', 'points')
        pt = ET.SubElement(arr, 'mxPoint')
        pt.set('x', str(int(x)))
        pt.set('y', str(int(y)))
    return ET.tostring(root, encoding='unicode')


def _has_vertex(xml: str, cell_id: str) -> bool:
    root = ET.fromstring(xml)
    return any((cell.get('vertex') == '1' and cell.get('id') == cell_id for cell in root.iter('mxCell')))


def _render_kept(model, previous):
    channel = DrawIOCleanEngineeringModel()
    channel.previous = previous
    channel.keep_positioning = True
    return channel.render(model)


def _create_kept(content, path):
    toolset = CleanEngineering().drawio
    toolset.channel.keep_positioning = True
    return toolset.create_diagram(content, path)


with description('a Draw.io modules diagram'):
    with context('that was rendered from canonical modules'):
        with before.each:
            model = CleanEngineeringModel(name='HeroesHandbook', sequential_order=1)
            checks = Module(name='checks', sequential_order=1, description='Resolve checks.', seam_terms=['Trait', 'Check'])
            character = Module(
                name='character',
                sequential_order=2,
                description='Sheet ownership.',
                seam_terms=['Character', 'ISource'],
                dependencies=['checks'],
            )
            model.modules.extend([checks, character])
            self.xml = DrawIOCleanEngineeringModel().render(model)

        with it('should use the Modules Context diagram id'):
            expect(self.xml).to(contain('id="modules-context"'))

        with it('should show the checks module name'):
            expect(self.xml).to(contain('checks'))

        with it('should show Trait as a seam bullet'):
            expect(self.xml).to(contain('\u2022 Trait'))

        with it('should show the character module name'):
            expect(self.xml).to(contain('character'))

        with it('should show ISource as a seam bullet'):
            expect(self.xml).to(contain('\u2022 ISource'))

        with it('should omit stack and tech callouts'):
            expect('stack / tech' in self.xml).to(be_false)

        with it('should draw a dependency from character to checks'):
            expect(self.xml).to(contain('source="character"'))

        with it('should target the checks module on that dependency'):
            expect(self.xml).to(contain('target="checks"'))

    with context('that round-trips markdown through Draw.io back to the model'):
        with before.each:
            parsed = MarkdownCleanEngineeringModel(name='', sequential_order=1).parse(_MODULES_MD)
            drawio = DrawIOCleanEngineeringModel().render(parsed)
            self.back = DrawIOCleanEngineeringModel().parse(drawio)

        with it('should recover both modules'):
            expect(self.back.modules).to(have_len(2))

        with it('should recover Trait on checks'):
            checks = next((m for m in self.back.modules if m.name == 'checks'))
            expect(checks.seam_terms).to(contain('Trait'))

        with it('should recover Check on checks'):
            checks = next((m for m in self.back.modules if m.name == 'checks'))
            expect(checks.seam_terms).to(contain('Check'))

        with it('should recover CheckResult on checks'):
            checks = next((m for m in self.back.modules if m.name == 'checks'))
            expect(checks.seam_terms).to(contain('CheckResult'))

        with it('should recover character depending on checks'):
            character = next((m for m in self.back.modules if m.name == 'character'))
            expect(character.dependencies).to(contain('checks'))

        with it('should leave checks with no dependencies'):
            checks = next((m for m in self.back.modules if m.name == 'checks'))
            expect(checks.dependencies).to(equal([]))

    with context('that was parsed from a nested Modules fidelity markdown section'):
        with before.each:
            self.model = MarkdownCleanEngineeringModel(name='', sequential_order=1).parse(_NESTED_MODULE_CONTEXT_MD)

        with it('should hold one module'):
            expect(self.model.modules).to(have_len(1))

        with it('should keep the module path name'):
            expect(self.model.modules[0].name).to(equal('powers/effect'))

        with it('should parse seam terms from the Modules fidelity block'):
            expect(self.model.modules[0].seam_terms).to(equal(['Effect']))

        with it('should parse one-way dependencies'):
            expect(self.model.modules[0].dependencies).to(equal(['character', 'checks']))

    with context('that was parsed from the AI template modules.drawio'):
        with before.each:
            path = _TEMPLATES / 'modules.drawio'
            self.model = DrawIOCleanEngineeringModel().parse(path.read_text(encoding='utf-8'))

        with it('should parse five placeholder modules'):
            expect(self.model.modules).to(have_len(5))

        with it('should keep placeholder module path names'):
            expect(self.model.modules[0].name).to(contain('module/path'))

        with it('should wire four dependency edges toward the hub module'):
            with_deps = [m for m in self.model.modules if m.dependencies]
            expect(with_deps).to(have_len(4))

    with context('that nests path children as containment'):
        with before.each:
            parsed = MarkdownCleanEngineeringModel(name='', sequential_order=1).parse(_NESTED_POWERS_MD)
            parsed.name = 'Heroes Handbook'
            self.xml = DrawIOCleanEngineeringModel().render(parsed)

        with it('should render the powers parent cell'):
            expect(self.xml).to(contain('id="powers"'))

        with it('should put Effect on the powers parent cell'):
            expect(self.xml).to(contain('\u2022 Effect'))

        with it('should nest powers/attack inside powers'):
            expect(self.xml).to(contain('id="powers-attack"'))

        with it('should parent the nested cell on powers'):
            expect(self.xml).to(contain('parent="powers"'))

        with it('should style nested children with the child fill'):
            expect(self.xml).to(contain('fillColor=#dae8fc'))

        with it('should not invent a powers/effect submodule name in the xml'):
            expect('powers/effect' in self.xml).to(be_false)

        with it('should not invent a powers-effect cell id'):
            expect('id="powers-effect"' in self.xml).to(be_false)

        with it('should omit a child-to-parent dependency edge'):
            expect(self.xml).not_to(contain('source="powers-attack" target="powers"'))


with description('a Draw.io class diagram'):
    with context('that was rendered from a typed class model'):
        with before.each:
            model = CleanEngineeringModel(name='Shop', sequential_order=1)
            module = Module(name='Shop', sequential_order=1)
            module.classes.append(
                OoadClass(
                    name='Cart',
                    sequential_order=1,
                    properties=[Property(name='owner', type_hint='str')],
                    operations=[Operation(name='place_order', return_type='Order')],
                )
            )
            model.modules.append(module)
            self.xml = DrawIOCleanEngineeringModel().render(model)

        with it('should use the class-diagram diagram id'):
            expect(self.xml).to(contain('id="CleanEngineering-model"'))

        with it('should not use the Modules Context id'):
            expect('modules-context' in self.xml).to(be_false)

        with it('should render the owner property'):
            expect(self.xml).to(contain('owner'))

        with it('should render the place_order operation'):
            expect(self.xml).to(contain('place_order'))

    with context('that keeps positioning'):
        with context('with existing class content that has changed'):
            with before.each:
                first = DrawIOCleanEngineeringModel().render(_shop_model())
                moved = _set_cell_xy(first, _CART, 500, 300)
                self.xml = _render_kept(
                    _shop_model(extra_properties=[Property(name='items', type_hint='list')]),
                    moved,
                )

            with it('should keep the existing class at its previous position'):
                expect(_cell_xy(self.xml, _CART)).to(equal((500.0, 300.0)))

            with it('should update the class contents in place'):
                expect(self.xml).to(contain('items'))

            with it('should still show the unchanged owner property'):
                expect(self.xml).to(contain('owner'))

        with context('with an existing relationship already present'):
            with before.each:
                first = DrawIOCleanEngineeringModel().render(_shop_model())
                marked = _set_edge_waypoint(first, _CART, _ORDER, 111, 222)
                self.xml = _render_kept(_shop_model(), marked)

            with it('should leave the existing relationship routing in place'):
                edge = _edge_cell(self.xml, _CART, _ORDER)
                points = [(pt.get('x'), pt.get('y')) for pt in edge.iter('mxPoint')]
                expect(points).to(contain(('111', '222')))

        with context('with a new class added to the model'):
            with before.each:
                first = DrawIOCleanEngineeringModel().render(_shop_model())
                moved = _set_cell_xy(first, _CART, 500, 300)
                invoice = OoadClass(name='Invoice', sequential_order=3, properties=[Property(name='number', type_hint='str')])
                self.xml = _render_kept(_shop_model(extra_class=invoice), moved)

            with it('should keep existing class positions'):
                expect(_cell_xy(self.xml, _CART)).to(equal((500.0, 300.0)))

            with it('should add the new class'):
                expect(_has_vertex(self.xml, _INVOICE)).to(be_true)

            with it('should show the new class members'):
                expect(self.xml).to(contain('number'))

            with it('should not place the new class on top of the kept class'):
                expect(_cell_xy(self.xml, _INVOICE) == (500.0, 300.0)).to(be_false)

        with context('with a new relationship added to the model'):
            with before.each:
                first = DrawIOCleanEngineeringModel().render(_shop_model())
                marked = _set_edge_waypoint(first, _CART, _ORDER, 111, 222)
                invoice = OoadClass(name='Invoice', sequential_order=3, properties=[Property(name='number', type_hint='str')])
                self.xml = _render_kept(
                    _shop_model(extra_class=invoice, extra_relationship=Relationship(target='Invoice', kind='association')),
                    marked,
                )

            with it('should leave the existing relationship in place'):
                edge = _edge_cell(self.xml, _CART, _ORDER)
                points = [(pt.get('x'), pt.get('y')) for pt in edge.iter('mxPoint')]
                expect(points).to(contain(('111', '222')))

            with it('should add the new relationship'):
                expect(_edge_cell(self.xml, _CART, _INVOICE).get('target')).to(equal(_INVOICE))

        with context('with no previous diagram'):
            with before.each:
                channel = DrawIOCleanEngineeringModel()
                channel.keep_positioning = True
                self.xml = channel.render(_shop_model())

            with it('should still render a class diagram'):
                expect(self.xml).to(contain('id="CleanEngineering-model"'))

            with it('should still place the cart class'):
                expect(_has_vertex(self.xml, _CART)).to(be_true)

        with context('with a model large enough for one page per module'):
            with before.each:
                from cdd_guidance.practices.clean_engineering.model.drawio.drawio_class_model import CLASSES_ON_ONE_PAGE

                def two_modules():
                    model = CleanEngineeringModel(name='Shop', sequential_order=1)
                    for number, name in enumerate(('Orders', 'Billing'), start=1):
                        module = Module(name=name, sequential_order=number)
                        module.classes.extend(
                            OoadClass(name=f'{name}Part{index}', sequential_order=index, properties=[Property(name='size', type_hint='int')])
                            for index in range(1, CLASSES_ON_ONE_PAGE // 2 + 2)
                        )
                        model.modules.append(module)
                    return model

                first = DrawIOCleanEngineeringModel().render(two_modules())
                self.card = next(cell.get('id') for cell in ET.fromstring(first).iter('mxCell') if cell.get('vertex') == '1' and 'OrdersPart3' in (cell.get('value') or ''))
                self.xml = _render_kept(two_modules(), _set_cell_xy(first, self.card, 1234, 567))

            with it('should keep a hand-moved card where it was on its module page'):
                expect(_cell_xy(self.xml, self.card)).to(equal((1234.0, 567.0)))

    with context('that does not keep positioning'):
        with context('with a new class added after a hand-moved layout'):
            with it('should not keep a hand-moved position after full relayout'):
                first = DrawIOCleanEngineeringModel().render(_shop_model())
                moved = _set_cell_xy(first, _CART, 500, 300)
                invoice = OoadClass(name='Invoice', sequential_order=3, properties=[Property(name='number', type_hint='str')])
                channel = DrawIOCleanEngineeringModel()
                channel.previous = moved
                channel.keep_positioning = False
                xml = channel.render(_shop_model(extra_class=invoice))
                expect(_cell_xy(xml, _CART) == (500.0, 300.0)).to(be_false)


with description('Drawio creating a diagram'):
    with context('that keeps positioning'):
        with context('with an existing diagram at the output path'):
            with before.each:
                self.tmp = tempfile.TemporaryDirectory()
                self.path = str(Path(self.tmp.name) / 'shop.drawio')
                first = DrawIOCleanEngineeringModel().render(_shop_model())
                Path(self.path).write_text(_set_cell_xy(first, _CART, 500, 300), encoding='utf-8')
                md = MarkdownCleanEngineeringModel(name='', sequential_order=1).render(
                    _shop_model(extra_properties=[Property(name='items', type_hint='list')])
                )
                _create_kept(md, self.path)
                self.xml = Path(self.path).read_text(encoding='utf-8')

            with it('should keep class positions from the existing diagram'):
                expect(_cell_xy(self.xml, _CART)).to(equal((500.0, 300.0)))

            with it('should refresh class contents from the new model'):
                expect(self.xml).to(contain('items'))

        with context('with no existing diagram at the output path'):
            with it('should create a new diagram file'):
                with tempfile.TemporaryDirectory() as tmp:
                    path = str(Path(tmp) / 'fresh.drawio')
                    md = MarkdownCleanEngineeringModel(name='', sequential_order=1).render(_shop_model())
                    _create_kept(md, path)
                    expect(Path(path).exists()).to(be_true)

            with it('should place the cart class in that new diagram'):
                with tempfile.TemporaryDirectory() as tmp:
                    path = str(Path(tmp) / 'fresh.drawio')
                    md = MarkdownCleanEngineeringModel(name='', sequential_order=1).render(_shop_model())
                    _create_kept(md, path)
                    xml = Path(path).read_text(encoding='utf-8')
                    expect(_has_vertex(xml, _CART)).to(be_true)


_TWO_MODULES = """# shop/cart

## Item

------
+ title: str
----

## Basket : Item

------
+ << composition >> lines: list[Line]
----

## Line

------
+ quantity: int
----

# shop/checkout

## Payment

------
+ << association >> basket: Basket
----
"""


with description('a class model that spans two modules'):
    with before.each:
        model = MarkdownCleanEngineeringModel(name='', sequential_order=1).parse(_TWO_MODULES)
        self.rendered = DrawIOCleanEngineeringModel().render(model)
        self.cells = {cell.get('id'): cell for cell in ET.fromstring(self.rendered).iter('mxCell')}

    with it('should draw every class on one page'):
        expect(ET.fromstring(self.rendered).findall('diagram')).to(have_len(1))

    with it('should colour each module differently'):
        fills = {re.search(r'fillColor=(#\w+)', cell.get('style')).group(1) for cell in self.cells.values() if cell.get('vertex') == '1'}
        expect(fills).to(have_len(2))

    with it('should draw an arrow for a marked list of a class'):
        arrow = next(cell for cell in self.cells.values() if cell.get('target') == 'shop-cart--line')
        expect(arrow.get('style')).to(contain('startArrow=diamondThin'))

    with it('should name the arrow after its property'):
        arrow = next(cell for cell in self.cells.values() if cell.get('target') == 'shop-cart--line')
        expect(arrow.get('value')).to(equal('lines'))

    with it('should draw inheritance from the class heading'):
        arrow = next(cell for cell in self.cells.values() if cell.get('source') == 'shop-cart--basket' and cell.get('target') == 'shop-cart--item')
        expect(arrow.get('style')).to(contain('endArrow=block'))

    with it('should keep each class in its module when read back'):
        parsed = DrawIOCleanEngineeringModel(name='', sequential_order=1).parse(self.rendered)
        expect([module.name for module in parsed.modules]).to(equal(['shop/cart', 'shop/checkout']))
