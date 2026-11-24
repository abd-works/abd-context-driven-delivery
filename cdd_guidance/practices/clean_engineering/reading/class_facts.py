"""The facts each class keeps about the other classes of the graph: the data bags it acts on, the fields and names it
copies from another class, the one class it only forwards to, the domain it extends from another package, and the
collaborator it builds that its caller cannot hand it."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from cdd_guidance.practices.clean_engineering.model.base_class_model import is_interface_name
from cdd_guidance.practices.clean_engineering.measures.read_facts import is_under, parameters_of
from cdd_guidance.practices.clean_engineering.reading.production_classes import names_in
from cdd_guidance.practices.clean_engineering.reading.folder_facts import folders_of, parent_folder, record_fact
from cdd_guidance.practices.clean_engineering.model.source_facts import CONSTRUCTOR_NAMES
from cdd_guidance.practices.source_code import split_top_level

if TYPE_CHECKING:
    from harness.graph.graph import Node

    from cdd_guidance.practices.clean_engineering.reading.production_classes import ProductionClass, ProductionClasses

# A copy of another class's fields: at least this many shared fields, covering most of the smaller class.
_MIN_COPIED_FIELDS = 3
_COPIED_SHARE = 0.75
_NAME_COPY = re.compile(r"^_*(?P<owner>[a-z]\w*?)(?:_name|_slug|Name|Slug)$")
_KEYED_COLLECTIONS = frozenset({"dict", "Dict", "Mapping", "MutableMapping", "Record", "Map"})
_STRING_KEYS = frozenset({"str", "string"})
# The fields a class is named by. Only a class that has a name can have its name copied.
_NAMING_FIELDS = frozenset({"name", "slug", "title", "key", "label"})
# A class whose name says it reaches outside the object: its caller has to be able to hand it a different one.
_OUTSIDE_COLLABORATOR = re.compile(
    r"(?:Repository|Repo|Service|Client|Gateway|Api|API|Provider|File|Connection|Database|Server|Cli|Socket|Process"
    r"|Daemon|Store)$"
)


class ComparedFact:
    """One fact the build records on each class by comparing it with the other production classes of the graph, after
    each read; a rule then reads only the fact."""

    def __init__(self, classes: "ProductionClasses") -> None:
        self._classes = classes

    def record(self) -> None:
        raise NotImplementedError(f"{type(self).__name__} must record its fact")


class ServicesTakingDataBags(ComparedFact):
    """The data bags each service takes (``data_bags_taken``): a service is a class with behavior and no state, and a data
    bag a class that holds state and does nothing; the bags are those its operations take as parameters."""

    def record(self) -> None:
        bags = {each.name for each in self._classes if each.fields and not each.has_behavior}
        for service in self._classes:
            record_fact(service.node, "data_bags_taken", self._bags_taken(service, bags) if self._is_service(service) else [])

    def _is_service(self, each: "ProductionClass") -> bool:
        """A class with behavior and no state. An interface declares what a resource does; it holds no state by design,
        so it is not a service."""
        return not each.fields and each.has_behavior and not is_interface_name(each.name)

    def _bags_taken(self, service: "ProductionClass", bags: set[str]) -> list[str]:
        """The data bags the service's operations take as parameters, other than the service itself."""
        return sorted(
            {
                name
                for operation in service.operations
                for parameter in parameters_of(operation)
                for name in names_in(parameter.get_fact("type_hint", "")) & bags
                if name != service.name
            }
        )


