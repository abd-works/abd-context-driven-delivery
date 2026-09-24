#!/usr/bin/env python3
"""Regenerate check-resolution-class-diagram.drawio from current CRC.
Layout optimized via validate_layout to minimize edge_crosses_class violations.
Run audit_diagram_report after save to confirm."""
import sys
from pathlib import Path

DRAWIO_TOOLS = Path(r"C:\Users\thoma\.cursor\skills\drawio-domain-sync\scripts")
sys.path.insert(0, str(DRAWIO_TOOLS))

from drawio_tools import (
    create_empty_mxfile, add_page, get_page, save_drawio,
    create_class_cell, create_edge, find_cell_by_name,
    audit_diagram_report,
)

OUTPUT = Path(r"C:\dev\mm3e-online-holistic\docs\check-resolution\check-resolution-class-diagram.drawio")
W = 320
GAP = 40
mxfile = create_empty_mxfile()


def edge(root, src, tgt, etype, label="", **anchors):
    s = find_cell_by_name(root, src)
    t = find_cell_by_name(root, tgt)
    if s is None or t is None:
        print(f"  WARN: edge {src}->{tgt} skipped (missing)")
        return
    create_edge(root, s.get("id"), t.get("id"), etype, label, **anchors)


C0 = 40
C1 = C0 + W + GAP      # 400
C2 = C1 + W + GAP      # 760
C3 = C2 + W + GAP      # 1120


# ═══ PAGE 1: Trait ═══════════════════════════════════════════════════════════
add_page(mxfile, "Trait")
_, root = get_page(mxfile, "Trait")

create_class_cell(root, "Trait",
    properties=[
        "character : Character",
        "purchased rank : number",
        "effective rank : number, Character",
        "modifier : Character, Imposed Conditions, Condition, Game Modifier",
    ],
    operations=[
        "real world value : Measurement, MEASUREMENT_TYPE, effective rank",
        "perform check : Check, Rank, Check Result",
        "AddRank : number, Measurement, MEASUREMENT_TYPE",
    ],
    invariants=[
        "effective rank = purchased rank − modifier",
        "ranks must not be added directly — convert to measures first",
        "MEASUREMENT_TYPE determined by trait operation",
    ],
    x=C0, y=40)

create_class_cell(root, "Character",
    properties=[
        "traits : Trait",
        "applied effects : Applied Effect",
        "imposed conditions : Imposed Conditions",
    ],
    operations=["make check : Check, Trait"],
    x=C2, y=40, imported_from="Character Construction")

create_class_cell(root, "MEASUREMENT_TYPE",
    properties=["MASS=1", "TIME=2", "DISTANCE=3", "VOLUME=4"],
    x=C0, y=420)

create_class_cell(root, "Measurement",
    properties=["measurement type : MEASUREMENT_TYPE"],
    operations=[
        "real-world value : Rank, MEASUREMENT_TYPE",
        "derive throwing distance : Rank",
        "derive travel distance : Rank",
        "derive travel time : Rank",
        "combine via measure arithmetic : Rank",
    ],
    invariants=[
        "throwing distance rank = strength rank − mass rank",
        "travel distance rank = time rank + speed rank",
        "travel time rank = distance rank − speed rank",
        "values at higher ranks are approximate guidelines",
    ],
    x=C2, y=420)

edge(root, "Trait", "Character", "association",
     exit_x=1.0, exit_y=0.25, entry_x=0.0, entry_y=0.25)
edge(root, "Trait", "Measurement", "association",
     exit_x=1.0, exit_y=0.75, entry_x=0.0, entry_y=0.25)
edge(root, "Measurement", "MEASUREMENT_TYPE", "association")


# ═══ PAGE 2: Check ═══════════════════════════════════════════════════════════
#
# Layout: C1 column clear between Check and subtypes.
# Check Result/Graded CR/Character in C2 (right side).
# Opposed on separate row from Routine/Team to prevent crossing.
#
#   R0: [Trait(C0)]     [Check(C1)]      [DC(C2)]
#   R1:                                  [Check Result(C2)]
#   R2:                                  [Graded CR(C2)]   [Condition(C3)]
#   R3: [Opposed(C0)]                    [Character(C2)]
#   R4:                 [Routine(C1)]     [Team(C2)]

add_page(mxfile, "Check")
_, root = get_page(mxfile, "Check")

R0 = 40
create_class_cell(root, "Trait",
    properties=["purchased rank", "effective rank"],
    x=C0, y=R0, imported_from="Trait")

create_class_cell(root, "Check",
    properties=[
        "using trait : Trait",
        "circumstance modifier : (±2 minor or ±5 major)",
    ],
    operations=[
        "roll total : Trait, Difficulty Class",
        "resolve : Difficulty Class, Check Result",
    ],
    invariants=[
        "roll total = d20 + trait rank + circumstance modifier",
        "shape: always roll total vs difficulty class",
    ],
    x=C1, y=R0)

