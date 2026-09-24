"""BDD specs for the DrawIO channel (modules view, class view, keep_positioning)."""
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Optional, Tuple
from expects import be_false, be_true, contain, equal, expect, have_len
from mamba import before, context, description, it
_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ('tools', 'practices', 'actions'):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)
from practices.clean_engineering.model.base_class_model import CleanEngineeringModel, Module, OoadClass, Operation, Property, Relationship
from practices.clean_engineering.model.drawio.drawio import Drawio
from practices.clean_engineering.model.drawio.drawio_class_model import DrawIOCleanEngineeringModel

class _Channel(DrawIOCleanEngineeringModel):

    def _shop_model(self, extra_properties, _rest) -> CleanEngineeringModel:
        extra_class, extra_relationship = _rest
        model = CleanEngineeringModel(name='Shop', sequential_order=1)
        module = Module(name='Shop', sequential_order=1)
        cart_props = [Property(name='owner', type_hint='str')]
        if extra_properties:
            cart_props.extend(extra_properties)
        cart_rels = [Relationship(target='Order', kind='association')]
        if extra_relationship:
            cart_rels.append(extra_relationship)
        module.classes.append(OoadClass(name='Cart', sequential_order=1, properties=cart_props, operations=[Operation(name='place_order', return_type='Order')], relationships=cart_rels))
        module.classes.append(OoadClass(name='Order', sequential_order=2, properties=[Property(name='total', type_hint='int')]))
        if extra_class is not None:
            module.classes.append(extra_class)
        model.modules.append(module)
        return model

    def _cell_xy(self, xml: str, cell_id: str) -> Tuple[float, float]:
        root = ET.fromstring(xml)
        for cell in root.iter('mxCell'):
            if cell.get('id') == cell_id:
                geo = cell.find('mxGeometry')
                if geo is None:
                    break
                return (float(geo.get('x', '0')), float(geo.get('y', '0')))
        raise AssertionError(f'no vertex {cell_id!r}')

    def _set_cell_xy(self, xml, _rest) -> str:
        cell_id, x, y = _rest
        root = ET.fromstring(xml)
        for cell in root.iter('mxCell'):
            if cell.get('id') == cell_id:
                geo = cell.find('mxGeometry')
                if geo is None:
                    continue
                geo.set('x', str(int(x)))
                geo.set('y', str(int(y)))
        return ET.tostring(root, encoding='unicode')

    def _edge_cell(self, xml, _rest) -> ET.Element:
        src, tgt = _rest
        root = ET.fromstring(xml)
        for cell in root.iter('mxCell'):
            if cell.get('edge') == '1' and cell.get('source') == src and (cell.get('target') == tgt):
                return cell
        raise AssertionError(f'no edge {src} -> {tgt}')

    def _set_edge_waypoint(self, xml, _rest) -> str:
        src, tgt, x, y = _rest
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

    def _has_vertex(self, xml: str, cell_id: str) -> bool:
        root = ET.fromstring(xml)
        return any((cell.get('vertex') == '1' and cell.get('id') == cell_id for cell in root.iter('mxCell')))

    def _edge_count(self, xml: str) -> int:
        root = ET.fromstring(xml)
        return sum((1 for cell in root.iter('mxCell') if cell.get('edge') == '1'))

    def render_kept(self, model, previous):
        self.previous = previous
        self.keep_positioning = True
        return self.render(model)

    def create_kept(self, content, path):
        kit = Drawio()
        kit.source_format = 'markdown'
        kit.keep_positioning = True
        return kit.create_diagram(content, path)
