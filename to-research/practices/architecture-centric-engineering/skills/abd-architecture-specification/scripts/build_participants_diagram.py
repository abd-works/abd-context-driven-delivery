#!/usr/bin/env python3
"""
Build script: MERN Architecture Spec — Domain Module Participants class diagram.

Page: Domain Module Participants
Source: architecture-specification.md §Participants

Run:
    python scripts/build_participants_diagram.py
"""
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

SCRIPTS = Path(r"C:\dev\sandbox\.cursor\skills\drawio-domain-sync\scripts")
sys.path.insert(0, str(SCRIPTS))

from drawio_tools import (
    create_empty_mxfile,
    add_page,
    save_drawio,
    build_class_html,
    calc_cell_height,
    CLASS_STYLE,
    CELL_WIDTH,
    create_edge,
    next_id,
    audit_diagram_report,
)

OUT = Path(__file__).resolve().parent.parent / "templates" / "architecture-specification-participants.drawio"
REF = Path(__file__).resolve().parent.parent / "reference" / "participants-class-diagram.drawio"

# ---------------------------------------------------------------------------
# Helper — create class cell with explicit stereotype
# ---------------------------------------------------------------------------

def add_class(root, name, stereotype=None, ops=None, x=40, y=40, w=None):
    ops = ops or []
    cid = str(next_id(root))
    label = build_class_html(name, properties=[], operations=ops, stereotype=stereotype)
    h = calc_cell_height(0, len(ops), 0)
    if stereotype:
        h += 16  # extra line for stereotype text
    cell = ET.SubElement(root, "mxCell")
    cell.set("id", cid)
    cell.set("value", label)
    cell.set("style", CLASS_STYLE)
    cell.set("vertex", "1")
    cell.set("parent", "1")
    geo = ET.SubElement(cell, "mxGeometry")
    geo.set("x", str(x))
    geo.set("y", str(y))
    geo.set("width", str(w or CELL_WIDTH))
    geo.set("height", str(h))
    geo.set("as", "geometry")
    return cell


def eid(cell):
    return cell.get("id")


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

mxfile = create_empty_mxfile()
_, root = add_page(mxfile, "Domain Module Participants",
                   page_width=1460, page_height=900)

# ── ROW 0 (y=40): SHARED — base classes ────────────────────────────────────
# EntityStatus  Entity  Entitys  EntityRepository
# x=40          x=360   x=680    x=1120

entity_status = add_class(
    root, "<<Entity>>Status",
    stereotype="«shared value object»",
    x=40, y=40)

entity = add_class(
    root, "<<Entity>>",
    stereotype="«shared entity»",
    ops=["+<<operation>>()"],
    x=360, y=40)

entitys = add_class(
    root, "<<Entity>>s",
    stereotype="«shared collection»",
    ops=["+<<operation>>()"],
    x=680, y=40)

entity_repo = add_class(
    root, "<<Entity>>Repository",
    stereotype="«shared interface»",
    ops=["+<<operation>>(args)"],
    x=1120, y=40)

# ── ROW 1 (y=260): EXTENSIONS ───────────────────────────────────────────────
# EntityClient   EntitysClient  EntitysServer  EntityRepositoryServer
# x=360          x=580          x=860          x=1120

entity_client = add_class(
    root, "<<Entity>>Client",
    stereotype="«client domain JS»",
    ops=["+<<operation>>()"],
    x=360, y=260)

entitys_client = add_class(
    root, "<<Entity>>sClient",
    stereotype="«client domain JS»",
    ops=["+<<operation>>()", "+toPresentation()"],
    x=580, y=260)

entitys_server = add_class(
    root, "<<Entity>>sServer",
    stereotype="«server»",
    ops=["+<<operation>>(args, repo)"],
    x=860, y=260)

entity_repo_server = add_class(
    root, "<<Entity>>RepositoryServer",
    stereotype="«server»",
    ops=["+<<operation>>(args)"],
    x=1120, y=260)

# ── ROW 2 (y=480): HOOKS / API / ROUTER ────────────────────────────────────
# useEntitys  EntityApi  EntityRouter
# x=360       x=620      x=900

use_entities = add_class(
    root, "use<<Entity>>s",
    stereotype="«client hook»",
    ops=["+<<operation>>()"],
    x=360, y=480)

entity_api = add_class(
    root, "<<Entity>>Api",
    stereotype="«client HTTP»",
    ops=["+<<operation>>(args)"],
    x=620, y=480)

entity_router = add_class(
    root, "<<Entity>>Router",
    stereotype="«server»",
    ops=["+<<operation>>(req, res)"],
    x=900, y=480)

# ── ROW 3 (y=680): VIEWS ────────────────────────────────────────────────────
# FeatureView  EntityListView  EntityCardView
# x=60         x=360           x=640

feature_view = add_class(
    root, "<<Feature>>View",
    stereotype="«app-client»",
    x=60, y=680)

list_view = add_class(
    root, "<<Entity>>ListView",
    stereotype="«client view»",
    x=360, y=680)

card_view = add_class(
    root, "<<Entity>>CardView",
    stereotype="«client view»",
    x=640, y=680)

# ── EDGES ───────────────────────────────────────────────────────────────────
# Rule: distinct anchor points when multiple edges leave/arrive the same side.

