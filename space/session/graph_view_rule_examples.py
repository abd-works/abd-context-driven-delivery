"""Examples for the rules the Files app's graph view shows on checkout-flow's nodes: the LERN overlay's Domain tier rules,
which LERN, constrained to TypeScript, gives a TypeScript domain class and never a Python one. Shared by the story tests of
Explore Graph In Files App."""

from __future__ import annotations

from space.kanban.session_board_examples import SessionSeed
from space.session.graph_view_examples import STORY_MAP, STORY_MAP_TEXT, TICKET_CODE, TICKET_TEXT, session_of

# Seed: checkout-flow working in the whole project with Stories, DDD and Clean Engineering on, so a class stereotyped as
# an aggregate root is a DDD entity root, the node LERN's Domain tier rules sit on.
CHECKOUT_FLOW_WITH_DDD = SessionSeed(
    "checkout-flow",
    "Checkout flow",
    fields={
        "practices": {key: {"enabled": False} for key in ("ux", "bdd")},
        "outputs": {"stories": {"root": ".context"}},
    },
)
# Seed: Ticket in ticket.py, stereotyped as an aggregate root, so DDD reads it as an entity root.
TICKET_ROOT_TEXT = "@aggregate_root\n" + TICKET_TEXT
# Seed: Ticket in ticket.ts, the Domain tier of LERN's ticket aggregate (src/<bounded context>/<aggregate>/<aggregate>.ts):
# the aggregate root Ticket and its in-memory repository, framework-free.
TICKET_DOMAIN_TIER = "src/kanban/ticket/ticket.ts"
TICKET_DOMAIN_TIER_TEXT = (
    "@AggregateRoot()\n"
    "export class Ticket {\n"
    "  activate(): void {\n"
    "    return\n"
    "  }\n"
    "}\n"
    "\n"
    "export class TicketRepository {\n"
    "  load(id: string): Ticket {\n"
    "    return new Ticket()\n"
    "  }\n"
    "}\n"
)
LERN = "lern_domain_driven"
# Interaction: the rules LERN's schema gives the entity root of its Domain tier
# (cdd_guidance/patterns/lern_domain_driven/practices/ddd/model/rules.yaml, entityRoot).
LERN_DOMAIN_TIER_RULES = ("share-domain-logic", "implement-domain-entities-correctly", "use-ubiquitous-language")
LISTED_WITH_DOMAIN_TIER = [STORY_MAP, TICKET_CODE, TICKET_DOMAIN_TIER]


def seed_checkout_flow_with_both_tickets(world) -> None:
    world.project.seed_session(CHECKOUT_FLOW_WITH_DDD)
    for path, text in ((TICKET_CODE, TICKET_ROOT_TEXT), (TICKET_DOMAIN_TIER, TICKET_DOMAIN_TIER_TEXT), (STORY_MAP, STORY_MAP_TEXT)):
        world.project.seed_file(path, text)


def entries_named(world, name: str, paths: list[str]) -> list[dict]:
    """Every entry named name in the trees answered for paths, each as its branch answers it, opening each branch as the
    page opens it."""
    session = session_of(world)
    found, named = list(world.data_of(session.graph_trees(paths=paths))), []
    while found:
        entry = found.pop()
        if entry["children_left_out"]:
            entry = world.data_of(session.graph_branch(node_id=entry["node_id"], paths=paths)) or entry
        if entry["name"] == name:
            named.append(entry)
        found.extend(child for child in entry["children"] if "children_left_out" in child)
    return named


def rule_slugs_on(world, name: str, path: str, paths: list[str]) -> set[str]:
    """The rules the graph view shows on the nodes named name read from the file at path, by slug."""
    held = [entry for entry in entries_named(world, name, paths) if f":{path}:" in entry["node_id"]]
    return {rule["slug"] for entry in held for rules in entry["children"] if rules.get("type") == "rules" for rule in rules["children"]}