create_class_cell(root, "Difficulty Class",
    properties=["threshold value : (integer 0–40)"],
    x=C2, y=R0)

R1 = 240
create_class_cell(root, "Check Result",
    properties=[
        "status : (success or failure)",
        "margin : (integer)",
        "is critical : (true or false)",
    ],
    invariants=["success when roll total ≥ DC; failure when below"],
    x=C2, y=R1)

R2 = 390
create_class_cell(root, "Graded Check Result",
    properties=[
        "degree : (1–4)",
        "resulting condition : Condition",
    ],
    invariants=[
        "base 1; +1 per 5 pts margin; max 4",
        "if is critical, increase degree by one",
        "condition determined by degree and effect's set",
    ],
    x=C2, y=R2)

create_class_cell(root, "Condition",
    properties=["condition name", "game modifier : Game Modifier"],
    x=C3, y=R2, imported_from="Condition")

R3 = 560
create_class_cell(root, "Opposed Check",
    properties=["opponent : Character"],
    operations=["difficulty class : Trait, Check Result"],
    invariants=[
        "DC from opposing character's roll total",
        "tie-break: higher trait bonus; then d20",
        "passive: DC = opposing trait modifier + 10",
    ],
    x=C0, y=R3)

create_class_cell(root, "Character",
    properties=["traits : Trait", "imposed conditions : Imposed Conditions"],
    x=C2, y=R3, imported_from="Character Construction")

R4 = 730
create_class_cell(root, "Routine Check",
    operations=["roll total"],
    invariants=[
        "substitutes 10 for d20; modifiers still apply",
        "some traits expand routine situations",
        "if routine total < DC, may still roll normally",
    ],
    x=C1, y=R4)

create_class_cell(root, "Team Check",
    properties=["helpers : Character"],
    operations=[
        "perform check : Check, Difficulty Class, Check Result",
    ],
    invariants=[
        "each helper runs perform check vs DC 10 first",
        "1–2 successes → +2; 3+ → +5; failure → −2",
        "only leader's roll total determines outcome",
    ],
    x=C2, y=R4)

# --- Edges ---
edge(root, "Check", "Trait", "association")
edge(root, "Check", "Difficulty Class", "association",
     exit_x=1.0, exit_y=0.3, entry_x=0.0, entry_y=0.5)
edge(root, "Check", "Check Result", "association",
     exit_x=1.0, exit_y=0.7, entry_x=0.0, entry_y=0.5)

edge(root, "Graded Check Result", "Check Result", "inheritance")
edge(root, "Graded Check Result", "Condition", "association")

edge(root, "Opposed Check", "Check", "inheritance-orthogonal",
     exit_x=0.5, exit_y=0.0, entry_x=0.2, entry_y=1.0)
edge(root, "Routine Check", "Check", "inheritance-orthogonal",
     exit_x=0.5, exit_y=0.0, entry_x=0.5, entry_y=1.0)
edge(root, "Team Check", "Check", "inheritance-orthogonal",
     exit_x=0.25, exit_y=0.0, entry_x=0.8, entry_y=1.0)

edge(root, "Opposed Check", "Character", "association",
     exit_x=1.0, exit_y=0.3, entry_x=0.0, entry_y=0.5)
edge(root, "Team Check", "Character", "association",
     exit_x=0.5, exit_y=0.0, entry_x=0.5, entry_y=1.0)


# ═══ PAGE 3: Condition ════════════════════════════════════════════════════════
#
# Layout: separate clusters to minimize long crossings.
#
#   R0: [Combined(C0)]  [Condition(C1)]   [Cond Source(C2)]
#   R1: [Game Mod(C0)]  [Imposed Cond(C1)]
#   R2: [Trait(C0)]     [Character(C1)]
#   R3: [Imposed Conds(C0)]
#   R4: [Effect(C1)]    [Applied Effect(C2)]   [Check(C3)]
#   R5:                 [Graded CR(C2)]

add_page(mxfile, "Condition")
_, root = get_page(mxfile, "Condition")

R0 = 40
create_class_cell(root, "Combined Condition",
    properties=["constituent conditions : Condition"],
    invariants=["each constituent superseded/resolved independently"],
    x=C0, y=R0)

create_class_cell(root, "Condition",
    properties=[
        "condition name : (dazed, stunned, impaired, ...)",
        "game modifier : Game Modifier",
        "supersedes : Condition",
        "superseded by : Condition",
    ],
    invariants=["supersession chain navigable through condition data"],
    x=C1, y=R0)

