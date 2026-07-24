# Grill Answers

### BDD placement in CDD stages

BDD is not a fifth discovery/explore lens. Add bdd alongside spec and engineer only
(child fidelities: behavior at spec, development at engineer). Same instruct path as
other concepts; discovery/explore menus stay stories + ddd + ux + clean_engineering.

### One sketch file grouped by theme

Single sketch file (engagement workspace .context/), not per-lens files. Group by
theme ? what ties the sketches (module / epic). Under each theme, place short sketches
of different types side by side so lenses stay close and comparable. Structure:
theme banner ? sketch ? sketch ? next theme. Types considered beside each other, not siloed.

### Theme kinds ? ask user with recommendation

A theme may be an epic, a module, a user goal (screens), an entire increment,
or any one of those. AI asks the user which theme kind to use for the next
cluster and leads with a recommendation grounded in stage and context.

### Default scopes by stage ? grill/sketch finer

Stage sets default scope for the run; grill and sketch work much finer-grained
inside that scope. discovery ? entire solution or large subsection of the solution;
explore ? increment or large subsection of the increment; spec and engineer ?
sub-epic-sized slice inside the solution/increment. Theme kind (epic/module/user-goal/
increment) is chosen inside that scope; AI recommends, user confirms.

### Sketch controls stage flow

The sketch also steers work flow: after a stage chunk, it records whether to
proceed to the next stage or do more at the same stage. AI recommends; user can
override. Flow decision lives in the one sketch file alongside theme clusters.

### When to recommend proceed ? views agree

Prefer proceed only when the views in play for the current scope agree with each
other (stories, domain, screens, structure ? and bdd at spec/engineer). If one
view still contradicts another or has an open blocker, recommend more at the same
stage. Avoid jargon like ripple-ready in the sketch; say views agree / still
disagree. User can override.

### Persistent action trail via richer TODOs in sketch

Action history lives in the one sketch file. Track work as TODO ? doing ? pass
#label (or skip #why) under flow/themes. When a theme cluster closes, move completed
pass lines into a bottom ## log keyed by stage / scope / theme so the top stays
readable and CDD does not lose the thread.

### Locked sketch ? implemented

Sketch locked. Implemented context_tools/cdd (BDD on spec/engineer, one-file theme
sketch with flow + TODO trail) and concise common/stages mapped to CDD context_tools.

### First increment ? Story ? CE imports

First structured link seam is Story ? clean_engineering example/object imports (epic/sub-epic/story Python importing helpers and example factories). UX annotations, shared CDD registry, and demo-story wrapper are later increments; story demo consumes these imports once they exist.

### Regeneration is conversion, not creation

Story Python (and other formats) are authored/created as the working representation. Regeneration/translateFrom is a conversion act between formats ? it does not define how stories are created, and must not drive the Story?CE import design. Import placement follows the authorship model in connected-context_tools.md (epic / sub-epic / rare story helpers), not a 'keep regeneratable files pure' rule.

### Lens blocks must use child sketch_template

CDD engagement sketch lens blocks (stories/ddd/ux/ce/bdd) are invalid if filled with free prose. Must call resolve_targets first and write each lens in that context's sketch_template notation. Fixed in cdd.md (lens-from-child-template + generate order), sketch-template.md, examples.md, and generate() now exposes resolve_targets.

### Import stack ? epic + sub-epic; story rare

Story?CE imports land at epic helper (shared) and sub-epic helper (scoped); story-level helper/class imports only when unique. Matches connected-context_tools.md authorship stack.

### CE surface ? example factories only

Story helpers import ExampleFactory / testable_class_factory (and example data they load). Fake/isolated/production/demo are factory outputs, not direct imports into the story tree. Typed CE modules and full class shapes are not the Increment 1 import surface.

### Factory bind ? methods on a named factory

Scenario/background examples bind via methods on a named factory object (e.g. CartFactory.cart_with_items()), not orphan module-level functions. Epic/sub-epic helpers import and expose those named factories; steps call factory methods.

### CE sketch gap ? generation variants unclear

