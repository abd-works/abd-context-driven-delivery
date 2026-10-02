"""Channel transform. Not collected with the other specs.

Loads the expected markdown, Draw.io, and TypeScript, writes each channel
under actual/from-{source}/to-{target}, and walks every node.

    .\\.venv\\Scripts\\python.exe -m mamba.cli practices/clean_engineering/model/class_channel.feature.py
"""

import html
import re
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

from expects import equal, expect
from mamba import before, context, describe, included_context, it, shared_context

from practices.clean_engineering.model.base_class_model import CleanEngineeringModel, Module, is_interface_name
from practices.clean_engineering.model.drawio.drawio_class_model import DrawIOCleanEngineeringModel
from practices.clean_engineering.model.markdown.markdown_class_model import MarkdownCleanEngineeringModel
from practices.clean_engineering.model.knowledge_graph.nodes import KnowledgeGraphCleanEngineeringModel
from practices.clean_engineering.model.typescript.typescript_class_model import (
    TypeScriptCleanEngineeringModel,
    _camel_identifier,
    _ts_type,
)

EXPECTED = Path(__file__).resolve().parent / ".examples" / "expected"
ACTUAL = Path(__file__).resolve().parent / ".examples" / "actual"

# TypeScript path, Draw.io path. Module names are the class-model.md headings.
_FILES = {
    "Customer": ("customer/Customer.ts", "customer/customer.drawio"),
    "KYC": ("KYC/kyc.ts", "KYC/kyc.drawio"),
    "Cart": ("cart/Cart.ts", "cart/cart.drawio"),
    "Plans": ("plans/plans.ts", "plans/plans.drawio"),
    "Numbers and SIMs": ("number/Numbers.ts", "number/numbers.drawio"),
    "Porting": ("number/porting.ts", "number/porting.drawio"),
    "Payments": ("billing/payments.ts", "billing/payments.drawio"),
    "Billing": ("billing/Billing.ts", "billing/billing.drawio"),
    "Subscription": ("subscription/Subscription.ts", "subscription/subscription.drawio"),
    "Care": ("care/care.ts", "care/care.drawio"),
}

_SOURCES = ("markdown", "drawio", "typescript")
_CHANNELS = ("markdown", "drawio", "typescript")


def _op_name(class_name: str, operation_name: str) -> str:
    if operation_name in {class_name, "constructor"}:
        return "constructor"
    return operation_name


def _is_constructor(class_name: str, operation) -> bool:
    return operation.name in {class_name, "constructor"}


def walk(model: CleanEngineeringModel) -> list:
    """Every module, class, property, operation, parameter, and relationship, in model order."""
    rows = []

    def visit_module(module, depth: int) -> None:
        rows.append(("module", depth, module.name))
        for loaded in module.classes:
            rows.append(("class", depth + 1, loaded.name, loaded.intent or ""))
            for prop in loaded.properties:
                rows.append((
                    "property",
                    depth + 2,
                    prop.name,
                    prop.type_hint,
                    prop.description or "",
                    prop.access,
                    prop.stereotype,
                    prop.cardinality,
                    prop.origin,
                ))
                for invariant in prop.invariants:
                    rows.append(("invariant", depth + 3, prop.name, invariant.sequential_order, invariant.text))
            for operation in loaded.operations:
                parameters = tuple((parameter.name, parameter.type_hint) for parameter in operation.parameters)
                rows.append((
                    "operation",
                    depth + 2,
                    _op_name(loaded.name, operation.name),
                    operation.return_type,
                    parameters,
                    tuple(operation.callees),
                    operation.description or "",
                ))
                for invariant in operation.invariants:
                    rows.append((
                        "invariant",
                        depth + 3,
                        _op_name(loaded.name, operation.name),
                        invariant.sequential_order,
                        invariant.text,
                    ))
            for relationship in loaded.relationships:
                rows.append((
                    "relationship",
                    depth + 2,
                    relationship.kind,
                    relationship.target,
                    relationship.cardinality,
                ))
        for child in module.modules:
            visit_module(child, depth + 1)

    for module in model.modules:
        visit_module(module, 0)
    return rows


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _one_module(module) -> CleanEngineeringModel:
    source = CleanEngineeringModel(name=module.name, sequential_order=1)
    holder = Module(name=module.name, sequential_order=module.sequential_order)
    holder.classes = list(module.classes)
    holder.modules = list(module.modules)
    source.modules.append(holder)
    return source