class CopiedModels(ComparedFact):
    """Copies of another class's data each class holds: the fields it copies from another class (``copied_fields``: the
    other class's name and the fields), and its name copies of a reference and dicts that hold one value per member,
    keyed by the member's name (``copied_references``: the field, ``name`` or ``member``, and the class it copies)."""

    def __init__(self, classes: "ProductionClasses") -> None:
        super().__init__(classes)
        # A mixin's annotations declare what the class it is mixed into holds, so it holds no model of its own.
        self._fields = {each.node_id: {} if each.is_mixin else each.fields for each in classes}

    def record(self) -> None:
        # Two subclasses that each fill the fields of a base they share hold one model, the base's, so a copy is looked
        # for only among the fields a class declares beyond its bases'.
        declared = {each.node_id: self._beyond_bases(each, self._fields[each.node_id]) for each in self._classes}
        holders: dict[str, list["Node"]] = {}
        for each in self._classes:
            for field in declared[each.node_id]:
                holders.setdefault(field, []).append(each.node)
        for each in self._classes:
            record_fact(each.node, "copied_fields", self._copied_fields(each.node, holders, declared))
            record_fact(each.node, "copied_references", self._copied_references(each))

    def _copied_fields(self, node: "Node", holders: dict[str, list["Node"]], fields: dict[str, dict[str, str]]) -> list:
        """The smaller class of each pair is the copy: it is the one holding a subset of the other's fields."""
        own = set(fields[node.node_id])
        for other in self._sharing_fields(own, holders):
            theirs = set(fields[other.node_id])
            if other is node or self._related(node, other) or (len(own), node.node_id) > (len(theirs), other.node_id):
                continue
            # A field copies another only with the same type: three common names, such as `result`, are no copied model.
            shared = {field for field in own & theirs if fields[node.node_id][field] == fields[other.node_id][field]}
            if self._copies(shared, own, theirs):
                return [other.name, sorted(shared)]
        return []

    def _sharing_fields(self, own: set[str], holders: dict[str, list["Node"]]) -> list["Node"]:
        """Every class holding any of the fields, each once, in the order of its node id."""
        others = {other.node_id: other for field in own for other in holders.get(field, [])}
        return [others[other_id] for other_id in sorted(others)]

    def _related(self, node: "Node", other: "Node") -> bool:
        """A subclass repeats its base's fields by design."""
        return other.name in (node.get_fact("bases", []) or []) or node.name in (other.get_fact("bases", []) or [])

    def _beyond_bases(self, each: "ProductionClass", fields: dict[str, str]) -> dict[str, str]:
        """The fields it holds that none of the classes it derives from declares, through every base the graph holds."""
        inherited: set[str] = set()
        seen: set[str] = set()
        pending = each.bases
        while pending:
            base = pending.pop()
            if base in seen:
                continue
            seen.add(base)
            for declaring in self._classes.named(base):
                inherited |= set(declaring.fields)
                pending.extend(declaring.bases)
        return {field: hint for field, hint in fields.items() if field not in inherited}

    def _copies(self, shared: set[str], own: set[str], theirs: set[str]) -> bool:
        smaller = min(len(own), len(theirs))
        return len(shared) >= _MIN_COPIED_FIELDS and len(shared) >= _COPIED_SHARE * smaller

    def _copied_references(self, each: "ProductionClass") -> list[list[str]]:
        """A name copy of a reference, or one value per member keyed by its name. A failure keeps the name of what it
        failed on for its message, so its names are not copies."""
        found: list[list[str]] = []
        node = each.node
        named_copies = not each.is_failure
        for field, hint in self._fields[node.node_id].items():
            named = _NAME_COPY.match(field) if named_copies else None
            owner = self._class_named(named.group("owner")) if named else ""
            if owner and owner != node.name and self._has_name(owner):
                found.append([field, "name", owner])
                continue
            member = self._member_keyed_by_name(field, hint)
            if member and member != node.name:
                found.append([field, "member", member])
        return found

    def _member_keyed_by_name(self, field: str, hint: str) -> str:
        """`fidelity_states: dict[str, str]` names a member class and keys a dict of one value each by name. A dict keyed
        by anything but a string, such as `dict[int, str]` keyed by `id()`, is keyed by no name."""
        mentioned = names_in(hint)
        if not mentioned & _KEYED_COLLECTIONS or self._key_type(hint) not in _STRING_KEYS:
            return ""
        words = self._words(field)
        for length in range(len(words) - 1, 0, -1):
            member = self._class_named("_".join(words[:length]))
            if member and member not in mentioned and self._holds_value(member, words[length:]):
                return member
        return ""

    def _has_name(self, owner: str) -> bool:
        """True when the class is named by a field of its own, such as `name` or `title`, which a copy could repeat."""
        return any(_NAMING_FIELDS & {field.lstrip("_") for field in declared.fields} for declared in self._classes.named(owner))

    def _holds_value(self, member: str, value_words: list[str]) -> bool:
        """True when the member class holds the value the dict keeps for each one: `fidelity_states` copies a
        `Fidelity`'s `state`. A dict whose values the member does not hold, such as each file's text by its path, copies
        nothing of it."""
        value = "_".join(value_words)
        wanted = {value, value.removesuffix("s"), f"{value}s"}
        return any(
            wanted & {field.lstrip("_") for field in declared.fields} or wanted & {operation.name for operation in declared.operations}
            for declared in self._classes.named(member)
        )

    def _key_type(self, hint: str) -> str:
        """The first type argument of a keyed collection, its key: `str` for `dict[str, int]` or `Record<string, X>`."""
        opened = re.search(r"[\[<]", hint)
        if opened is None:
            return ""
        arguments = split_top_level(hint[opened.end() :].rstrip("]> "))
        return arguments[0].strip() if arguments else ""

    def _class_named(self, snake: str) -> str:
        pascal = "".join(word.capitalize() for word in self._words(snake))
        return pascal if bool(self._classes.named(pascal)) else ""

    def _words(self, name: str) -> list[str]:
        spaced = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", name.strip("_"))
        return [word.lower() for word in spaced.split("_") if word]


