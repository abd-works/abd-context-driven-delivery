# CDD Sketch-to-Code Transformation Design

## Core Flow

```text
Context
  ↓ AI
CDD Sketch
  ↓ deterministic transform
Domain code skeleton
  ↓ AI
Implemented domain behavior
  ↓ deterministic architecture transform
Architecture-specific skeleton
  ↓ AI
Remaining implementation behavior
```

The **existing CDD sketch notation is the canonical input to transformation**.

Do not introduce a new YAML, JSON, `Concept/State/Operations`, or other parallel representation.

---

# 1. Context → Sketch is AI

AI reads:

```text
source context
+ applicable Stories rules
+ applicable Clean Engineering rules
+ relevant DDD rules
+ the existing sketch templates
```

and produces the existing CDD sketch syntax.

The two key templates are:

```text
practices/stories/templates/stories-sketch.md
practices/clean_engineering/templates/clean_engineering-sketch.md
```

The sketch contains both behavioral and object-model information at the appropriate fidelity.

---

# 2. Stories Sketch

Use the existing Stories sketch notation:

```text
{Epic verb-noun}
    {Sub-epic verb-noun}
        {Actor} --> {Story verb-noun}
            {scenario name}
                given ...
                when ...
                then ...
~> Increment 1: ...
```

Example:

```text
Manage Deliveries
    Plan Deliveries
        Customer --> Book Delivery
        Dispatcher --> Assign Delivery
        Dispatcher --> Reassign Delivery

    Complete Deliveries
        Driver --> Collect Delivery
        Driver --> Confirm Delivery

~> Increment 1: Complete one delivery:
   Book Delivery, Assign Delivery, Collect Delivery, Confirm Delivery
```

At later fidelity the same sketch can deepen:

```text
Dispatcher --> Assign Delivery
    suitable driver and vehicle assigned
        given a Delivery with handling requirements
            and a Driver with required qualifications
            and a Vehicle with sufficient capacity
        when the Dispatcher assigns the Delivery
        then the Delivery has the Driver assigned
            and the Delivery has the Vehicle assigned
```

Stories provide behavioral context for the domain design.

---

# 3. Clean Engineering Sketch

Use the existing CE notation exactly.

The template defines:

```text
ClassName : BaseClass
  propertyName
  operationName param param
  RelatedClass

  ----
 PeerClass
      property
      operation param
```

Important semantics from the existing template:

```text
ClassName
    = class

propertyName
    = state held by the class

operationName param param
    = operation and its parameters

indent
    = ownership/composition/subordination

----
    = peer class

-> collaborator.operation
    = actual collaboration

// ...
    = invariant or sequencing note
```

So for the delivery example, the sketch should look like this:

```text
Delivery
  id
  status
  deliveryWindow
  handlingRequirements
  driver
  vehicle

  assign driver vehicle
      -> driver.isAvailable
      -> driver.isQualifiedFor
      -> vehicle.canCarry
      -> vehicle.supports
      // assignment must satisfy Delivery handling requirements

  reassign driver vehicle
      -> driver.isAvailable
      -> vehicle.canCarry
      // preserve deliveryWindow and handlingRequirements

  confirm proof
      // only an assigned Delivery can be confirmed

  ----

Driver
  availability
  qualifications

  isAvailable
  isQualifiedFor requirements

  ----

Vehicle
  capacity
  refrigerationCapability

  canCarry delivery
  supports handlingRequirements
```

This is the real semantic input.

There is no intermediate:

```text
Concept:
State:
Operations:
```

schema.

The CE sketch already carries those semantics.

---

# 4. Fidelity Matters

The existing CE sketch intentionally gets more precise as fidelity increases.

## Early sketch

Names may be relatively loose:

```text
Delivery
  deliveryWindow
  assign driver vehicle
```

AI is still resolving the design.

## Model fidelity

The sketch becomes typed and exact:

```text
Delivery
  id DeliveryId
  status DeliveryStatus
  deliveryWindow DeliveryWindow
  handlingRequirements HandlingRequirements

  assign driver:Driver vehicle:Vehicle -> void
  reassign driver:Driver vehicle:Vehicle -> void
  confirm proof:DeliveryProof -> DeliveryConfirmation
```

The current template notation may need a small extension/normalization for return types and explicit type syntax if these are not already represented consistently by the parser.

That is preferable to inventing another model format.

---

# 5. AI Owns Semantic Decisions

AI produces the precise sketch.

AI decides:

```text
Delivery
```

rather than some alternative concept.

AI decides:

```text
assign
```

rather than `allocate`, `dispatch`, etc.

AI decides:

```text
assign driver vehicle
```

including the exact parameters.

AI decides:

```text
deliveryWindow
handlingRequirements
status
```

as state owned by Delivery.

AI also decides exact types and return values once the sketch reaches model fidelity.

Example:

```text
assign driver:Driver vehicle:Vehicle -> void
confirm proof:DeliveryProof -> DeliveryConfirmation
```

The transformer does **not** infer these semantic choices.

---

# 6. Sketch → Domain Code is Deterministic

The transformer parses the actual sketch.

For:

```text
Delivery
  status DeliveryStatus
  deliveryWindow DeliveryWindow

  assign driver:Driver vehicle:Vehicle -> void
  confirm proof:DeliveryProof -> DeliveryConfirmation
```

the transformer understands:

```text
Class = Delivery

members:
    status
    deliveryWindow

operations:
    assign(driver, vehicle)
    confirm(proof)
```

This parse result can exist transiently in memory.

It is **not another persisted domain model**.

Then the selected language renderer produces source.