from practices.clean_engineering.model.markdown.markdown_class_model import MarkdownCleanEngineeringModel
_MODULES_MD = '# checks\n\nFoundation check resolution.\n\n- **Purpose:** Resolve d20 + trait against difficulty.\n- **Seam (terms):** Trait, Check, CheckResult\n- **Dependencies (one-way):** *(none)*\n\n# character\n\nOwns the hero sheet and ISource.\n\n- **Purpose:** Character sheet ownership and ISource.\n- **Seam (terms):** Character, Ability, ISource\n- **Dependencies (one-way):** checks\n'
_NESTED_POWERS_MD = '# powers\n\nOwns Effect shared base.\n\n- **Purpose:** Shared Effect seam on the parent.\n- **Seam (terms):** Effect\n- **Dependencies (one-way):** character, checks\n\n# powers/attack\n\nAttack-typed effects.\n\n- **Purpose:** Specialize Effect for attack-type powers.\n- **Seam (terms):** AttackEffect\n- **Dependencies (one-way):** powers, checks\n\n# checks\n\nFoundation.\n\n- **Purpose:** Resolve checks.\n- **Seam (terms):** Trait, Check\n- **Dependencies (one-way):** *(none)*\n\n# character\n\nSheet.\n\n- **Purpose:** Sheet ownership.\n- **Seam (terms):** Character, ISource\n- **Dependencies (one-way):** checks\n'
_NESTED_MODULE_CONTEXT_MD = '# powers/effect\n\nShared base for all power effects.\n\n## Modules fidelity\n\n### Module `powers/effect`\n\n- **Purpose:** Own the shared Effect seam.\n- **Seam (terms):** Effect\n- **Dependencies (one-way):** `character`, `checks`\n- **Build order:** see module-build-order.md\n'
with description('DrawIO modules fidelity'):
    with context('render modules view from canonical modules'):
        with before.each:
            model = CleanEngineeringModel(name='HeroesHandbook', sequential_order=1)
            checks = Module(name='checks', sequential_order=1, description='Resolve checks.', seam_terms=['Trait', 'Check'])
            character = Module(name='character', sequential_order=2, description='Sheet ownership.', seam_terms=['Character', 'ISource'], dependencies=['checks'])
            model.modules.extend([checks, character])
            self.xml = _Channel().render(model)
        with it('should use Modules Context diagram id'):
            expect(self.xml).to(contain('id="modules-context"'))
        with it('should render module names and seam bullets'):
            expect(self.xml).to(contain('checks'))
            expect(self.xml).to(contain('\u2022 Trait'))
            expect(self.xml).to(contain('character'))
            expect(self.xml).to(contain('\u2022 ISource'))
        with it('should not include stack/tech callouts'):
            expect('stack / tech' in self.xml).to(be_false)
        with it('should draw a dependency edge character -> checks'):
            expect(self.xml).to(contain('source="character"'))
            expect(self.xml).to(contain('target="checks"'))
    with context('round-trip markdown -> drawio -> model'):
        with before.each:
            parsed = MarkdownCleanEngineeringModel(name='', sequential_order=1).parse(_MODULES_MD)
            drawio = _Channel().render(parsed)
            self.back = _Channel().parse(drawio)
        with it('should recover both modules'):
            expect(self.back.modules).to(have_len(2))
        with it('should recover seam terms on checks'):
            checks = next((m for m in self.back.modules if m.name == 'checks'))
            expect(checks.seam_terms).to(contain('Trait'))
            expect(checks.seam_terms).to(contain('Check'))
            expect(checks.seam_terms).to(contain('CheckResult'))
        with it('should recover character -> checks dependency'):
            character = next((m for m in self.back.modules if m.name == 'character'))
            expect(character.dependencies).to(contain('checks'))
        with it('should leave checks with no dependencies'):
            checks = next((m for m in self.back.modules if m.name == 'checks'))
            expect(checks.dependencies).to(equal([]))
    with context('parse nested Modules fidelity markdown section'):
        with before.each:
            self.model = MarkdownCleanEngineeringModel(name='', sequential_order=1).parse(_NESTED_MODULE_CONTEXT_MD)
        with it('should parse the module path name'):
            expect(self.model.modules).to(have_len(1))
            expect(self.model.modules[0].name).to(equal('powers/effect'))
        with it('should parse seam terms from the Modules fidelity block'):
            expect(self.model.modules[0].seam_terms).to(equal(['Effect']))
        with it('should parse one-way dependencies'):
            expect(self.model.modules[0].dependencies).to(equal(['character', 'checks']))
    with context('parse AI template modules.drawio'):
        with before.each:
            path = _REPO_ROOT / 'practices' / 'clean_engineering' / 'templates' / 'modules.drawio'
            self.model = _Channel().parse(path.read_text(encoding='utf-8'))
        with it('should parse placeholder modules as modules view'):
            expect(self.model.modules).to(have_len(5))
        with it('should keep placeholder module path names'):
            expect(self.model.modules[0].name).to(contain('module/path'))
        with it('should wire four dependency edges toward the hub module'):
            with_deps = [m for m in self.model.modules if m.dependencies]
            expect(with_deps).to(have_len(4))
    with context('path nesting renders as containment'):
        with before.each:
            parsed = MarkdownCleanEngineeringModel(name='', sequential_order=1).parse(_NESTED_POWERS_MD)
            parsed.name = 'Heroes Handbook'
            self.xml = _Channel().render(parsed)
        with it('should put Effect on the powers parent cell'):
            expect(self.xml).to(contain('id="powers"'))
            expect(self.xml).to(contain('\u2022 Effect'))
        with it('should nest powers/attack inside powers'):
            expect(self.xml).to(contain('id="powers-attack"'))
            expect(self.xml).to(contain('parent="powers"'))
        with it('should style nested children with the child fill'):
            expect(self.xml).to(contain('fillColor=#dae8fc'))
        with it('should not invent a powers/effect submodule cell'):
            expect('powers/effect' in self.xml).to(be_false)
            expect('id="powers-effect"' in self.xml).to(be_false)
        with it('should omit child->parent dependency edge'):
            expect(self.xml).not_to(contain('source="powers-attack" target="powers"'))
    with context('typed class model still renders UML class diagram'):
        with before.each:
            model = CleanEngineeringModel(name='Shop', sequential_order=1)
            module = Module(name='Shop', sequential_order=1)
            module.classes.append(OoadClass(name='Cart', sequential_order=1, properties=[Property(name='owner', type_hint='str')], operations=[Operation(name='place_order', return_type='Order')]))
            model.modules.append(module)
            self.xml = _Channel().render(model)
        with it('should use the class-diagram diagram id'):
            expect(self.xml).to(contain('id="CleanEngineering-model"'))
        with it('should not use Modules Context id'):
            expect('modules-context' in self.xml).to(be_false)
        with it('should render class members'):
            expect(self.xml).to(contain('owner'))
            expect(self.xml).to(contain('place_order'))