class PassThroughClasses(ComparedFact):
    """Pass-through layers: the one class each class's public operations all forward to (``forwards_to``), and, on each
    folder whose classes all forward, and all to the classes of one other folder, that folder (``forwards_to_module``,
    empty on every other folder)."""

    def record(self) -> None:
        targets = {each.node_id: self._forwarding_target(each) for each in self._classes}
        names = {node.node_id: node.name for node in self._classes.in_graph.nodes("OoadClass")}
        for each in self._classes:
            target = targets[each.node_id]
            record_fact(each.node, "forwards_to", names[target] if target else "")
        self._record_folders(targets)

    def _forwarding_target(self, each: "ProductionClass") -> str:
        """The one class every public operation forwards to, or empty when the class does any work of its own."""
        operations = each.operations
        if not operations or len(each.fields) > 1:
            return ""
        candidates: set[str] | None = None
        for operation in operations:
            callee = self._sole_forward(operation)
            if not callee or (len(operations) == 1 and callee != operation.name):
                return ""
            defining = self._classes.defining(callee) - {each.node_id}
            candidates = defining if candidates is None else candidates & defining
        return sorted(candidates)[0] if candidates and len(candidates) == 1 else ""

    def _sole_forward(self, operation: "Node") -> str:
        """The callee of an operation whose body is one statement making one call on a collaborator: a parameter
        (``cart.subtotal()``) or a field (``self._cart.subtotal()``)."""
        callees = {callee for callee in operation.get_fact("callees", []) or [] if callee}
        body = operation.get_fact("body_text") or ""
        statements = [line for line in body.splitlines() if line.strip() and not line.strip().startswith(("#", "//"))]
        if len(callees) != 1 or len(statements) != 1:
            return ""
        callee = next(iter(callees))
        parameters = [re.escape(parameter.name) for parameter in parameters_of(operation)]
        receivers = [r"(?:self|this)\.\w+"] + [rf"\b{name}" for name in parameters]
        forwards = re.search(rf"(?:{'|'.join(receivers)})\.{re.escape(callee)}\s*\(", statements[0])
        return callee if forwards else ""

    def _record_folders(self, targets: dict[str, str]) -> None:
        """Each module folder whose classes all forward, and all to classes of one other folder."""
        folder_of = {node.node_id: self._folder_id(node) for node in self._classes.in_graph.nodes("OoadClass")}
        members: dict[str, list[str]] = {}
        for each in self._classes:
            members.setdefault(folder_of[each.node_id], []).append(each.node_id)
        reached: dict[str, str] = {}
        for folder_id, class_ids in members.items():
            others = {folder_of[targets[class_id]] for class_id in class_ids if targets[class_id]} - {folder_id}
            if all(targets[class_id] for class_id in class_ids) and len(others) == 1:
                reached[folder_id] = next(iter(others))
        for folder in folders_of(self._classes.in_graph):
            folder.set_fact("forwards_to_module", self._name_of(reached.get(folder.node_id, "")))

    def _name_of(self, folder_id: str) -> str:
        """The name of the folder called folder_id, or its id when the graph holds no node of it; empty for none."""
        if not folder_id:
            return ""
        other = self._classes.in_graph.graph.node(folder_id)
        return other.name if other else folder_id

    def _folder_id(self, node: "Node") -> str:
        """The id of the folder the class belongs to, through its belongsTo edge."""
        return next((edge.child.node_id for edge in node.graph.edges.from_parent("belongsTo", node)), "")