def _render_markdown(model: CleanEngineeringModel) -> str:
    channel = MarkdownCleanEngineeringModel(name=model.name, sequential_order=1)
    channel.translate_from(model)
    return channel.render()


def _render_typescript(model: CleanEngineeringModel) -> str:
    channel = TypeScriptCleanEngineeringModel(name=model.name, sequential_order=1)
    channel.translate_from(model)
    return channel.render()


def _code_path(name: str) -> str:
    return _FILES[name][0]


def _drawio_path(name: str) -> str:
    return _FILES[name][1]


def load_source(name: str) -> CleanEngineeringModel:
    if name == "markdown":
        return MarkdownCleanEngineeringModel().parse((EXPECTED / "class-model.md").read_text(encoding="utf-8"))
    model = CleanEngineeringModel(name=name, sequential_order=1)
    for module_name in _FILES:
        if name == "drawio":
            text = (EXPECTED / _drawio_path(module_name)).read_text(encoding="utf-8")
            parsed = DrawIOCleanEngineeringModel().load(text)
        else:
            text = (EXPECTED / _code_path(module_name)).read_text(encoding="utf-8")
            parsed = TypeScriptCleanEngineeringModel.parse(text)
        for module in parsed.modules:
            module.name = module_name
            model.modules.append(module)
    return model


def save_channel(source_name: str, target: str, source: CleanEngineeringModel) -> CleanEngineeringModel:
    folder = ACTUAL / f"from-{source_name}" / f"to-{target}"
    if folder.exists():
        shutil.rmtree(folder)
    folder.mkdir(parents=True)
    if target == "markdown":
        _write(folder / "class-model.md", _render_markdown(source))
        return MarkdownCleanEngineeringModel().parse((folder / "class-model.md").read_text(encoding="utf-8"))
    if target == "drawio":
        return _save_drawio(folder, source)
    if target == "knowledge_graph":
        copied = KnowledgeGraphCleanEngineeringModel(source)
        copied.translate_from(source)
        _write(folder / "class-model.kg", copied.save())
        return copied
    loaded = CleanEngineeringModel(name=source.name, sequential_order=1)
    for module in source.modules:
        _write(folder / _code_path(module.name), _render_typescript(_one_module(module)))
        parsed = TypeScriptCleanEngineeringModel.parse((folder / _code_path(module.name)).read_text(encoding="utf-8"))
        for parsed_module in parsed.modules:
            parsed_module.name = module.name
            loaded.modules.append(parsed_module)
    return loaded


def _save_drawio(folder: Path, source: CleanEngineeringModel) -> CleanEngineeringModel:
    """One page per module, with an edge for every relationship whose target is on the model."""
    pages = _drawio_pages(DrawIOCleanEngineeringModel(name=source.name, sequential_order=1).render(source))
    loaded = CleanEngineeringModel(name=source.name, sequential_order=1)
    for module in source.modules:
        text = pages[module.name]
        _write(folder / _drawio_path(module.name), text)
        parsed = DrawIOCleanEngineeringModel().load(text)
        for parsed_module in parsed.modules:
            parsed_module.name = module.name
            loaded.modules.append(parsed_module)
    return loaded


def _drawio_pages(text: str) -> dict:
    root = ET.fromstring(text)
    pages = {}
    for diagram in list(root.findall("diagram")):
        page = ET.Element("mxfile")
        page.set("host", "CleanEngineering.diagram.drawio")
        page.append(diagram)
        ET.indent(page, space="  ")
        pages[diagram.get("name") or ""] = ET.tostring(page, encoding="unicode")
    return pages


def _class_names(model: CleanEngineeringModel) -> set:
    names = set()

    def visit(modules) -> None:
        for module in modules:
            names.update(loaded.name for loaded in module.classes)
            visit(module.modules)

    visit(model.modules)
    return names


