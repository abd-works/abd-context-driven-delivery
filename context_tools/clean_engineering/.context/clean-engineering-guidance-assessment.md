# Clean Engineering Guidance Assessment

## Purpose

Assess `context_tools/clean_engineering/clean_engineering.md` against the rules and concrete artifacts in `C:\dev\paradise-mobile\pml-domainmodel\domain`, without changing the Clean Engineering guidance.

The assessment separates:

- shared rules that Paradise makes more precise;
- missing rules that can become shared guidance;
- project conventions that should remain in Paradise;
- contradictions that must be resolved before rules are promoted; and
- structural and editorial problems in the current shared guidance.

## Sources Reviewed

- `C:\dev\abd-context-driven-delivery\context_tools\clean_engineering\clean_engineering.md`
- Clean Engineering templates, testing guidance, class-model Draw.io guidance, and companion tool behavior
- `C:\dev\paradise-mobile\pml-domainmodel\domain\AGENTS.md`
- Paradise `domain-model.md` and `bounded-context-map.md`
- Paradise module diagrams and TypeScript transcriptions under `domain/`
- `C:\dev\abd-context-driven-delivery\rules\writing-guidelines.md`

## Executive Assessment

The shared Clean Engineering guidance already provides strong foundations: one-way dependencies, domain vocabulary, deep modules, behavior on the object that owns the state, explicit collaborators, relationship kinds, narrow public interfaces, and production behavior without empty implementations.

The Paradise domain work adds tested detail in areas the shared model guidance barely covers:

1. Repositories are typed collections that own aggregate lifecycle.
2. Another system is reached through a named service interface rather than modeled as a domain repository.
3. A domain wrapper may know the external system type, but the external system type must not know the domain.
4. Model modules inherit their names and boundaries from the partition artifact.
5. State-changing operations return the resulting record or a named failure.

These principles are useful beyond Paradise. The PML system names, module assignments, Draw.io file workflow, and vendor-specific relationship rules are not.

The shared guidance also needs repair before new rules are added. It contains missing template references, references to sections that do not exist, language-specific model rules presented as universal rules, and unclear distinctions between domain objects and external-system access interfaces.

## Existing Rules To Strengthen

### `put-logic-on-the-owning-resource`

**Shared source:** `clean_engineering.md:93,113`

**Paradise source:** `domain/AGENTS.md:10,76`

The shared rule asks which object owns the data. Paradise adds three practical traps: a route name, the actor named in a Story, and the object used in Given do not determine operation ownership.

**Recommendation:** State that an operation belongs to the object that owns the invariant. Names used by transport routes, screens, or Story actors do not move that operation to another object. Include one neutral example where a route named after a customer still invokes an operation owned by a cart.

### `do-not-invent-parallel-object-models`

**Shared source:** `clean_engineering.md:137`

**Paradise source:** `domain/AGENTS.md:14-15,85-86`; examples in `domain-model.md:135,689,790,1244,1291,1408`

The shared rule says to wrap or extend live objects. Paradise clarifies the direction of knowledge: the domain wrapper knows which external type it represents, while the external-system type exposes no domain types and no reverse reference.

**Recommendation:** Add this direction to the shared rule. A domain wrapper may represent an external type; the external type must remain independent of the domain model.

### `use-property-not-accessor`

**Shared source:** `clean_engineering.md:115`

**Paradise source:** `domain/AGENTS.md:19`

The shared rule assumes Python `@property` and setters. The portable design is that named properties expose state and encapsulate changes that can be expressed as assigning one property. Explicit `getX`, `setX`, and calculated UI-state accessors are not the domain interface. Use an operation only when the behaviour cannot be expressed truthfully as a property change.

**Recommendation:** Rewrite this rule without language syntax. Use named properties for state and for changes whose validation and invariants can remain inside that property. Use an operation when the behaviour coordinates several values, collaborators, or lifecycle steps and cannot be represented as one property assignment. Put `@property`, setters, and language idioms in language-specific guidance.

### `limit-operation-parameters`

**Shared source:** `clean_engineering.md:122`

**Paradise evidence:** `domain-model.md:305,557,1073`

The shared preference for zero to two parameters is useful for domain operations, but Paradise contains legitimate external patch and integration operations with three or more values. One case correctly promotes related data into `PaymentCharge`; others mirror the record expected by another system.

**Recommendation:** Keep zero to two as a domain-operation design test, not an absolute limit. Promote cohesive domain values to an object. Permit an external-system operation to accept the explicit record or fields required by the verified external contract when combining them would hide that contract.

### Avoiding invented `Service` classes

**Shared source:** `clean_engineering.md:91`

**Paradise source:** `domain/AGENTS.md:16`; examples in `domain-model.md:211,288,1101`

The shared guidance rejects `Manager`, `Service`, `Helper`, and `Processor` classes that take behavior away from the object that owns it. Paradise also uses `Service` to name access to an external system. These are different designs.

