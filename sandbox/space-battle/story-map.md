---
fidelity: discovery
artifact: story-map
format: md
section: body
---

# Story Map — Space Battle: TIE Fighter vs X-wing Combat Simulator

**Sources / context:** user request, 2026-10-23 — "a Star Wars TIE fighter vs X-wing combat simulator". No other source exists yet, so every node below is **intended** (evidence: user request only). Mechanics that set the two craft apart (X-wing deflector shields and proton torpedoes; TIE fighter speed and agility without shields) are **inferred** from the Star Wars setting and need confirmation.

**Decisions:** 2026-10-23 — a person flies one starfighter; every other starfighter is flown by an AI Pilot (user answer to open question 1).
2026-10-23 — the battle is 2D and turn-based (user answer to open questions 2 and 3).
2026-10-23 — starfighters act one at a time each turn, fastest first: when a starfighter's activation comes up, its pilot commits orders and the Simulation Engine resolves that starfighter's movement and fire before the next one acts (user answer to the turn-order question).
2026-10-23 — Adjust Throttle, Maneuver Starfighter, Route Reactor Power and Lock Target stay as separate **system stories**: the Pilot or AI Pilot sets them in Commit Activation Orders, and the Simulation Engine applies each one with its own mechanics (user ruling on validate failure 5).
2026-10-23 — Fire Laser Cannons is also a system story: the pilot names the laser target in Commit Activation Orders, and the Simulation Engine fires after movement (user approved the scenario validate fix).

**Actors:** Commander (sets up and watches a battle), Pilot (the person flying one starfighter), AI Pilot (flies every starfighter not flown by a person), Simulation Engine (advances time and resolves physics and combat).

---

# (E) Simulate Starfighter Dogfight
    ## (E) Set Up Engagement
        ### (S) Commander --> Choose Squadron Composition
        ### (S) Commander --> Configure Battle Arena
        ### (S) Commander --> Deploy Starfighters
        ### (S) Commander --> Launch Engagement
    ## (E) Pilot Starfighter
        ### (S) Simulation Engine --> Adjust Throttle
        ### (S) Simulation Engine --> Maneuver Starfighter
        ### (S) Simulation Engine --> Route Reactor Power
        ### (S) Simulation Engine --> Order Starfighter Activations
        ### (S) Pilot --> Commit Activation Orders
        ### (S) Simulation Engine --> Resolve Starfighter Movement
    ## (E) Exchange Fire
        ### (S) Simulation Engine --> Lock Target
        ### (S) Simulation Engine --> Fire Laser Cannons
        ### (S) Pilot --> Launch Proton Torpedo
        ### (S) Simulation Engine --> Resolve Shot Hit
    ## (E) Resolve Combat Damage
        ### (S) Simulation Engine --> Absorb Hit With Deflector Shields
        ### (S) Simulation Engine --> Damage Hull
        ### (S) Simulation Engine --> Disable Subsystem
        ### (S) Simulation Engine --> Destroy Starfighter
    ## (E) Pilot AI Starfighters
        ### (S) AI Pilot --> Select Target
        ### (S) AI Pilot --> Pursue Target
        ### (S) AI Pilot --> Evade Pursuer
        ### (S) AI Pilot --> Break Off Engagement
    ## (E) Conclude Engagement
        ### (S) Simulation Engine --> Determine Engagement Victor
        ### (S) Commander --> Report Battle Statistics
        ### (S) Commander --> Pause Engagement
        ### (S) Commander --> Restart Engagement

---

## Walking skeleton

One X-wing flown by the Pilot vs one TIE fighter flown by an AI Pilot, in an empty arena:
Deploy Starfighters → Launch Engagement → Order Starfighter Activations → Adjust Throttle → Maneuver Starfighter → Commit Activation Orders → Resolve Starfighter Movement → Pursue Target → Fire Laser Cannons → Resolve Shot Hit → Damage Hull → Destroy Starfighter → Determine Engagement Victor.

Later increments: squadrons (Choose Squadron Composition), shields and power (Route Reactor Power, Absorb Hit With Deflector Shields), torpedoes and target lock, subsystem damage, AI evasion and break-off, then statistics and pause/restart.

---

## Scope boundary

**In scope:** starfighter-vs-starfighter combat between X-wings and TIE fighters, set up by a Commander, flown by AI Pilots and optionally a person, resolved by the simulation, ending in a victor.

**Out of scope (until requested):** capital ships and other craft (Y-wing, TIE Interceptor, Star Destroyer), campaigns and pilot progression, multiplayer over a network, terrain such as asteroid fields or trench runs, audio.

## Open questions

1. ~~Does a person fly a starfighter?~~ Resolved: yes, one starfighter (see Decisions). Open: can the Pilot choose X-wing or TIE fighter?
2. ~~2D or 3D?~~ Resolved: 2D. Maneuver Starfighter means changing heading on a plane.
3. ~~Real-time or turns?~~ Resolved: turn-based, one starfighter at a time, fastest first. Open: is "fastest" the craft's top speed or its current throttle, and how are ties broken?
4. Is there a screen (browser, desktop) or is it headless with a report?
5. Confirm the craft differences: X-wing has shields and proton torpedoes; TIE fighter has none but is faster and turns tighter.
