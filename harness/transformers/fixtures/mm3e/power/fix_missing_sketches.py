#!/usr/bin/env python3
"""Fix missing domain sketch sections using a more robust insertion approach."""

MISSING_SKETCHES = {
    "power type": [
        "is the *category label* on every effect that governs which general rules apply",
        "classifies each effect into exactly one of six categories: Attack, Control, Defense, General, Movement, Sensory",
        "determines whether an effect requires an attack check, allows a resistance check, or is permanent",
        "Invariant: every effect belongs to exactly one power type; power type cannot be changed by modifiers",
        "Collaborates with: effect (carries the type label), modifier (extras may change behavior but not the official type)",
    ],
    "base cost": [
        "is the *unmodified power-point cost per rank* as printed in the rules for a specific effect",
        "is immutable — set at effect design time and cannot be changed by play or by modifiers",
        "seeds the modifier math: cost per rank = base cost + extras − flaws",
        "Invariant: base cost is always a positive integer ≥ 1 for every defined effect",
        "Collaborates with: effect (carries its base cost), modifier (adjusts from this baseline), cost per rank (derived value)",
    ],
    "cost per rank": [
        "is the *final modified cost per rank* paid for each rank of an effect after all modifier math is complete",
        "is computed as: base cost + (sum of per-rank extras) − (sum of per-rank flaws)",
        "drives the bulk of total power cost: effect cost = (cost per rank × ranks) + flat modifiers",
        "Invariant: cost per rank cannot drop below 1 pp/rank regardless of flaws applied",
        "Collaborates with: base cost (starting value), extra/flaw (modifiers applied), flat modifier (post-multiplication), rank (the multiplier)",
    ],
    "flat modifier": [
        "is a *fixed-point price adjustment* applied to the final total cost after per-rank cost × rank is computed",
        "adds (flat extra) or subtracts (flat flaw) a set number of points from the total, regardless of rank",
        "is applied last in the cost formula: (cost per rank × rank) + flat extras − flat flaws",
        "Invariant: flat modifiers cannot reduce total power cost below 1 power point",
        "Collaborates with: extra (flat extras add to total), flaw (flat flaws subtract), cost per rank (applied after multiplication)",
    ],
    "Blast (Damage, Ranged)": [
        "is *Damage with the Ranged extra already incorporated* — a common preconfigured combination, not a separate effect",
        "requires a ranged attack check vs. target Dodge; on hit, target makes Toughness check vs. DC 15 + rank",
        "applies damage conditions on failed checks using the standard four-degree damage table",
        "costs exactly 2 pp/rank (base Damage 1 + Ranged extra 1) — already factored in at acquisition",
        "Invariant: Blast is Damage with Ranged; it does not represent a distinct effect type in the rules",
        "Collaborates with: Damage (its base effect), Ranged extra (the preconfigured extra), Toughness (the resistance), attack check",
    ],
    "Enhanced Trait": [
        "is a *General effect* that temporarily raises an existing character trait above its normal base value",
        "requires the target trait to already exist on the character sheet; Enhanced Trait raises it further",
        "costs per rank equal to the target trait's own base cost per rank",
        "drops the enhanced trait to its base if the character cannot maintain the sustained effect",
        "Invariant: Enhanced Trait is subject to PL limits on the resulting combined total",
        "Collaborates with: the enhanced trait (the target), PL limits (the cap), sustained duration (the maintenance requirement)",
    ],
    "Luck Control": [
        "is a *Control effect* that manipulates the hero point economy for characters within perception range",
        "allocates each rank to one capability: spend a hero point for another, transfer a hero point, negate a hero point use, or force a re-roll",
        "triggers as a Reaction — activates in response to hero point-related events",
        "Invariant: each rank provides exactly one capability from the defined list; capabilities do not stack",
        "Collaborates with: hero point (the currency manipulated), perception range (the range requirement), Combat module (owns hero point mechanics)",
    ],
    "Mind Reading": [
        "is a *Sensory effect* that accesses a target's thoughts via an opposed mental check",
        "initiates contact with an opposed check (effect rank vs. target Will); degree of success determines depth",
        "grants access at four depths: degree 1 surface thoughts, degree 2 personal thoughts, degree 3 memories, degree 4 subconscious",
        "allows target a Will check at end of each of their turns; success breaks contact",
        "is sustained — contact ends if concentration is broken or the effect is not maintained",
        "Invariant: Mind Reading cannot directly harm the target — it extracts information only",
        "Collaborates with: Will (the resistance), perception range (the targeting requirement), sustained duration",
    ],
    "Move Object": [
        "is a *Control effect* that telekinetically lifts and moves objects or unwilling targets at ranged distance",
        "provides effective Strength = effect rank for all lifting and moving operations",
        "cannot directly damage targets as a primary action; can be used for disarm, grab, or trip at range",
        "allows targets to resist with Strength check vs. effect rank; inanimate objects do not resist",
        "is sustained — held objects or creatures fall if concentration is broken",
        "Invariant: Move Object cannot deal Damage as a primary action",
        "Collaborates with: effective Strength (= rank), grab/disarm/trip (combat applications), Strength check (target resistance), sustained duration",
    ],
    "Remote Sensing": [
        "is a *Sensory effect* that displaces the character's senses to a remote location within range",
        "costs 1–5 pp/rank based on number of sense types covered (same scale as Communication and Illusion)",
        "suppresses normal senses while active — the character perceives only through the displaced location",
        "marks the character as vulnerable (halved active defenses) while active",
        "Invariant: Remote Sensing suppresses normal senses; the character cannot perceive both locations simultaneously",
        "Collaborates with: sense type (the displaced senses), vulnerable condition (the use cost), range (determined by rank)",
    ],
    "Check Required": [
        "is a *flat flaw* that gates effect activation behind a successful skill or ability check",
        "costs −1 per rank of the effect",
        "sets check DC = 10 + extra ranks beyond base; natural 1 on the die always fails",
        "grants 1 effective rank per point exceeding the DC on a success",
        "Invariant: Check Required is in addition to any other checks the effect normally requires",
        "Collaborates with: skill check (the gate), DC (10 + extra ranks), flat modifier (the cost mechanism), effect rank (increased by exceeding DC)",
    ],
    "origin descriptor": [
        "is a *descriptor subtype* that identifies how the character came to have their powers",
        "covers origin categories: Accidental, Bestowed, Invented, Mutant, Training",
        "typically applies to the character's entire power set rather than individual powers",
        "Invariant: origin descriptor rarely has direct mechanical effects; it is primarily a narrative and GM-ruling tool",
        "Collaborates with: descriptor (its parent concept), power set (the scope it typically covers)",
    ],
    "source descriptor": [
        "is a *descriptor subtype* that identifies the energy or force a power draws upon to function",
        "covers source categories: Biological, Cosmic, Divine, Extradimensional, Magical, Moral, Psionic, Technological",
        "has direct mechanical significance — Nullify targeting 'magical effects' counters all powers with Magical source",
        "a power can have multiple source descriptors if it draws on more than one source",
        "Invariant: source descriptor determines Nullify and Immunity interactions more directly than origin descriptor",
        "Collaborates with: descriptor (its parent concept), Nullify (primary mechanical consumer), Immunity (secondary consumer)",
    ],
    "Alternate Effect": [
        "is a *variant effect in a Power Array* that can substitute for the primary effect at flat cost",
        "costs 1 flat point per Alternate Effect added to the Array",
        "must have a total cost (all extras, flaws, ranks included) ≤ the primary effect's total cost",
        "cannot be a permanent effect — permanent effects cannot be switched in/out",
        "Invariant: only one Alternate Effect (or the primary) can be active at a time",
        "Collaborates with: Array (the container), flat modifier (the cost mechanism), primary effect (the cost ceiling), mutual exclusivity rule",
    ],
    "Dynamic Alternate Effect": [
        "is a *variant of Alternate Effect* that can share power points with other Dynamic effects and operate simultaneously at reduced effectiveness",
        "costs 2 flat points per Dynamic Alternate Effect (the base effect costs 1 extra point to become dynamic)",
        "allows point reallocation among Dynamic effects once per turn as a free action",
        "operates at reduced effectiveness when sharing — combined allocation cannot exceed the Array pool total",
        "Invariant: Dynamic effects CAN operate simultaneously; standard Alternate Effects cannot",
        "Collaborates with: Array (the container), power points (shared resource), free action (reallocation mechanism), pool size (upper limit)",
    ],
}