# — Inheritance / implementation —

# EntityClient --|> Entity  (both x=360, vertically aligned)
create_edge(root, eid(entity_client), eid(entity), "inheritance",
            label="extends",
            exit_x=0.5, exit_y=0, entry_x=0.5, entry_y=1)

# EntitysClient --|> Entitys  (left child of Entitys)
create_edge(root, eid(entitys_client), eid(entitys), "inheritance",
            label="extends",
            exit_x=0.5, exit_y=0, entry_x=0.3, entry_y=1)

# EntitysServer --|> Entitys  (right child of Entitys — distinct anchor)
create_edge(root, eid(entitys_server), eid(entitys), "inheritance",
            label="extends",
            exit_x=0.5, exit_y=0, entry_x=0.7, entry_y=1)

# EntityRepositoryServer ..|> EntityRepository  (implements)
create_edge(root, eid(entity_repo_server), eid(entity_repo), "dependency",
            label="implements",
            exit_x=0.5, exit_y=0, entry_x=0.5, entry_y=1)

# — Shared associations —

# Entity --> EntityStatus  (uses; to the left — exit left, enter right)
create_edge(root, eid(entity), eid(entity_status), "association-straight",
            label="uses",
            exit_x=0, exit_y=0.5, entry_x=1, entry_y=0.5)

# Entitys o-- Entity  (contains; to the left — exit left, enter right)
create_edge(root, eid(entitys), eid(entity), "aggregation-straight",
            label="contains",
            exit_x=0, exit_y=0.5, entry_x=1, entry_y=0.5)

# — Client interactions —

# EntitysClient --> EntityApi  (calls; downward)
create_edge(root, eid(entitys_client), eid(entity_api), "association",
            label="calls",
            exit_x=0.5, exit_y=1, entry_x=0.3, entry_y=0)

# EntitysClient ..> EntityClient  (toPresentation; leftward)
create_edge(root, eid(entitys_client), eid(entity_client), "dependency",
            label="toPresentation",
            exit_x=0, exit_y=0.5, entry_x=1, entry_y=0.5)

# EntityApi ..> EntityRouter  (uses; rightward)
create_edge(root, eid(entity_api), eid(entity_router), "dependency",
            label="uses",
            exit_x=1, exit_y=0.5, entry_x=0, entry_y=0.5)

# EntityApi ..> Entity  (fromDto via schema; upward, offset to avoid overlap)
create_edge(root, eid(entity_api), eid(entity), "dependency",
            label="fromDto",
            exit_x=0.2, exit_y=0, entry_x=0.8, entry_y=1)

# — Hook —

# useEntitys --> EntitysClient  (holds state; rightward-up)
create_edge(root, eid(use_entities), eid(entitys_client), "association",
            label="holds state",
            exit_x=1, exit_y=0.3, entry_x=0, entry_y=1)

# useEntitys ..> EntityRouter  (uses; rightward)
create_edge(root, eid(use_entities), eid(entity_router), "dependency",
            label="uses",
            exit_x=1, exit_y=0.7, entry_x=0, entry_y=0.7)

# — Views —

# FeatureView --> EntityListView  (composes)
create_edge(root, eid(feature_view), eid(list_view), "association",
            label="composes",
            exit_x=1, exit_y=0.5, entry_x=0, entry_y=0.5)

# EntityListView --> useEntitys  (delegates; upward)
create_edge(root, eid(list_view), eid(use_entities), "association",
            label="delegates",
            exit_x=0.5, exit_y=0, entry_x=0.5, entry_y=1)

# EntityListView --> EntityCardView  (renders; rightward)
create_edge(root, eid(list_view), eid(card_view), "association",
            label="renders",
            exit_x=1, exit_y=0.5, entry_x=0, entry_y=0.5)

# EntityCardView --> EntityClient  (<<operation>>; upward, leftward)
create_edge(root, eid(card_view), eid(entity_client), "association",
            label="<<operation>>",
            exit_x=0.3, exit_y=0, entry_x=0.7, entry_y=1)

# — Server —

# EntityRouter --> EntitysServer  (calls; leftward)
create_edge(root, eid(entity_router), eid(entitys_server), "association",
            label="calls",
            exit_x=0, exit_y=0.5, entry_x=1, entry_y=0.5)

# EntitysServer --> EntityRepository  (<<operation>>; rightward-up)
create_edge(root, eid(entitys_server), eid(entity_repo), "association",
            label="<<operation>>",
            exit_x=1, exit_y=0.3, entry_x=0, entry_y=1)

# EntityRepositoryServer ..> Entity  (maps via schema; leftward across)
create_edge(root, eid(entity_repo_server), eid(entity), "dependency",
            label="maps via schema",
            exit_x=0, exit_y=0.7, entry_x=1, entry_y=0.7)

# ---------------------------------------------------------------------------
# Save + audit
# ---------------------------------------------------------------------------

OUT.parent.mkdir(parents=True, exist_ok=True)
save_drawio(str(OUT), mxfile)
print(f"Saved template: {OUT}")

import shutil
REF.parent.mkdir(parents=True, exist_ok=True)
shutil.copy2(str(OUT), str(REF))
print(f"Copied to reference: {REF}")

report = audit_diagram_report(str(OUT))
print(report)
