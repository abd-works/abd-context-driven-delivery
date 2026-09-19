# Practice Guidance — class model (model fidelity)

Markdown channel for the same types as `practice-guidance-model.py`. Live names: *PracticeGuidance*, *FidelityGuidance*, *Markdown*, *Render*.

**Out of scope:** Diagnose companion, `ce()` on the practice, production render bodies, moving Stories/UX/CE parse implementations (folder layout only).

---

## Language companion

A *PracticeGuidance* loads *FidelityGuidance* children from the practice markdown. Each fidelity owns **Stage**, **Default format**, and an optional **Clean Engineering** fidelity companion. Callers convert artifacts through the *Render* action, which asks *PracticeGuidance.render*. Practices that own an artifact keep it under `model/` with one folder per format underneath. BDD and DDD have no `model/` formats; they render through the companion.

---

## PracticeGuidance : Guidance

PracticeGuidance(format, path, session, workspace, fidelity, stage)
------
fidelities: GuidanceCollection
format: str
	Invariant: constructor format overrides FidelityGuidance.default_format; omitted format uses the current fidelity default_format
	Invariant: never _fidelity_format_defaults
	Invariant: never ce()
formats: dict[str, type]
	Invariant: keys are format names; values are parse/render types in {practice}/model/{format}/
	Invariant: empty on BDD and DDD
	Invariant: never document/, diagram/, code/, or web/ as format parents
load_fidelities_from_markdown()
	Interaction:
		-> Markdown.fidelity_blocks
		-> Markdown.fidelity_stage
		-> Markdown.fidelity_format
		-> Markdown.fidelity_clean_engineering
		# resolve companion name against CleanEngineering.fidelities; miss or empty → null
guidance() -> str
	Interaction:
		-> fidelities.current
		# if current.clean_engineering is null, skip
		-> current.clean_engineering.instructions
render(format: str, content: str, source: str | None) -> dict
	Interaction:
		# formats empty and current.clean_engineering set
		-> current.clean_engineering.practice_guidance.render
		-> formats[source or self.format].parse
		-> formats[format].render

## FidelityGuidance : Guidance

FidelityGuidance(name, stage, default_format, practice_guidance, clean_engineering)
------
name: str
stage: str
default_format: str
	Invariant: from **Default format:** in this fidelity’s markdown block
practice_guidance: PracticeGuidance | None
fidelity: str
clean_engineering: FidelityGuidance | None
	Invariant: null → skip; set → a FidelityGuidance owned by CleanEngineering
	Invariant: Clean Engineering’s own fidelities stay null

## Markdown

------
fidelity_blocks(text: str) -> list[tuple[str, str]]
fidelity_stage(body: str) -> str
fidelity_format(body: str) -> str
	# **Default format:** ; first token is the channel name
fidelity_clean_engineering(body: str) -> str
	# **Clean Engineering:** modules|model|code; omit → empty

## Render : GuidanceAction

------
render(guidance: GuidanceArg, format: str, content: str) -> list
	Interaction:
		-> PracticeGuidance.render