with description('DrawIOCleanEngineeringModel.render keep_positioning'):
    with context('existing class content changes'):
        with before.each:
            channel = _Channel()
            first = channel.render(channel._shop_model(None, (None, None)))
            moved = channel._set_cell_xy(first, ('cart', 500, 300))
            self.xml = channel.render_kept(
                channel._shop_model([Property(name='items', type_hint='list')], (None, None)),
                moved,
            )
            self.channel = channel
        with it('should keep the existing class at its previous position'):
            expect(self.channel._cell_xy(self.xml, 'cart')).to(equal((500.0, 300.0)))
        with it('should update the class contents in place'):
            expect(self.xml).to(contain('items'))
            expect(self.xml).to(contain('owner'))
    with context('existing relationship already present'):
        with before.each:
            channel = _Channel()
            first = channel.render(channel._shop_model(None, (None, None)))
            marked = channel._set_edge_waypoint(first, ('cart', 'order', 111, 222))
            self.xml = channel.render_kept(channel._shop_model(None, (None, None)), marked)
            self.channel = channel
        with it('should leave the existing relationship routing in place'):
            edge = self.channel._edge_cell(self.xml, ('cart', 'order'))
            points = [(pt.get('x'), pt.get('y')) for pt in edge.iter('mxPoint')]
            expect(points).to(contain(('111', '222')))
    with context('new class added to the model'):
        with before.each:
            channel = _Channel()
            first = channel.render(channel._shop_model(None, (None, None)))
            moved = channel._set_cell_xy(first, ('cart', 500, 300))
            invoice = OoadClass(name='Invoice', sequential_order=3, properties=[Property(name='number', type_hint='str')])
            self.xml = channel.render_kept(channel._shop_model(None, (invoice, None)), moved)
            self.channel = channel
        with it('should keep existing class positions'):
            expect(self.channel._cell_xy(self.xml, 'cart')).to(equal((500.0, 300.0)))
        with it('should add the new class using the layout algorithm'):
            expect(self.channel._has_vertex(self.xml, 'invoice')).to(be_true)
            expect(self.xml).to(contain('number'))
        with it('should not place the new class on top of the kept class'):
            ix, iy = self.channel._cell_xy(self.xml, 'invoice')
            expect((ix, iy) == (500.0, 300.0)).to(be_false)
    with context('new relationship added to the model'):
        with before.each:
            channel = _Channel()
            first = channel.render(channel._shop_model(None, (None, None)))
            marked = channel._set_edge_waypoint(first, ('cart', 'order', 111, 222))
            invoice = OoadClass(name='Invoice', sequential_order=3, properties=[Property(name='number', type_hint='str')])
            self.xml = channel.render_kept(
                channel._shop_model(None, (invoice, Relationship(target='Invoice', kind='association'))),
                marked,
            )
            self.channel = channel
        with it('should leave the existing relationship in place'):
            edge = self.channel._edge_cell(self.xml, ('cart', 'order'))
            points = [(pt.get('x'), pt.get('y')) for pt in edge.iter('mxPoint')]
            expect(points).to(contain(('111', '222')))
        with it('should add the new relationship'):
            self.channel._edge_cell(self.xml, ('cart', 'invoice'))
            expect(self.channel._edge_count(self.xml) >= 2).to(be_true)
    with context('keep_positioning with no previous diagram'):
        with it('should still render a class diagram'):
            channel = _Channel()
            channel.keep_positioning = True
            xml = channel.render(channel._shop_model(None, (None, None)))
            expect(xml).to(contain('id="CleanEngineering-model"'))
            expect(channel._has_vertex(xml, 'cart')).to(be_true)
    with context('keep_positioning is off and a new class is added'):
        with it('should not keep a hand-moved position after full relayout'):
            channel = _Channel()
            first = channel.render(channel._shop_model(None, (None, None)))
            moved = channel._set_cell_xy(first, ('cart', 500, 300))
            invoice = OoadClass(name='Invoice', sequential_order=3, properties=[Property(name='number', type_hint='str')])
            channel.previous = moved
            channel.keep_positioning = False
            xml = channel.render(channel._shop_model(None, (invoice, None)))
            expect(channel._cell_xy(xml, 'cart') == (500.0, 300.0)).to(be_false)