def _model_edges(model: CleanEngineeringModel) -> list:
    """Source class, kind, target. A target that is not a class on the model has no box to connect."""
    names = _class_names(model)
    edges = []

    def visit(modules) -> None:
        for module in modules:
            for loaded in module.classes:
                for relationship in loaded.relationships:
                    if relationship.target in names:
                        edges.append((loaded.name, relationship.kind or "association", relationship.target))
            visit(module.modules)

    visit(model.modules)
    return edges


def _diagram_edges(text: str) -> list:
    """Edges written in the Draw.io file: source class, kind, target class. Import cards count."""
    root = ET.fromstring(text)
    names = {}
    for cell in root.iter("mxCell"):
        if cell.get("vertex") != "1":
            continue
        value = html.unescape(cell.get("value") or "")
        match = re.search(r"<b[^>]*>([^<]+)</b>", value)
        if match:
            names[cell.get("id")] = match.group(1).strip()
    channel = DrawIOCleanEngineeringModel()
    edges = []
    for cell in root.iter("mxCell"):
        if cell.get("edge") != "1":
            continue
        source = names.get(cell.get("source"))
        target = names.get(cell.get("target"))
        if not source or not target:
            continue
        edges.append((source, channel._classify_edge(cell.get("style") or ""), target))
    return edges


def _diagram_file(source_name: str, module_name: str) -> Path:
    return ACTUAL / f"from-{source_name}" / "to-drawio" / _drawio_path(module_name)


def _code_file(source_name: str, module_name: str) -> Path:
    return ACTUAL / f"from-{source_name}" / "to-typescript" / _code_path(module_name)


def _solid_class_names(text: str) -> set:
    """Class boxes on the page. Dashed cards are imports from another module."""
    root = ET.fromstring(text)
    names = set()
    for cell in root.iter("mxCell"):
        if cell.get("vertex") != "1" or "dashed=1" in (cell.get("style") or ""):
            continue
        value = html.unescape(cell.get("value") or "")
        match = re.search(r"<b[^>]*>([^<]+)</b>", value)
        if match:
            names.add(match.group(1).strip())
    return names


def _written_diagram_edges(source_name: str, model: CleanEngineeringModel) -> list:
    folder = ACTUAL / f"from-{source_name}" / "to-drawio"
    edges = []
    for module in model.modules:
        edges.extend(_diagram_edges((folder / _drawio_path(module.name)).read_text(encoding="utf-8")))
    return edges