**Recommendation:** Clarify that the rule rejects invented logic holders. A named interface to an external system is valid when it represents a real boundary and exposes that system's operations.

## Missing Rules To Add

### `repository-is-aggregate-collection`

**Paradise source:** `domain/AGENTS.md:17,21`; examples in `domain-model.md:67-90,623-643,792-811`

A repository represents a typed collection of one aggregate root. Its collection property has the root's multiplicity; a singular reference is not a substitute for the collection.

**Recommended `ddd-building_blocks` rule:** Model a repository as a typed collection of one aggregate root. Show collection multiplicity explicitly, because a singular reference describes one loaded object rather than the root's persistence boundary.

### `repository-owns-aggregate-lifecycle`

**Paradise source:** `domain/AGENTS.md:22,83`

An aggregate instance does not create or load itself. Its repository owns creation, lookup, loading, and persistence for that root.

**Recommended `ddd-building_blocks` rule:** Put creation and loading of an aggregate root on its repository. Keep behavior that changes an existing aggregate on the aggregate itself, because lifecycle lookup and domain behavior have different owners.

### `external-system-access-is-a-service-interface`

**Paradise source:** `domain/AGENTS.md:16,52`; examples in `domain-model.md:630,799`

Paradise separates the domain collection from the external system. A domain repository holds its aggregate collection and collaborates with an external-system interface. The external interface has operations, not a collection of domain roots.

**Recommended `ddd-building_blocks` rule:** Represent access to another system with a named service or gateway interface. Let the domain repository hold the domain aggregate collection and call that interface when persistence or retrieval crosses the system boundary, because the external system is not the domain collection.

### `model-modules-follow-the-partition`

**Paradise source:** `domain/AGENTS.md:9,80`; module headings in `domain-model.md`

Paradise's model headings come directly from its bounded-context map. The shared model template has module headings but does not say where their names originate.

**Recommended shared rule:** Use the partition artifact's module names and boundaries as the model's top-level modules. Change the partition before changing a boundary in the model, because otherwise the two artifacts describe different designs.

### `one-canonical-model-document`

**Paradise source:** `domain/AGENTS.md:5,12,79`

Paradise keeps the public class model in one document and rejects companion files that restate it. The shared code guidance rejects parallel documents, but model guidance does not state the same constraint.

**Recommended shared rule:** Keep all modules for one model artifact in one canonical model document. Link diagrams and code to it rather than restating its classes in another design document, because parallel models become inconsistent.

This rule should not require one model document for an entire repository. Its scope is one model artifact or one modeled system, as defined by the current work.

### `state-change-returns-record-or-named-failure`

**Paradise source:** `domain/AGENTS.md:19`; examples in `domain-model.md:453-465,1069`

Paradise models a state-changing operation as returning the resulting record or a named failure value. The shared guidance explains exceptions and ordinary empty results but does not define model-level failure results.

**Recommended shared rule:** Make a state-changing operation return the resulting record or a named failure. Name the failure after the rule that rejected the change, then decide at code fidelity whether that model result is represented by a result type or a domain exception.

### `catalog-has-an-evaluation-operation`

**Paradise source:** `domain/AGENTS.md:24,87`; examples in `domain-model.md:137,195-210,376-396`

Paradise distinguishes a catalog of rules from the operation that evaluates those rules. The catalog data alone does not implement the behavior.

**Recommended shared rule:** Let a catalog hold named rules and give the catalog or owning aggregate an operation that evaluates them and returns the unmet rules. This keeps rule data and rule execution explicit.

The scenario-step and assertion parts of the Paradise rule belong in Stories guidance rather than the class-model rule.

## Project Rules To Keep In Paradise

Do not copy these into shared guidance as written:

- Vendor names and topology: Mavenir, Cognito, Amplify, Twilio, Zendesk, Persona, Vouchera, FAC, Apple, and GrowthBook.
- The exact module list and ownership assignments for Customer, KYC, Cart, Plans, Numbers and SIMs, Porting, Payments, Billing, Subscription, and Care.
- `## Paradise`, `## Mavenir`, and `## System` subsections.
- The project-specific `PortalGateway` slices.
- One named Draw.io file per module and the rule for closing an open Draw.io tab after an external write.
- Exact Draw.io colors, borders, and named module examples where the shared Draw.io template already owns notation.
- The worktree instruction and local source paths.
- One-customer-type and one-epic-at-a-time constraints.
- PML workarounds and manually tracked process exceptions.
- Per-module TypeScript transcription files.

These conventions may remain strong project rules. They do not describe every domain model.

## Paradise Contradictions To Resolve Before Promotion

### Duplicate repository rule

`domain/AGENTS.md:17` and `domain/AGENTS.md:21` define `repository-is-aggregate-collection` twice. The second version includes system collections that the model does not contain, while the first correctly distinguishes services from collections.

**Recommendation:** Keep one canonical rule. Retain explicit collection multiplicity and the distinction between aggregate repositories and external-system services. Remove stale system repository examples.