class DomainExtensions(ComparedFact):
    """The domain each class extends from another package (``extends_domain``: the bases it extends, the folder they come
    from, and the bases of its own package it joins them with). A class that joins one of its own package's types with
    the class of another package it is named after extends that other package's domain, so it belongs beside the class
    it extends; in the package that declares that class, or one nested under it, it is where it belongs."""

    def record(self) -> None:
        for each in self._classes:
            record_fact(each.node, "extends_domain", self._extension(each))

    def _extension(self, each: "ProductionClass") -> dict:
        node = each.node
        own_folder = parent_folder(each.file)
        homes = {base: {parent_folder(declared.file) for declared in self._classes.named(base)} for base in each.bases}
        own = [base for base, folders in homes.items() if own_folder in folders]
        extended = self._extended_domain_bases(node.name, homes, own_folder)
        if not own or not extended or self._builds_on(own, homes[extended[0]]):
            return {}
        return {"extended": extended, "home": sorted(homes[extended[0]])[0], "own": own}

    def _builds_on(self, own: list[str], home: set[str]) -> bool:
        """True when a base of the class's own package already derives from a class of the package it extends: the
        package is a format built on that one (`DrawIOClass(DiagramClass)`), and the class is where it belongs, since
        moving it would make the base package import its format."""
        return any(
            parent_folder(declared.file) in home
            for base in own
            for owned in self._classes.named(base)
            for parent in owned.bases
            for declared in self._classes.named(parent)
        )

    def _extended_domain_bases(self, name: str, homes: dict[str, set[str]], own_folder: str) -> list[str]:
        """The bases a class named name extends from another package's domain: the ones it is named after (`GraphEpic`
        extends `Epic`), declared in a package that is neither the class's own nor one it is nested under."""
        return [
            base
            for base, folders in homes.items()
            if folders and not any(is_under(own_folder, folder) for folder in folders) and name.endswith(base)
        ]


class BuiltCollaborators(ComparedFact):
    """The first collaborator each class's constructor builds that its caller cannot hand it (``constructs_collaborator``).
    Left out are values, failures, and collections (``ProductionClasses.is_value``), the peers an Entity composes, and a part the
    owner builds once and keeps: a class of the program's own that is no outside collaborator. An outside collaborator
    is a class the program does not declare, such as a library's client, or one whose name says it reaches outside the
    object (a repository, service, client, gateway, file, connection, or other process)."""

    def record(self) -> None:
        for each in self._classes:
            record_fact(each.node, "constructs_collaborator", self._collaborator(each))

    def _collaborator(self, each: "ProductionClass") -> str:
        node = each.node
        for type_name in node.get_fact("constructs", []):
            if type_name == node.name or self._classes.is_value(type_name) or self._owned_part(each, type_name):
                continue
            # <<Entity>> / <<Aggregate Root>> may compose sibling types from the same file.
            if node.get_fact("composes_peers") and type_name in node.get_fact("peer_names", []):
                continue
            return type_name
        return ""

    def _owned_part(self, owner: "ProductionClass", type_name: str) -> bool:
        """True for a class the program declares, whose name names no outside collaborator, that the constructor builds
        from nothing: `EdgeIndex()`. One built from something outside the object, `Sessions(Path.cwd())`, ties the
        class to that outside thing."""
        if not self._classes.named(type_name) or _OUTSIDE_COLLABORATOR.search(type_name) is not None:
            return False
        built_empty = re.compile(rf"(?<![\w.$]){re.escape(type_name)}\s*\(\s*\)")
        constructors = [operation for operation in owner.operations if operation.name in CONSTRUCTOR_NAMES]
        return any(built_empty.search(operation.get_fact("body_text") or "") for operation in constructors)