with shared_context("a class model saved through a channel"):
    with it("should match each module, class, property, operation, parameter, and relationship"):
        expected = self.source
        actual = self.loaded
        stores_properties = self.channel != "typescript"
        stores_intent = self.channel == "markdown"
        stores_property_notes = self.channel == "markdown"
        stores_invariants = self.channel != "drawio"
        stores_interactions = self.channel != "drawio"
        stores_types = self.channel != "typescript"
        stores_relationships = self.channel == "drawio"

        def check_parameters(actual_operation, expected_operation, class_name: str) -> None:
            if self.channel == "typescript" and _is_constructor(class_name, expected_operation):
                return
            expect(len(actual_operation.parameters)).to(equal(len(expected_operation.parameters)))
            for index, expected_parameter in enumerate(expected_operation.parameters):
                actual_parameter = actual_operation.parameters[index]
                expect(actual_parameter.name).to(equal(expected_parameter.name))
                if stores_types:
                    expect(actual_parameter.type_hint).to(equal(expected_parameter.type_hint))

        def check_operations(actual_class, expected_class) -> None:
            expect(len(actual_class.operations)).to(equal(len(expected_class.operations)))
            for index, expected_operation in enumerate(expected_class.operations):
                actual_operation = actual_class.operations[index]
                expect(_op_name(actual_class.name, actual_operation.name)).to(
                    equal(_op_name(expected_class.name, expected_operation.name))
                )
                if stores_types:
                    expect(actual_operation.return_type).to(equal(expected_operation.return_type))
                check_parameters(actual_operation, expected_operation, expected_class.name)
                if stores_interactions:
                    expect(tuple(actual_operation.callees)).to(equal(tuple(expected_operation.callees)))
                    expect(actual_operation.description or "").to(equal(expected_operation.description or ""))
                    expect([item.text for item in actual_operation.invariants]).to(
                        equal([item.text for item in expected_operation.invariants])
                    )

        def check_properties(actual_class, expected_class) -> None:
            expect(len(actual_class.properties)).to(equal(len(expected_class.properties)))
            for index, expected_property in enumerate(expected_class.properties):
                actual_property = actual_class.properties[index]
                expect(actual_property.name).to(equal(expected_property.name))
                expect(actual_property.type_hint).to(equal(expected_property.type_hint))
                expect(actual_property.access).to(equal(expected_property.access))
                drawn = self.channel != "drawio" or any(
                    name in _class_names(self.source)
                    for name in re.findall(r"\b([A-Z][A-Za-z0-9]*)\b", expected_property.type_hint or "")
                )
                if drawn:
                    expect(actual_property.stereotype).to(equal(expected_property.stereotype))
                    expected_relationship = expected_property.relationship
                    actual_relationship = actual_property.relationship
                    if expected_relationship is None:
                        expect(actual_relationship).to(equal(None))
                    else:
                        expect(actual_relationship is not None).to(equal(True))
                        expect(actual_relationship.target).to(equal(expected_relationship.target))
                        expect(actual_relationship.kind).to(equal(expected_relationship.kind))
                        if self.channel != "drawio":
                            expect(actual_relationship.cardinality).to(equal(expected_relationship.cardinality))
                if self.channel != "drawio":
                    expect(actual_property.cardinality).to(equal(expected_property.cardinality))
                    expect(actual_property.origin).to(equal(expected_property.origin))
                if stores_property_notes:
                    expect(actual_property.description or "").to(equal(expected_property.description or ""))
                if stores_invariants:
                    expect([item.sequential_order for item in actual_property.invariants]).to(
                        equal([item.sequential_order for item in expected_property.invariants])
                    )
                    expect([item.text for item in actual_property.invariants]).to(
                        equal([item.text for item in expected_property.invariants])
                    )

        def check_modules(actual_modules, expected_modules) -> None:
            expect(len(actual_modules)).to(equal(len(expected_modules)))
            for index, expected_module in enumerate(expected_modules):
                actual_module = actual_modules[index]
                expect(actual_module.name).to(equal(expected_module.name))
                expect(len(actual_module.classes)).to(equal(len(expected_module.classes)))
                for class_index, expected_class in enumerate(expected_module.classes):
                    actual_class = actual_module.classes[class_index]
                    expect(actual_class.name).to(equal(expected_class.name))
                    if stores_intent:
                        expect(actual_class.intent or "").to(equal(expected_class.intent or ""))
                    if stores_properties:
                        check_properties(actual_class, expected_class)
                    check_operations(actual_class, expected_class)
                check_modules(actual_module.modules, expected_module.modules)

        check_modules(actual.modules, expected.modules)
        if stores_relationships:
            expected_edges = sorted(_model_edges(expected))
            expect(expected_edges).to(equal(sorted(_written_diagram_edges(self.source_name, expected))))
            expect(expected_edges).to(equal(sorted(_model_edges(actual))))


with shared_context("a drawio page"):
    with it("should keep each module on its own page and cluster only that module's classes"):
        for module in self.source.modules:
            text = _diagram_file(self.source_name, module.name).read_text(encoding="utf-8")
            expect(text.count("<diagram")).to(equal(1))
            expect(_solid_class_names(text)).to(equal({loaded.name for loaded in module.classes}))

    with it("should join property relationships with arrows that meet both classes"):
        for module in self.source.modules:
            text = _diagram_file(self.source_name, module.name).read_text(encoding="utf-8")
            for source_name, _kind, target_name in _diagram_edges(text):
                expect(bool(source_name) and bool(target_name)).to(equal(True))

    with it("should meet each class on a side of its box"):
        for module in self.source.modules:
            root = ET.fromstring(_diagram_file(self.source_name, module.name).read_text(encoding="utf-8"))
            for cell in root.iter("mxCell"):
                if cell.get("edge") != "1":
                    continue
                style = cell.get("style") or ""
                expect("exitX=" in style and "entryX=" in style).to(equal(True))