### Stale `repository-per-responsible-system`

`domain/AGENTS.md:84` says several external systems each have a repository, but `domain-model.md` models Paradise repositories collaborating with services instead.

**Recommendation:** Remove or rewrite the watch entry to point to the canonical repository and service rules.

### Presentation details in the domain model

`domain/AGENTS.md:25,27` excludes colors, glyphs, button state, and keystroke timing. `domain-model.md:611-615,1050-1051,1079-1084` still contains UI wording and labels.

**Recommendation:** Decide whether exact copy is domain data owned by a modeled concept or presentation detail. Keep it only when scenarios require the exact value and the domain object owns it; otherwise move it to UX artifacts.

### Repeated product-order operation

`PortalGateway.createProductOrder` appears with different detail at `domain-model.md:743-746` and `domain-model.md:1458-1475`; related orchestration is repeated at `domain-model.md:546-556`.

**Recommendation:** Choose one owning module and one canonical operation. Other modules should name their collaboration with that operation instead of copying its steps.

### Stale paths and incomplete lists

`domain/AGENTS.md:3,9` names source paths that do not match the current repository layout. The external-service list at line 16 omits a service named elsewhere in the same file.

**Recommendation:** Correct the paths and derive watch entries from canonical rules rather than maintaining separate copies.

### Watch-list drift

`domain/AGENTS.md:74-90` restates many rules instead of pointing to them. Several restatements contain different examples or scope.

**Recommendation:** Keep the watch list, but let each item point to one canonical rule and describe only the recurring mistake.

## Shared Guidance Problems To Resolve First

### Missing language template

`clean_engineering.md:18,33,87` refers to `templates/clean_engineering-language.md`, but that file does not exist.

**Recommendation:** Create the template or remove the references and keep the complete language instructions in one existing artifact.

### Missing Interfaces section

`clean_engineering-sketch.md` and `strategies/separate factory.md` refer to an Interfaces section that does not exist in `clean_engineering.md`.

**Recommendation:** Add a short Interfaces subsection under model guidance or update the references to the existing interface guidance.

### References to absent sections

`clean_engineering.md:33,47` tells the reader not to use `## Sketching` and `## Templates`, but those sections are absent.

**Recommendation:** Remove those names from the stop-reading instructions unless the sections are restored.

### Incorrect H1

`clean_engineering.md:1` is `# Contexts`. `clean_engineering.py` contains a comment that relies on that heading.

**Recommendation:** Rename the heading to `# Clean Engineering` and update the companion code or tests that expect the old heading in the same change.

### Model formats are under-described

`clean_engineering.md:81` presents Python as the model default, but the tool also has Markdown and Draw.io class-model channels. Paradise uses Markdown plus module diagrams.

**Recommendation:** Name the supported model channels and what each produces. Keep language syntax in templates and language guidance.

### Broken language-tools link

`clean_engineering.md:150` places Markdown link syntax inside code formatting and uses a root-relative path.

**Recommendation:** Use a working repository-relative Markdown link.

### Undefined scaffold rules

`clean_engineering.md:51` invokes `one-way-deps` and `domain-nouns-only`, but neither appears in the canonical module rule list.

**Recommendation:** Define the rules once or make the scaffold instruction refer to the actual canonical rule names.

### Writing and consistency defects

The document contains spelling and grammar defects, including `rigourous`, `while they exists`, `misunderstodd`, `cayse`, `Dependebcues`, and `propery`. It also has inconsistent heading names and a broken sentence at `clean_engineering.md:17`.

**Recommendation:** Complete one editorial pass under `rules/writing-guidelines.md`. Keep each rule as a named practice, a positive instruction, and a short reason. Replace vague metaphors with the concrete dependency or maintenance problem.

## Recommended Improvement Order

1. Repair missing references, absent sections, the broken H1 dependency, the language-tools link, undefined scaffold rules, and editorial defects.
2. Clarify the operation-parameter rule, external-system `Service` distinction, and language-neutral property rule.
3. Add repository collection, aggregate lifecycle, and external-system access rules to `ddd-building_blocks`.
4. Add the direction-of-knowledge rule to `clean_engineering-model`.
5. Add model-from-partition and canonical-model-document rules.
6. Add record-or-named-failure and catalog-evaluation rules.
7. Document Markdown, code, and Draw.io model channels without moving template mechanics into rules.
8. Repair the Paradise duplicate rules, stale paths, presentation conflict, and repeated product-order operation separately.

## Bottom Line

Paradise demonstrates several missing model practices on a large working artifact. Its Repository and external-system access rules belong in `ddd-building_blocks`; its model-boundary, external dependency direction, and failure-result rules belong in `clean_engineering-model` after they are rewritten without PML names.

The shared document should first become internally consistent and explicit about its formats and references. Paradise's topology, file workflow, and vendor-specific modeling decisions should remain project guidance, and its duplicated or stale rules should be corrected before their wording is reused.