User flagged cdd-sketch ce block (ExampleFactory / CartFactory / helpers): it does not show how the class is extended per generation (fake / isolated / production / demo). Need an explicit CE sketch of the generation variants relative to the interface surface before proceeding.

### Generation fills interface slots

Same interface (constructor, public api, internals, dependencies); generation chooses which slots are real ? fake (ctor+api), isolated (ctor+api+deps), production (all), demo (UI invoker wrap). Open: for a concrete app (e.g. pet store), what must authors extend/create for factories and fakes vs what the framework supplies.

### Grill discipline ? one question at a time

User requires one focused question per turn. Stop packing multi-part option essays.

### App factories by pattern ? no ExampleFactory base

PetFactory (and CartFactory, etc.) are generated plain classes by pattern ? named methods whose bodies call load/fill machinery. They do not extend ExampleFactory. Framework = generation pattern + load/fill (fake/isolated/?). App = generated named factory classes + interface + examples.

### Load/fill is a pattern ? not an ExampleLoader framework type

There is no ExampleLoader framework class. Load/fill + generation slots are a generation pattern applied when emitting app factory methods. Framework contribution is the pattern (and whatever generation machinery implements fake/isolated/?), not a runtime Loader type apps import.

### Per type artifacts ? interface + examples + factory

For a new app type (e.g. Pet), generation produces: Pet interface, class_examples data, and PetFactory with named methods shaped by the load/fill/generation pattern. No ExampleLoader type; no hand-written FakePet unless custom.

### Patterns documented as {parameter} then example

CE factory pattern in cdd-sketch uses {Type}Factory / {example_method} / {Type} + {example_key} + {generation}, followed by concrete Pet/Cart example. No ExampleLoader type.

### Examples are multi-type bundles per example_key

class_examples[{Type}][{example_key}] is wrong ? a factory method may load multiple example classes (e.g. Cart + Product). Examples are keyed by example_key as a bundle of types, not one examples property per Type.

### Typical IType extensions ? Fake Isolated Production

Pattern now shows Fake{Type}, Isolated{Type}, Production{Type} as typical generated extensions of {IType}. Demo{Type} optional later. Factory returns one of those extensions; examples remain multi-type bundles by example_key.

### Proceed discovery to explore

User approved proceed. Discovery Increment 1 (Story->CE imports, pattern factories, Fake/Isolated/Production, multi-type example bundles) is agreed. Moving CDD fidelity to explore.

### Discovery generate before explore

Corrected premature explore. Generated discovery artifacts first: connect-story-examples/story-map.md + thin-slice.md (stories@discovery); example-factories/example-factories.md (ce@language). Explore waits on user review/proceed.

### Stories reframe ? generate extensions; generate stories that import

Stories are not about Author importing helpers. Correct framing: (1) CE generates Fake/Isolated/Production extending IType ? production already works; (2) stories generator generates epics, scenarios, steps that import those factories. Rewrote story-map, thin-slice, ce language doc, and cdd-sketch.

### Stories reframe confirmed

User confirmed: (1) CE generates Fake/Isolated/Production extending IType ? production already works; (2) stories generator generates epics/sub-epics/scenario steps that import those factories. Not Author-import stories.

### Proceed to explore

User approved proceed to explore after discovery generates and stories reframe. Increment 1 lenses: stories@exploration and clean_engineering@modules.

### Explore sketch + grill before treating generates as locked

User required proper explore sketch from child templates and grilling. Explore generates already written are provisional until sketch+grill confirms.

### Scenario steps call helpers not factories directly

Generated scenario steps call epic/sub-epic helpers; helpers import ExampleFactory and expose methods. Steps do not call CartExampleFactory directly.

### Fake at exploration/spec; Isolated/Production by test tier

Story exploration and specification use Fake. Story tests are by tier: Isolated for one layer, Production for another. Helpers return Fake during explore/spec; tier wiring chooses Isolated or Production per layer.

### Clarify Fake fill from bundle

User asked what 'constructor and public api filled from the bundle' means. Pending confirmation of plain-English meaning.

