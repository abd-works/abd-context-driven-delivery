<!--
  clean_engineering markdown template — unified across all fidelities.

  Fidelity tags on every element (as HTML comments at end of line or block):
    L  = language companion (prose identity; refined at every stage — not a fidelity)
    Mu = modules        (thin terms, one-way deps, build order; no I{Class} yet)
    Md = model          (I{ClassName} only — empty public props/ops)
    S  = specification  ({ClassName} extends I{ClassName}; public filled; privates empty)
    C  = code           (fill {ClassName}; drop interactions; keep invariant comments)

  Class member format (model & specification):
    ------  (six dashes)   constructor / properties separator
    ----    (four dashes)  properties / operations separator
    -       (dash prefix)  private operation
    +       (plus prefix)  public — specification fidelity only

  Subtypes use ### **{ChildClass} : {ClassName}** notation; deltas only.
  Substitute {ClassName} / {owned_property} / {param} / {Type} / … when generating.
-->

# {ClassName}                                                     <!-- L -->

---

## Language companion                                             <!-- L -->

*{ClassName}* is {intent — what role it plays, what it holds, what it does.
This paragraph IS the class definition. Identity only.}           <!-- L -->

### {class_name_as_a_concept}                                     <!-- L -->

- {bullet: what it holds, what it does, how it relates to *another class*} <!-- L -->
- {as many bullets as the concept warrants}                       <!-- L -->
- **Invariant:** {rule that must always hold — only when one exists} <!-- L -->

### {ChildClass} *is a type of* {ClassName}                       <!-- L -->

- {delta behavior only — what this subtype adds or overrides}     <!-- L -->

---

## Modules fidelity                                               <!-- Mu -->

### Module `{module_path}`                                        <!-- Mu -->

- **Purpose:** {one paragraph}                                    <!-- Mu -->
- **Seam (terms):** {ClassName}, {ChildClass}, …                  <!-- Mu -->
- **Dependencies (one-way):** {other_module}, …                   <!-- Mu -->
- **Build order:** see `{session}/.context/module-build-order.md` <!-- Mu -->

Diagram (optional): fill `templates/modules.drawio` — one blue box per module;
bullets = Seam terms; arrows = one-way Dependencies (toward the depended-on module).
Path nesting = containment (child boxes inside the parent). Shared base terms live on
the parent module, not a `parent/base` submodule. No stack/tech callouts.
Transform: `markdown` ↔ `drawio` at modules fidelity.

---

## Model fidelity                                                 <!-- Md -->

### **I{ClassName}**                                              <!-- Md -->

I{ClassName}({param}: {Type})                                     <!-- Md -->
------
{owned_property}: {Type}                                          <!-- Md -->
{plain_property}: {Type}                                          <!-- Md -->
----
{operation_name}({param}: {Type}): {ReturnType}                   <!-- Md -->
{another_operation}(): {ReturnType}                               <!-- Md -->

### **I{ChildClass}**                                             <!-- Md -->

I{ChildClass}({param}: {Type})                                    <!-- Md -->
------
----
{delta_operation}({param}: {Type}): {ReturnType}                  <!-- Md -->

---

## Specification fidelity                                         <!-- S -->

### **{ClassName} : I{ClassName}**                                <!-- S -->

+ {ClassName}({param}: {Type})                                    <!-- S -->
------
+ {owned_property}: {Type}                                        <!-- S -->
	Invariant: {constraint sentence.}                             <!-- S -->
+ << composition >> {owned_property}: {Type}                      <!-- S -->
+ << aggregation >> {collected_property}: list[{Type}]            <!-- S -->
+ << association >> {referenced_property}: {Type}                 <!-- S -->
----
+ {operation_name}({param}: {Type}): {ReturnType}                 <!-- S -->
	Invariant: {constraint sentence applicable to this operation.} <!-- S -->
	Interaction:                                                   <!-- S -->
		{variable}: {Type} = {other}.{call}({args})               <!-- S -->
		return {variable}                                         <!-- S -->
- _{private_helper}({param}: {Type}): {Type}                      <!-- S -->

### **{ChildClass} : I{ChildClass}**                              <!-- S -->

+ {ChildClass}({param}: {Type})                                   <!-- S -->
------
+ {child_specific_property}: {Type}                               <!-- S -->
	Invariant: {constraint sentence.}                             <!-- S -->
----
+ {delta_operation}({param}: {Type}): {ReturnType}                <!-- S -->

### **Example factory (when Stories-bound) — separate file**      <!-- Md/S -->

Write factories in `{type_slug}_example_factory.md` (or code sibling), **not** in the production family file.
Do not sketch Fake{ClassName} / Isolated{ClassName} / Production{ClassName} types.

### **I{ClassName}ExampleFactory**                                <!-- Md -->

+ load_{example_key}(mode): I{ClassName}                          <!-- Md -->

### **{ClassName}ExampleFactory : I{ClassName}ExampleFactory**    <!-- S -->

+ load_{example_key}(mode): I{ClassName}                          <!-- S -->
	// examples[{example_key}] multi-type bundle                  <!-- S -->
	// Fake: mock/stub framework + feed examples                  <!-- S -->
	// Isolated: new {ClassName}(ctor-injected mocks/stubs)       <!-- S -->
	// Production: new {ClassName}(real collaborators)            <!-- S -->
