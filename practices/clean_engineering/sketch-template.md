# clean_engineering sketch template — terse indent notation

Rough shape for sketching an clean_engineering analysis before generating the formal artifact. Use clean_engineering vocabulary directly (class, property, operation, subtype, composition, aggregation, association) rather than the generic `thing` fallback.

## Notation

```
ClassName : BaseClass
  propertyName
  operationName param param
  otherPropertyOrOperationName
       nestedThing                      <-- a owned class
       nestedOperation param
  RelatedClass                          <-- association candidate

  ----
 SubtypeName : ClassName
      otherCollaborator                 <-- construction property (delta)
      operationName param
       -> otherCollaborator.operation   <-- real call on a held collaborator
       -> super.operation               <-- base operation when subtype extends it
       // invariant or sequencing note
      ----
 Collaborator
      property
      operation param
```

## Legend

| Symbol | clean_engineering meaning |
|---|---|
| `ClassName` | a class — earn a name once identity, state, behavior, or invariants justify it |
| `ClassName : BaseClass` | subtype of BaseClass; record only the delta |
| `propertyName` | something the class holds (noun phrase) |
| `operationName param` | something the class does (verb phrase); trailing tokens are parameters |
| indent | ownership / composition / subordination |
| `----` | separator between the primary class block and a peer class it relates to |
| `-> collaborator.operation` | interaction — a real operation on a property, peer, or `super` |
| `-> _private_helper` | rare — only when no public collaborator operation exists and the helper is essential to the story |
| `// …` | invariant or sequencing note |

## Interaction rules (read these)

- **Prefer real calls.** Write `-> opposingTrait.resolve`, `-> cart.add_item`, `-> super.resolve` — names that exist (or will exist) on the sketch.
- **Do not invent underscore placeholders** (`_opposing_roll`, `_private_helper_important_enough_to_show`) as a default. Those hide the design. If you cannot name a real receiver + operation, the collaboration is not understood yet — grill it or leave a `//` note.
- **`-> ClassName` alone is not an interaction.** Point at an operation (or a property read that matters), not the type.
- Show only interactions that clarify collaboration; suppress incidental helpers.

## Fidelity progression

- **Language fidelity** — everything is a name; parameters are prose; relationship kind (composition / aggregation / association) is not yet committed.
- **Model fidelity** — add types to properties and operation signatures. Relationship kind is decided per pair.
- **Specification fidelity** — full typed contracts, invariants, cardinality. The sketch is superseded once the formal artifact captures all of this.

## Rules

- Nothing needs a formal name until the grill reveals it. `thing` is fine as a placeholder if the concept isn't stable yet.
- Indent = owned or subordinate. Never use indent for association — put associated classes as peers below `----`.
- One class family per file (`cohesive-file`): a class plus its subtypes and tightly connected peers (element + collection, small aggregate + part). Multiple unrelated families belong in separate sketches / separate code files.

## Discovery precedence (context for the sketcher)

Session context wins. If the caller pasted their own template in chat, use that instead of this file. This file is the clean_engineering-flavoured convention layer, one step above the generic default at `sketch/sketch-template.md`.