with description('Drawio.create_diagram keep_positioning'):
    with context('existing diagram at the output path'):
        with before.each:
            self.tmp = tempfile.TemporaryDirectory()
            self.path = str(Path(self.tmp.name) / 'shop.drawio')
            channel = _Channel()
            first = channel.render(channel._shop_model(None, (None, None)))
            Path(self.path).write_text(channel._set_cell_xy(first, ('cart', 500, 300)), encoding='utf-8')
            md = MarkdownCleanEngineeringModel(name='', sequential_order=1).render(
                channel._shop_model([Property(name='items', type_hint='list')], (None, None))
            )
            channel.create_kept(md, self.path)
            self.xml = Path(self.path).read_text(encoding='utf-8')
            self.channel = channel
        with it('should load the existing diagram and keep class positions'):
            expect(self.channel._cell_xy(self.xml, 'cart')).to(equal((500.0, 300.0)))
        with it('should refresh class contents from the new model'):
            expect(self.xml).to(contain('items'))
    with context('no existing diagram at the output path'):
        with it('should create a new diagram'):
            with tempfile.TemporaryDirectory() as tmp:
                path = str(Path(tmp) / 'fresh.drawio')
                channel = _Channel()
                md = MarkdownCleanEngineeringModel(name='', sequential_order=1).render(channel._shop_model(None, (None, None)))
                channel.create_kept(md, path)
                xml = Path(path).read_text(encoding='utf-8')
                expect(channel._has_vertex(xml, 'cart')).to(be_true)
                expect(Path(path).exists()).to(be_true)