create_class_cell(root, "Condition Source",
    properties=["source : (power effect name, attacker ref, or event)"],
    invariants=["shared source → same-source supersession rules"],
    x=C2, y=R0)

R1 = 240
create_class_cell(root, "Game Modifier",
    properties=["applies to : Trait", "amount : number"],
    x=C0, y=R1)

create_class_cell(root, "Imposed Condition",
    properties=[
        "applied condition : Condition",
        "active status : (active or inactive)",
        "imposing source : Condition Source",
        "blocking condition : Imposed Condition",
    ],
    invariants=[
        "only active condition applies its modifier",
        "different-source less-severe → inactive while blocked",
    ],
    x=C1, y=R1)

R2 = 450
create_class_cell(root, "Trait",
    properties=["purchased rank", "effective rank"],
    x=C0, y=R2, imported_from="Trait")

create_class_cell(root, "Character",
    properties=[
        "traits : Trait",
        "applied effects : Applied Effect",
        "imposed conditions : Imposed Conditions",
    ],
    operations=["make check : Check, Trait"],
    x=C2, y=R2, imported_from="Character Construction")

R3 = 600
create_class_cell(root, "Imposed Conditions",
    properties=["applied conditions : Imposed Condition"],
    operations=[
        "apply new condition : Condition, Condition Source, Imposed Condition",
        "enforce on check : Check",
        "reveal blocked condition : Imposed Condition",
        "track dying fortitude progress : Check Result",
    ],
    invariants=[
        "same-source more severe replaces; less severe ignored",
        "different-source more severe supersedes regardless",
        "different-source less severe added inactive",
    ],
    x=C0, y=R3)

R4 = 860
create_class_cell(root, "Effect",
    properties=["effect rank : (integer)"],
    operations=["resist : Character, Trait, Graded Check Result"],
    invariants=["resistance check DC = 10 + effect rank"],
    x=C0, y=R4, imported_from="Power")

create_class_cell(root, "Applied Effect",
    properties=[
        "effect : Effect",
        "imposed conditions : Imposed Condition",
        "is ongoing : (active or ended)",
    ],
    operations=["resist : Character, Trait, Graded Check Result"],
    invariants=[
        "knows which imposed conditions it created",
        "when ended, removes all imposed conditions it created",
        "on resist success → ends; on failure → persists",
    ],
    x=C1, y=R4)

create_class_cell(root, "Check",
    properties=["using trait : Trait"],
    x=C3, y=R4, imported_from="Check")

R5 = R4 + 240
create_class_cell(root, "Graded Check Result",
    properties=["degree : (1–4)", "resulting condition : Condition"],
    x=C1, y=R5, imported_from="Check")

# --- Edges ---
edge(root, "Combined Condition", "Condition", "association",
     exit_x=1.0, exit_y=0.5, entry_x=0.0, entry_y=0.5)
edge(root, "Condition", "Game Modifier", "association",
     exit_x=0.0, exit_y=1.0, entry_x=0.5, entry_y=0.0)
edge(root, "Game Modifier", "Trait", "association",
     exit_x=0.5, exit_y=1.0, entry_x=0.5, entry_y=0.0)
edge(root, "Imposed Condition", "Condition", "association",
     exit_x=0.5, exit_y=0.0, entry_x=0.5, entry_y=1.0)
edge(root, "Imposed Condition", "Condition Source", "association",
     exit_x=1.0, exit_y=0.25, entry_x=0.5, entry_y=1.0)
edge(root, "Imposed Conditions", "Imposed Condition", "composition",
     exit_x=0.75, exit_y=0.0, entry_x=0.0, entry_y=1.0)
edge(root, "Imposed Conditions", "Check", "dependency-orthogonal",
     exit_x=1.0, exit_y=0.5, entry_x=0.5, entry_y=0.0)
edge(root, "Character", "Imposed Conditions", "composition",
     exit_x=0.0, exit_y=1.0, entry_x=0.5, entry_y=0.0)
edge(root, "Character", "Applied Effect", "composition",
     exit_x=0.5, exit_y=1.0, entry_x=0.5, entry_y=0.0)
edge(root, "Applied Effect", "Effect", "association",
     exit_x=0.0, exit_y=0.5, entry_x=1.0, entry_y=0.5)
edge(root, "Applied Effect", "Imposed Condition", "association",
     exit_x=0.25, exit_y=0.0, entry_x=0.25, entry_y=1.0)
edge(root, "Applied Effect", "Graded Check Result", "association",
     exit_x=0.5, exit_y=1.0, entry_x=0.5, entry_y=0.0)

# ═══ Save and Audit ══════════════════════════════════════════════════════════
save_drawio(OUTPUT, mxfile)
print(f"Saved: {OUTPUT}\n")
print(audit_diagram_report(str(OUTPUT)))
