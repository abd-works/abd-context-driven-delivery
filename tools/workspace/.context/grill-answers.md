# Grill Answers

### Work Session Rule storage

Work Session rules are one flat tagged RulesCollection under `.sessions/{name}/`, not a mirrored practice tree and not patches to practice markdown. Each rule carries optional guideline and fidelity tags. Inject filters by the current guideline plus fidelity, and also takes Shared: guideline-only, or neither tag (global).

### WorkSessionGuidance is PracticeGuidance

WorkSession owns WorkSessionGuidance. WorkSessionGuidance has the same interface as PracticeGuidance: format, fidelities, Rule Collections, templates, guidance. WorkSessionRule lives inside a RulesCollection on that guidance (shared or a fidelity’s) — same RulesCollection type unless capture or prominence needs extra operations. For now only rules and guidance are in play; templates and unused pieces wait. Guideline and fidelity are placement on the guidance, not tags on the rule.

### WorkSessionGuidance is a practice dictionary

WorkSessionGuidance is a proxy collection, not itself a PracticeGuidance. It holds a dictionary of PracticeGuidance keyed by practice. Each entry is that practice’s project guidance and owns its own RulesCollection (plus the rest of the PracticeGuidance surface). A WorkSessionRule sits in the matching practice’s collection.

### WorkSessionPracticeGuidance plus turn aggregate

The dictionary value is WorkSessionPracticeGuidance, not PracticeGuidance. WorkSessionGuidance stays a collection of those children. Aggregation for the current turn belongs on WorkSessionGuidance: integrate each child’s rules and guidance with the mirrored practice, same-slug session rule overrides the practice rule. Do not make each Guidance property a dict keyed by practice — that splits one child’s overrides across parallel bags and changes the type of rules/format.

### Priority relevant context bands

Bands are failure windows over WorkSessions, not “this file vs last file.” Priority = failed in the current session or last N_priority sessions (this-run fails sort to the top of that band, then session ★). Relevant = failed in last N_relevant sessions minus priority. Context = last N_context sessions or all, minus the two tighter bands. Each band has a configurable inclusion of examples | body | slug | omit. Defaults: priority=examples with a count cap, relevant=body, context=slug. Nested windows so a rule sits in one band.

### Relevancy lives on RulesCollection

priorityWindow, relevantWindow, contextWindow, inclusions, and priority/relevant/context live on RulesCollection — the same collection PracticeGuidance already uses. WorkSessionGuidance only holds practices and aggregate(turn). Relevancy is a basic RulesCollection capability; sparse catalogs still work, they just have little to band.

### Integrated set on WorkSessionPracticeGuidance

WorkSessionGuidance does not aggregate practice rules onto a turn. Each WorkSessionPracticeGuidance determines the integrated set: pass-through format, fidelities, and templates from the mirrored PracticeGuidance; session rules overlay that practice’s rules with same-slug override. Lookup creates the child for a practice; scaffold is gone. Banding stays on the integrated RulesCollection.

### WorkSessionRulesCollection add and inject

Capture and inject are WorkSessionRulesCollection operations, a subtype of RulesCollection. add(rule, mistake, correction) tags the rule with guidance and fidelity, attaches the example, stars it, and inserts it at the top of the work-guidelines rules section when it has the highest star. inject_rules looks at the practice rules being injected this turn, matches session rules by that guidance plus fidelity, and reorders. Each WorkSessionRule holds guidance and fidelity. No aggregated PracticeGuidance graph. A new generate is an announced Turn (/turn).

### add takes a WorkSessionRule

WorkSessionRulesCollection.add takes a WorkSessionRule. No matching base rule → insert it new. Matching base rule → add the example and raise star (priority). Each example has a mistake and a correction. inject_rules stays the hook reorder; it is not a second write path.

### Unmatched add and inclusion branches

add takes a WorkSessionRule. No matching base rule creates a new entry; a match adds the example and raises star. Band windows and inclusion (examples | body | slug | omit) live on WorkSessionRulesCollection. Changing a window or inclusion changes inject detail for the same rules; the collection still holds them.

### New, practice-wide, and global rules

A WorkSessionRule may have guidance+fidelity, guidance only (practice-wide), or neither (global). add with no matching base rule mints a new rule, tagged from the generate in play or left untagged. inject_rules includes practice-wide and global rules in the same star order as fidelity-specific matches — empty guidance or fidelity still matches the current generate.

### Inclusion counts, injection detail, exclude age

Band membership is turn-count inclusion: priorityInclusion, relevantInclusion, contextInclusion. exclude is a turn age (for example 5) — a rule that last failed that many turns ago is not injected and stays on the collection. Each band has an injection detail (examples, body, or slug). There is no omit inclusion.

### Add on the work session; turn increments without git

Turn.record_correction and record_mistake are deferred (star as to be implemented). Capture goes to workSession.guidance.rules.add. /turn is WorkSession.turn — increment turn age for inclusion and exclude, no GitRepo.

### Completed turns as commit SHA; rule holds turn id

WorkSession.completedTurns holds commit SHAs of finished turns. WorkSession.turn still commits and appends that SHA. WorkSessionRule.turn is that turn id so inclusion is by turn identity, not only this/last turn. Corrections and mistakes stay on WorkSessionGuidance.rules.add — not on Turn.

### Configuration change re-bands on next inject

Changing priorityInclusion, relevantInclusion, contextInclusion, exclude, or a band's injection detail does not remove rules from the collection. The next inject_rules re-bands and re-renders against completed turn age using the new settings.