### Isolated tier meaning needs specificity

User rejected vague 'IsolatedType exists for that tier layer'. Asking whether Isolated means the type under test has faked dependencies (user's example) vs earlier slot model where dependencies* are filled as real collaborators.

### Clarify production path reused

User does not understand 'existing production path is reused'. That phrase was agent shorthand for earlier 'production already works' ? needs plain-English confirmation of what already exists vs what we generate.

### Fakes come from the factory via helpers

User confirmed intent: exploration/spec FakeCart/FakeProduct come from the ExampleFactory. Chain is steps -> helper -> factory -> Fake*. Sketch wording should say helpers call factory methods that return Fakes, not that helpers invent Fakes.

### Isolated, Production, factory chain confirmed

Isolated = real public API for the tier; dependencies stubbed/mocked. 'CE already generates production / reuse path' is not a testable story ? drop that framing. Production = real implementation used by a production-tier story test. Explore/spec Fakes come from ExampleFactory via helpers (steps -> helper -> factory -> Fake*).

### Proceed explore to spec

User approved proceed to spec. Increment 1 lenses: stories@specification and clean_engineering@specification. Grill before sketch before generate.

### Interface extensions = one story several scenarios

generate-interface-extensions is one story with several scenarios (Fake, Isolated, Production), not three separate stories. Pending confirm of story name and whether import-factories sub-epic also collapses.

### Story name ? Generate Type Extending Interface

One story: Generator --> Generate Type Extending Interface. Scenarios: Fake, Isolated, Production (not three stories).

### Import-factories stay separate stories

Generate Stories That Import Factories keeps separate stories (epic helper, sub-epic helper, scenario steps) ? behaviour different enough. Only Generate Interface Extensions collapses to one story with Fake/Isolated/Production scenarios.

### Clarify Fake/Isolated/Production class generation question

User did not understand 'generate Fake/Isolated/Production as classes extending IType at spec'. Rephrase in plain English: today we only have interfaces (ICart). Next generate ? create real FakeCart/IsolatedCart/ProductionCart classes now, or wait until engineering?

### Cart/Product are pattern examples only ? not the app

User correction: Cart/Product/PetStore are EXAMPLES for the factory pattern documentation. We are not building a pet store or cart app. Work is generators ? CE generates Fake/Isolated/Production pattern; stories generator emits artifacts that import factories. Do not treat FakeCart as product deliverable.

### Extend CE + Stories generators ? not a cart app

Spec work extends context_tools/clean_engineering: generator instructions/templates/methods build Fake/Isolated/Production for any {Type}. Extends context_tools/stories: generator emits example factories / links to factories and uses those objects in scenarios. Cart/Product remain pattern examples only.

### Generate CE then Stories packages

User chose 1 ? generate into packages CE first then Stories. Extending clean_engineering instructions/templates for Fake/Isolated/Production; then stories for factory links + scenario object use.

### Proceed spec to engineer

User approved proceed to engineer (layout consolidation confirmed OK). Increment 1 still: extend CE + Stories generators ? not a cart app.

### Engineer ships templates + instructions + format converters

User chose 1 with clarification: engineer work is primarily template and instruction changes, along with format converters (render/transform channels) ? not a separate heavy runtime product. Still include thin tier tests that prove emission. CE + Stories packages.

### Engineer ships templates + instructions + format converters

User chose 1 with clarification: engineer work is primarily template and instruction changes, along with format converters (render/transform channels) ? not a separate heavy runtime product. Still include thin tier tests that prove emission. CE + Stories packages.

### Engineer converters ? python, js, md

User: format converters for Python and JS, and also MD. Engineer ships templates + instructions + format converters in those three channels for CE Fake/Isolated/Production and Stories factory links.

### Generate CE converters first

User approved generate CE converters first (python, javascript, markdown) for Fake/Isolated/Production + ExampleFactory. Then Stories.

### Generate Stories converters

User approved Stories converters next ? py/js/md emit factory imports in helpers + scenario use. Thin tests prove emission.

