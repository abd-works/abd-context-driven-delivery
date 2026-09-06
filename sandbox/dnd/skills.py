"""Skills — ability-linked proficiencies and check modifiers."""

from __future__ import annotations

from enum import Enum

from sandbox.dnd.abilities import Ability, AbilityScores


class Skill(str, Enum):
    ACROBATICS = "acrobatics"
    ANIMAL_HANDLING = "animal_handling"
    ARCANA = "arcana"
    ATHLETICS = "athletics"
    DECEPTION = "deception"
    HISTORY = "history"
    INSIGHT = "insight"
    INTIMIDATION = "intimidation"
    INVESTIGATION = "investigation"
    MEDICINE = "medicine"
    NATURE = "nature"
    PERCEPTION = "perception"
    PERFORMANCE = "performance"
    PERSUASION = "persuasion"
    RELIGION = "religion"
    SLEIGHT_OF_HAND = "sleight_of_hand"
    STEALTH = "stealth"
    SURVIVAL = "survival"


SKILL_ABILITY: dict[Skill, Ability] = {
    Skill.ACROBATICS: Ability.DEXTERITY,
    Skill.ANIMAL_HANDLING: Ability.WISDOM,
    Skill.ARCANA: Ability.INTELLIGENCE,
    Skill.ATHLETICS: Ability.STRENGTH,
    Skill.DECEPTION: Ability.CHARISMA,
    Skill.HISTORY: Ability.INTELLIGENCE,
    Skill.INSIGHT: Ability.WISDOM,
    Skill.INTIMIDATION: Ability.CHARISMA,
    Skill.INVESTIGATION: Ability.INTELLIGENCE,
    Skill.MEDICINE: Ability.WISDOM,
    Skill.NATURE: Ability.INTELLIGENCE,
    Skill.PERCEPTION: Ability.WISDOM,
    Skill.PERFORMANCE: Ability.CHARISMA,
    Skill.PERSUASION: Ability.CHARISMA,
    Skill.RELIGION: Ability.INTELLIGENCE,
    Skill.SLEIGHT_OF_HAND: Ability.DEXTERITY,
    Skill.STEALTH: Ability.DEXTERITY,
    Skill.SURVIVAL: Ability.WISDOM,
}


def skill_modifier(
    skill: Skill,
    abilities: AbilityScores,
    *,
    proficiency_bonus: int = 0,
    proficient: bool = False,
    expertise: bool = False,
) -> int:
    """Ability modifier plus optional proficiency (double for expertise)."""
    base = abilities.modifier(SKILL_ABILITY[skill])
    if not proficient:
        return base
    bonus = proficiency_bonus * (2 if expertise else 1)
    return base + bonus