Python:

```python
class Delivery:
    status: DeliveryStatus
    delivery_window: DeliveryWindow

    def assign(
        self,
        driver: Driver,
        vehicle: Vehicle,
    ) -> None:
        raise NotImplementedError()

    def confirm(
        self,
        proof: DeliveryProof,
    ) -> DeliveryConfirmation:
        raise NotImplementedError()
```

TypeScript:

```typescript
export class Delivery {
    status: DeliveryStatus;
    deliveryWindow: DeliveryWindow;

    assign(driver: Driver, vehicle: Vehicle): void {
        throw new Error("Not implemented");
    }

    confirm(proof: DeliveryProof): DeliveryConfirmation {
        throw new Error("Not implemented");
    }
}
```

Java:

```java
public class Delivery {
    DeliveryStatus status;
    DeliveryWindow deliveryWindow;

    public void assign(Driver driver, Vehicle vehicle) {
        throw new UnsupportedOperationException();
    }

    public DeliveryConfirmation confirm(DeliveryProof proof) {
        throw new UnsupportedOperationException();
    }
}
```

Same sketch semantics, different renderer.

---

# 7. AI Implements Domain Behavior

Once real domain classes exist:

```text
Delivery
Driver
Vehicle
```

AI receives:

```text
domain source
+ Stories/scenarios/examples
+ original sketch
+ CE/DDD rules
```

and implements the bodies.

For example:

```text
Delivery.assign(...)
```

gets:

```text
driver availability check
driver qualification check
vehicle capacity check
refrigeration check
assignment mutation
invariant enforcement
```

The public structure already exists.

AI should not casually rename operations, move ownership, or alter signatures.

If implementation reveals a design error, revise the sketch explicitly and regenerate/reconcile.

---

# 8. Domain Code → Architecture is Deterministic

After the domain code is implemented, the selected architecture specification expands it.

Example input:

```text
Delivery
  assign(driver, vehicle)
  reassign(driver, vehicle)
  confirm(proof)
```

The architecture profile may require:

```text
DeliveryRepository
Delivery persistence representation
Delivery HTTP boundary
Delivery client
Delivery page
ExampleFactory
Acceptance-test infrastructure
module exports
wiring
```

These should be derived from the actual domain structure and the selected architecture specification.

Example:

```text
Delivery
        ↓ architecture transform

DeliveryRepository
  load
  create
  search
  update

DeliveryRecord
  persistent representation of Delivery state

DeliveryServer
  assign
  reassign
  confirm

DeliveryClient
  assign
  reassign
  confirm

DeliveryPage
  invokes the appropriate client/domain operations
```

The architecture transform should **propagate existing names and semantics**, not independently reinvent them.

---

# 9. Architecture Transform vs AI

The architecture transformer can deterministically decide:

```text
Delivery
    → DeliveryRepository

Delivery.assign
    → server/client operation named assign

Delivery state
    → persistence fields

module
    → folder/package layout

selected architecture
    → route conventions
    → repository conventions
    → dependency wiring
```

AI is used only when the architecture encounters a genuine semantic gap.

For example:

```text
Should assign be remotely exposed?
```

If the story/spec already makes that clear, transform it.

If not, AI resolves the ambiguity.

---

# 10. Role of Jinja

Jinja is a renderer behind the transformer.

It does not understand the original context.

It receives parsed sketch/domain structures and emits source.

Example:

```jinja
class {{ class.name }}:
{% for member in class.members %}
    {{ member.name }}: {{ member.type }}
{% endfor %}

{% for op in class.operations %}
    def {{ op.name }}(
        self{% for p in op.parameters %},
        {{ p.name }}: {{ p.type }}{% endfor %}
    ) -> {{ op.return_type }}:
        raise NotImplementedError()
{% endfor %}
```

The important distinction:

```text
AI
    creates the sketch

Sketch parser
    reads existing CDD syntax

Transformer
    decides mechanical derivations

Jinja
    writes source text
```

Jinja never decides domain semantics.

---

# 11. Tooling

Recommended implementation:

```text
Existing CDD sketch templates
        ↓
small sketch parser
        ↓
existing CDD semantic/model classes where useful
        ↓
transformation functions
        ↓
Jinja language templates
        ↓
source
```

For existing-source updates later:

```text
Tree-sitter / ast-grep
```

For advanced language-specific rewriting only where required:

```text
TypeScript → ts-morph
Python     → LibCST
C#         → Roslyn
Java       → JavaParser
```

For validation:

```text
compiler
tests
CDD scanners
CodeQL
```

---

# 12. Important Constraint

Do not replace the existing sketch syntax with a new generic intermediate specification.

The sketch already is the human/AI-facing semantic representation.

The implementation should therefore focus on:

```text
existing sketch
      ↓
parse
      ↓
transform
      ↓
code
```

not:

```text
existing sketch
      ↓
convert to YAML/JSON/meta-model
      ↓
transform
```

A temporary parse tree/object graph in memory is fine.

It is implementation state, not another artifact.

---

# Final Architecture

```text
CONTEXT
    ↓ AI

CDD SKETCH
Stories sketch +
Clean Engineering sketch

    ↓ deterministic parser/transform

DOMAIN CODE SKELETON

    ↓ AI

IMPLEMENTED DOMAIN

    ↓ deterministic architecture transform

ARCHITECTURE-SPECIFIC CODE SKELETON

    ↓ AI

WORKING IMPLEMENTATION
```

The architectural rule remains:

> **AI decides semantics in the existing CDD sketch. Transformers materialize and propagate those semantics.**