def add_sketch_by_insertion(content, term_name, bullets):
    """Find the term's #### heading and insert Domain Sketch after Domain Language."""
    # Build pattern: look for the exact heading
    pattern = f"#### {term_name}\n"
    idx = content.find(pattern)
    if idx == -1:
        # Try with different line endings or trailing spaces
        print(f"  STILL MISSING: {term_name}")
        return content
    
    # Check already present
    if "#### Domain Sketch" in content[idx:idx+2000]:
        return content
    
    # Find #### References or #### Decisions made to insert before
    term_end = content.find("\n#### ", idx + 1)
    # But we want the one that comes AFTER Domain Language bullets
    search_start = idx + len(pattern)
    
    # Skip past #### Domain Language section
    dl_pos = content.find("#### Domain Language\n", search_start)
    if dl_pos == -1 or dl_pos > idx + 3000:
        # No Domain Language section found nearby; insert right after heading
        insert_pos = idx + len(pattern)
    else:
        # Find end of Domain Language bullets (next #### heading)
        after_dl = dl_pos + len("#### Domain Language\n")
        next_section = content.find("\n#### ", after_dl)
        if next_section != -1 and next_section < idx + 3000:
            insert_pos = next_section + 1  # After the \n
        else:
            insert_pos = idx + len(pattern) + 200  # Fallback
    
    # Build sketch text
    sketch = "\n#### Domain Sketch\n\n"
    sketch += "\n".join(f"- {b}" for b in bullets)
    sketch += "\n"
    
    return content[:insert_pos] + sketch + content[insert_pos:]


