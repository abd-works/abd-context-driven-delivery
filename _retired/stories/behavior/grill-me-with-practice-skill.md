# Grill Me — Practice Skill

## Activation

Invoke any practice skill with **"grill me"** to enter grill mode:

> `/abd-story-mapping grill me`  
> `/abd-domain-model grill me`  
> `grill me with abd-story-mapping`

When a skill is invoked **without** "grill me", it generates directly. Grill mode is opt-in. **If "grill me" was not in the invocation — stop reading this file.**

---

## Purpose

You are grilling to establish shared understanding at the **current fidelity level**. Your questions are shaped by what the practice skill at this perspective and fidelity needs as input. You validate that understanding by running the skill — the generated output confirms or reveals gaps. Stay focused at one fidelity level until it's resolved before moving deeper.

You must ask questions **one at a time**, waiting for feedback before continuing.

If a question can be answered by reading existing skill outputs or the codebase, read them instead of asking. Use `behavior/skill-index.md` output filenames to know what to look for.

---

## Where your questions come from

**[`reference/grill-me.md`](reference/grill-me.md)** in the active skill package — interview questions for this method. Read it in full when grill mode is active.

Do **not** use **`reference/input-traps.md`** for grilling — input traps are a silent pre-flight check in every run, not interview questions.

Skill **rules** — each FAIL example can suggest a follow-up question when output reveals a gap.

---

## Modes

**Default — cross-perspective (no flag):**  
Grill across all perspectives at the current fidelity level. When the user's answer touches domain, stories, UX, or architecture, follow that thread and reference what those peer skills have already produced (or surface the gap).

**Single-skill mode — `only` or `with <skill>`:**  
Stay inside the named skill. Do not navigate to peer perspectives.

> `/abd-story-mapping grill me only`  
> `grill me with abd-story-mapping only`

Use this when the user wants to sharpen one skill's input without bringing in other perspectives. Questions come only from the active skill's **`reference/grill-me.md`** and **`rules/`**. No cross-perspective surfacing.

---

## During the interview

### Check what already exists

Before asking the user anything, look at what's already been produced. Check `behavior/skill-index.md` for the output filenames at each perspective and fidelity level — scan for those files in the workspace. If something has been defined, don't re-ask. Reference it.

### Surface contradictions across perspectives *(default mode only)*

Every fact lives across domain, stories, UX, and architecture. When the user says something that conflicts with any of those — surface it. "The domain language defines Account as a billing entity, but you're describing it as a user profile — which is it?"

### Stress-test with concrete scenarios *(default mode only)*

When examining the ask, use the stories perspective at the current fidelity level to probe. Invent specific scenarios that force the user to be precise about boundaries between concepts — "What happens when a family member tries to view an account they don't own?" The answer either confirms existing stories cover it, or reveals a gap the story skills need to fill.

### Sharpen fuzzy language

When the user uses vague or overloaded terms, check if the domain skills have already pinned it down. If yes, reference it. If no, ask them to be precise — that gap signals the domain skill is needed.

---

## Generate-to-learn

You don't finish all questions before generating. Once you have enough shared understanding for the current perspective at the current fidelity level — run the skill, generate output, and show it to the user to validate your understanding. The output will surface what's still unresolved. Examine again. Iterate.

---

## Never

- Never pick the most likely option when multiple exist — present them.
- Never infer domain meaning from general knowledge — check skill outputs, code, or ask.
- Never skip a question because the answer seems obvious.
- Always say where your context came from.
- Never force a transition when detail is unresolved at the current fidelity level. Take a note, tag the gap to the story or concept, stay at the current level until the user says to move.
- Never generate plausible-sounding steps for a mechanism or behaviour you haven't confirmed with the user. If you don't know how something works, ask. "I don't know" is not a generation prompt — it is a question.
