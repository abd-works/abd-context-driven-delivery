<!--
  clean_engineering markdown template — unified across all fidelities.

  Fidelity tags on every element (as HTML comments at end of line or block):
    L = language      (prose description; no types, signatures, or relationship kinds)
    M = model         (typed compact block; constructor, properties, operation stubs)
    S = specification (+ prefix, relationship kinds, invariant sentences, interactions)

  Class member format (model & specification):
    ------  (six dashes)   constructor / properties separator
    ----    (four dashes)  properties / operations separator
    -       (dash prefix)  private operation
    +       (plus prefix)  public — specification fidelity only

  Subtypes use ### **Child : Parent** notation; deltas only.
-->

# {ClassName}                                                     <!-- L -->

---

## Language fidelity                                              <!-- L -->

*{ClassName}* is {intent — what role it plays, what it holds, what it does.
This paragraph IS the class definition. Identity only.}           <!-- L -->

### {class_name_as_a_concept}                                     <!-- L -->

- {bullet: what it holds, what it does, how it relates to *another class*} <!-- L -->
- {as many bullets as the concept warrants}                       <!-- L -->
- **Invariant:** {rule that must always hold — only when one exists} <!-- L -->

### {SubtypeName} *is a type of* {ClassName}                      <!-- L -->

- {delta behavior only — what this subtype adds or overrides}     <!-- L -->

---

## Model fidelity                                                 <!-- M -->

### **{ClassName}**                                               <!-- M -->

{ClassName}({Type}, {Type})                                       <!-- M -->
------
{propertyName}: {Type}                                            <!-- M -->
	Invariant: {constraint sentence.}                             <!-- M -->
{anotherProperty}: {Type}                                         <!-- M -->
----
{operationName}({Type}): {ReturnType}                             <!-- M -->
	Invariant: {constraint sentence applicable to this operation.} <!-- M -->
{anotherOperation}(): void                                        <!-- M -->
- {privateHelper}({Type}): {Type}                                 <!-- M -->

### **{ChildClass} : {ParentClass}**                              <!-- M -->

{ChildClass}({Type})                                              <!-- M -->
------
----
{deltaOperation}({Type}): {ReturnType}                            <!-- M -->

---

## Specification fidelity                                         <!-- S -->

### **{ClassName}**                                               <!-- S -->

+ {ClassName}({param}: {Type})                                    <!-- S -->
------
+ {property}: {Type}                                              <!-- S -->
	Invariant: {constraint sentence.}                             <!-- S -->
+ << composition >> {ownedProperty}: {Type}                       <!-- S -->
+ << aggregation >> {collectedProperty}: list[{Type}]             <!-- S -->
+ << association >> {referencedProperty}: {Type}                  <!-- S -->
----
+ {operation}({param}: {Type}): {ReturnType}                      <!-- S -->
	Invariant: {constraint sentence applicable to this operation.} <!-- S -->
	Interaction:                                                   <!-- S -->
		{variable}: {Type} = {other}.{call}({args})               <!-- S -->
		return {variable}                                         <!-- S -->
- _{privateHelper}({param}: {Type}): {Type}                       <!-- S -->

### **{ChildClass} : {ParentClass}**                              <!-- S -->

+ {ChildClass}({param}: {Type})                                   <!-- S -->
------
+ {childSpecificProperty}: {Type}                                 <!-- S -->
	Invariant: {constraint sentence.}                             <!-- S -->
----
+ {childOperation}({param}: {Type}): {ReturnType}                 <!-- S -->