def main():
    path = r"c:\dev\mm3e-online-holistic\docs\power\power.md"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    for term_name, bullets in MISSING_SKETCHES.items():
        # Find the term and where to insert
        pattern = f"#### {term_name}\n"
        idx = content.find(pattern)
        if idx == -1:
            print(f"  NOT FOUND: {term_name!r}")
            # Show nearby content
            for alt in [f"#### {term_name.lower()}\n", f"#### {term_name}\r\n"]:
                alt_idx = content.find(alt)
                if alt_idx != -1:
                    print(f"    Found with alt pattern: {alt!r}")
            continue
        
        # Check already present
        term_block = content[idx:idx+3000]
        if "#### Domain Sketch" in term_block:
            print(f"  Already has sketch: {term_name}")
            continue
        
        # Find #### References within the term to insert before
        ref_pos = content.find("#### References\n", idx)
        dl_pos = content.find("#### Domain Language\n", idx)
        dec_pos = content.find("#### Decisions made\n", idx)
        
        # Determine next #### h4 after domain language
        if dl_pos != -1 and dl_pos < idx + 2000:
            after_dl = dl_pos + len("#### Domain Language\n")
            next_h4_after_dl = content.find("\n#### ", after_dl)
            if next_h4_after_dl != -1 and next_h4_after_dl < idx + 2000:
                insert_pos = next_h4_after_dl + 1
            elif ref_pos != -1 and ref_pos < idx + 2000:
                insert_pos = ref_pos
            else:
                insert_pos = after_dl
        elif ref_pos != -1 and ref_pos < idx + 2000:
            insert_pos = ref_pos
        else:
            insert_pos = idx + len(pattern) + 100
        
        sketch = "\n#### Domain Sketch\n\n"
        sketch += "\n".join(f"- {b}" for b in bullets)
        sketch += "\n"
        
        content = content[:insert_pos] + sketch + content[insert_pos:]
        print(f"  Added: {term_name}")
    
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print("\nDone.")


if __name__ == "__main__":
    main()