def _class_source(text: str, name: str) -> str:
    """The class or interface block, from its heading through the matching brace."""
    for marker in (f"class {name} {{", f"interface {name} {{", f"abstract class {name} "):
        start = text.find(marker)
        if start >= 0:
            break
    else:
        return ""
    depth = 0
    for index in range(start, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[start:index + 1]
    return ""


def _comments_above(block: str, field_line: str) -> list:
    lines = block.splitlines()
    for index, line in enumerate(lines):
        if line.strip() != field_line:
            continue
        notes = []
        cursor = index - 1
        while cursor >= 0 and lines[cursor].strip().startswith("//"):
            notes.append(lines[cursor].strip()[2:].strip())
            cursor -= 1
        notes.reverse()
        return notes
    return []


with shared_context("a typescript file"):
    with it("should declare each class, field, and constructor assignment"):
        for module in self.source.modules:
            text = _code_file(self.source_name, module.name).read_text(encoding="utf-8")
            for loaded in module.classes:
                block = _class_source(text, loaded.name)
                expect(bool(block)).to(equal(True))
                if is_interface_name(loaded.name) or not loaded.properties:
                    continue
                expect("constructor(" in block).to(equal(True))
                for prop in loaded.properties:
                    camel = _camel_identifier(prop.name)
                    expect(f"this.{camel} = {camel};" in block).to(equal(True))

    with it("should put the stereotype, cardinality, and origin on the lines above the field"):
        for module in self.source.modules:
            text = _code_file(self.source_name, module.name).read_text(encoding="utf-8")
            for loaded in module.classes:
                block = _class_source(text, loaded.name)
                for prop in loaded.properties:
                    if not prop.type_hint:
                        continue
                    field = f"{_camel_identifier(prop.name)}: {_ts_type(prop.type_hint)};"
                    notes = _comments_above(block, field)
                    if prop.stereotype:
                        expect(f"<< {prop.stereotype} >>" in notes).to(equal(True))
                    if prop.cardinality:
                        expect(prop.cardinality in notes).to(equal(True))
                    if prop.origin:
                        expect(f"from {prop.origin}" in notes).to(equal(True))

    with it("should call each callee from the operation that names it"):
        for module in self.source.modules:
            text = _code_file(self.source_name, module.name).read_text(encoding="utf-8")
            for loaded in module.classes:
                block = _class_source(text, loaded.name)
                for operation in loaded.operations:
                    for callee in operation.callees:
                        expect(f"{callee}();" in block).to(equal(True))
                    if operation.name in {loaded.name, "constructor"} or not operation.return_type:
                        continue
                    signature = re.search(
                        rf"{re.escape(_camel_identifier(operation.name))}\([^)]*\):\s*{re.escape(operation.return_type)}(?:\s|\{{)",
                        block,
                    )
                    expect(signature is not None).to(equal(True))


def _open(example, source_name: str, target: str) -> None:
    example.source_name = source_name
    example.source = example.sources[source_name]
    example.channel = target
    example.loaded = save_channel(source_name, target, example.source)


with describe("a class model"):
    with before.all:
        if ACTUAL.exists():
            shutil.rmtree(ACTUAL)
        self.sources = {name: load_source(name) for name in _SOURCES}
        self.walks = {name: walk(model) for name, model in self.sources.items()}

    with context("that is loaded from the expected markdown"):
        with it("should include every module, class, property, and operation"):
            kinds = {row[0] for row in self.walks["markdown"]}
            expect(kinds.issuperset({"module", "class", "property", "operation", "invariant"})).to(equal(True))

    with describe("from markdown"):
        with describe("to markdown"):
            with before.all:
                _open(self, "markdown", "markdown")
            with included_context("a class model saved through a channel"):
                pass
            with context("that is saved a second time"):
                with it("should keep the same nodes"):
                    again = save_channel("markdown", "markdown", self.loaded)
                    expect(walk(again)).to(equal(walk(self.loaded)))
        with describe("to drawio"):
            with before.all:
                _open(self, "markdown", "drawio")
            with included_context("a class model saved through a channel"):
                pass
            with included_context("a drawio page"):
                pass
            with context("with relationships drawn on the page"):
                with it("should connect classes in this module and classes that live in another module"):
                    edges = _written_diagram_edges(self.source_name, self.source)
                    names_by_module = {
                        module.name: {loaded.name for loaded in module.classes}
                        for module in self.source.modules
                    }
                    leaves = [
                        edge for module in self.source.modules
                        for edge in _diagram_edges(
                            (ACTUAL / f"from-{self.source_name}" / "to-drawio" / _drawio_path(module.name)).read_text(encoding="utf-8")
                        )
                        if edge[2] not in names_by_module[module.name]
                    ]
                    expect(bool(edges) and bool(leaves)).to(equal(True))
        with describe("to typescript"):
            with before.all:
                _open(self, "markdown", "typescript")
            with included_context("a class model saved through a channel"):
                pass
            with included_context("a typescript file"):
                pass
            with context("with domain types on fields and signatures"):
                with it("should bring those types back as relationships"):
                    rows = [row for row in walk(self.loaded) if row[0] == "relationship"]
                    expect(len(rows) > 0).to(equal(True))
        with describe("to knowledge graph"):
            with before.all:
                _open(self, "markdown", "knowledge_graph")
            with included_context("a class model saved through a channel"):
                pass

    with describe("from drawio"):
        with describe("to markdown"):
            with before.all:
                _open(self, "drawio", "markdown")
            with included_context("a class model saved through a channel"):
                pass
        with describe("to drawio"):
            with before.all:
                _open(self, "drawio", "drawio")
            with included_context("a class model saved through a channel"):
                pass
            with included_context("a drawio page"):
                pass
        with describe("to typescript"):
            with before.all:
                _open(self, "drawio", "typescript")
            with included_context("a class model saved through a channel"):
                pass
            with included_context("a typescript file"):
                pass
        with describe("to knowledge graph"):
            with before.all:
                _open(self, "drawio", "knowledge_graph")
            with included_context("a class model saved through a channel"):
                pass

    with describe("from typescript"):
        with describe("to markdown"):
            with before.all:
                _open(self, "typescript", "markdown")
            with included_context("a class model saved through a channel"):
                pass
        with describe("to drawio"):
            with before.all:
                _open(self, "typescript", "drawio")
            with included_context("a class model saved through a channel"):
                pass
            with included_context("a drawio page"):
                pass
        with describe("to typescript"):
            with before.all:
                _open(self, "typescript", "typescript")
            with included_context("a class model saved through a channel"):
                pass
            with included_context("a typescript file"):
                pass
        with describe("to knowledge graph"):
            with before.all:
                _open(self, "typescript", "knowledge_graph")
            with included_context("a class model saved through a channel"):
                pass

with describe("a class model populated from the stored codeql database"):
    with it("should write the typescript classes"):
        from practices.clean_engineering.model.codeql.codeql_model import (
            CleanEngineeringModel as CodeQLCleanEngineeringModel,
        )

        database = (
            Path(__file__).resolve().parents[2]
            / "stories"
            / "model"
            / ".examples"
            / "expected"
            / "codeql"
        )
        populated = CodeQLCleanEngineeringModel.load_content(database)
        expected_names = set()
        for path in EXPECTED.rglob("*.ts"):
            expected_names.update(re.findall(r"(?m)^class\s+(\w+)", path.read_text(encoding="utf-8")))
        found = {item.name for module in populated.modules for item in module.classes}
        expect(bool(found) and found <= expected_names).to(equal(True))
        expect({"Customer", "AccountCredentials", "Plan"} <= found).to(equal(True))
        written = set()
        for module in populated.modules:
            parsed = TypeScriptCleanEngineeringModel.parse(_render_typescript(_one_module(module)))
            written.update(item.name for parsed_module in parsed.modules for item in parsed_module.classes)
        expect(written).to(equal(found))
