---
rule: subjects-are-domain-concepts
severity: error
---
# Subjects Are Domain Concepts

This rule is not about grammar. It is about how hard you thought before you named a subject.

Every describe subject must be a **first-class domain concept** — a thing that has independent meaning in the domain, has real behaviors and state of its own, and would be discussed by a domain expert without any reference to code. If your candidate subject only exists because the code needed a place to put some machinery, you have not found the real subject yet. Stop, do deeper object-oriented domain analysis, and find the actual thing whose state or behavior you are describing.

The most common failure mode is inventing subjects out of internal plumbing — an AST, a synchronizer, a positioner, a factory, a coordinator, a manager, a helper — and treating them as if they had domain meaning. They do not. They have no observable state a domain expert would name; they have no behaviors independent of the real thing they support; they were only ever a code-structural choice.

## What a real domain subject looks like

A real domain subject satisfies all of these:

1. **It has independent meaning in the domain.** A domain expert who has never seen the code recognises it and can talk about it. `a Story Map`, `an Epic`, `a Markdown document`, `a diagram Story Map` all pass this. `a StoryNode`, `a LanguageAst`, `a MarkdownSynchronizer` do not — the expert would ask "is that something in your code?"
2. **It has real state you can describe with state elaborations.** You can write `with X`, `that has been Y`, `with 4 Z in sequential order` and produce meaningful sub-states. If every state elaboration you attempt reads as "that has been called with", "that has just executed", "that returned", the thing has no state of its own — it is machinery, not a subject.
3. **Its observations are facts about it, not facts about what it did to other things.** `a Story Map ... it should hold 5 Epics` is a fact about the Story Map. `a Synchronizer ... it should have applied the changes to the document` is a fact about *the document*, dressed up as if the synchronizer were the subject.
4. **You can name it without any implementation vocabulary.** If you have to say "a TypeScript AST" or "a Node in the Story tree" or "a Row Position calculator", you are naming a code artifact. If you can say "a Story Map rendered as TypeScript" or "an Epic" or "a diagram Story Map", you have named a domain concept.

## What plumbing looks like when it sneaks in as a subject

The plumbing subjects that most often slip in — and the real subject hiding behind each:

| Plumbing subject you were tempted to write | The real domain subject | Why the plumbing failed the test |
|---|---|---|
| `a LanguageAst` | `a code Story Map` | An AST is a parser's data structure. Nobody in the domain talks about ASTs. The real thing is the Story Map that got rendered as source. |
| `a TypeScriptAst` | `a TypeScript Story Map` | Same. The rendered artifact is the domain thing; the AST is how the code manipulates it. |
| `a RowPositions` | `a diagram Story Map` | Positioning is a property of the diagram, not a separate concept. "Where does the Epic sit?" is a fact about the diagram, not about a positioner. |
| `a MarkdownSynchronizer` | `a Markdown document` (in the state "that has been edited and synced back") | Synchronisation is what happens *to* the document. The document is what has state; the synchroniser has none. |
| `a TypeScriptSynchronizer` | `a TypeScript Story Map` (in the state "that has been edited in source and synced back") | Same. |
| `a DiagramStoryNode` | `a diagram Story Map` or `an Epic in a diagram Story Map` | `-Node` is a data-structure noun. The real subject is what that node represents in the diagram. |
| `a StoryNode` | `a Story Map`, `an Epic`, `a SubEpic`, `a Story` — pick the actual node kind | `StoryNode` is a code superclass. Nobody in the domain talks about "a node" — they talk about the specific kind of thing. |
| `a UserRepository` | `a User` (in the state "that has been persisted", "that has been loaded from storage") | Repositories are persistence plumbing. The user is the subject. |
| `a StripePaymentAdapter` | `a Payment` (in the state "that has been submitted to Stripe", "that has been authorised") | Adapters are integration plumbing. The payment is the subject. |
| `an OrderValidator` | `an Order` (in the state "with insufficient stock", "with an invalid shipping address") | Validators are policy plumbing. The order — in a valid or invalid state — is the subject. |

Pattern: whenever your candidate subject ends in `-Node`, `-Ast`, `-Synchronizer`, `-Positioner`, `-Positions`, `-Manager`, `-Coordinator`, `-Handler`, `-Helper`, `-Factory`, `-Builder`, `-Marshaller`, `-Parser`, `-Serializer`, `-Renderer`, `-Validator`, `-Repository`, `-Adapter`, `-Mapper`, `-Service`, `-Controller`, or reads as a data-structure noun (`-Tree`, `-Graph`, `-List`, `-Set`, `-Map`, `-Node`, `-Entry`, `-Row`, `-Column`), you are almost certainly looking at plumbing. Ask: what real thing does this plumbing operate on or represent? That is your subject.

## The recovery move: object-oriented domain analysis

When you catch yourself with a plumbing subject, do not just rename it. Do the analysis:

1. **What real thing does this plumbing operate on or represent?** The AST operates on / represents source code. The synchroniser operates on a document. The positioner operates on a diagram. The repository operates on a User. That real thing is the candidate subject — but keep going.
2. **Do the observations you wanted to write make sense as facts about that real thing?** "The AST should have 4 top-level nodes" becomes "the code Story Map should render as 4 top-level folders". "The synchroniser should have applied the rename" becomes "the document, that has been synced, should show the new name". If the observations read naturally on the real thing, you have found the subject.
3. **What state elaboration puts that real thing in the situation you were originally describing?** "That has been rendered from a 4-Epic Story Map." "That has been edited and synced back against the canonical Story Map." "With 4 Epics on the Epic row." The plumbing's *action* becomes a *state* on the real subject.
4. **Does the real subject already exist as a domain concept, or do you need to add one?** Often you will discover you need a new domain concept — `a code Story Map`, `a diagram Story Map`, `a rendered document` — that captures the shared idea across many concrete backends. Add it to your domain language, then use it. Do not skip step 4 and reach for the concrete backend as a subject just because it is nameable.

## Mock-backed abstraction pattern (for genuinely shared behavior)

When behavior is shared across many concrete backends and no single backend is the "domain" answer, the domain concept you need often does not exist yet in the code — it lives at the abstract level.

- Real code has `DiagramStoryNode` (abstract) with `DrawIODiagramStoryNode` and `MiroDiagramStoryNode` as concretes.
- The domain concept behind them is *"a Story Map represented as a diagram"* — that is what the shared behavior is about.
- Model that concept as `a diagram Story Map` (subject).
- Back it in tests with a mock `DiagramStoryNode` that implements only the abstract contract.
- Then `a DrawIO Story Map` and `a Miro Story Map` are separate subjects that add only the backend-specific facts on top.

The abstract class name never appears as a subject. The domain concept it represents does. If no domain concept exists for it yet, invent one — that is the work.

## Behaviors of a subject stay on the subject

If a "service" or "helper" class in the code exists to perform behaviors on a domain object, those behaviors live on the domain object as a subject, not on the helper as a subject.

Wrong:

```
a MarkdownSynchronizer
  that has synced a canonical Story Map into an existing Markdown document
    the returned UpdateReport
      it should list every add, remove, rename, reorder, and move applied to the document
```

The `UpdateReport` is what the sync produced *about the document*. The document is what changed. The synchroniser has no state — it only did a thing.

Right:

```
a Markdown document
  that has been edited and synced back against a canonical Story Map
    the returned UpdateReport
      it should list every add, remove, rename, reorder, and move applied to the document
    the reconstructed Story Map
      it should reflect every edit made to the document
```

The `MarkdownSynchronizer` class may still exist in code. It is just not a subject in the spec.

## The three-question interrogation

Before you accept a subject, ask it three questions:

1. **"What are you, independent of the code that manipulates you?"** If the honest answer is "I am the code that manipulates X", you are not a subject — X is.
2. **"What state can I put you in that a domain expert cares about?"** If the honest answer is only "you can call my methods and I run", you are not a subject.
3. **"What can I truthfully say about you, not about something you did to another thing?"** If every observation you can support is really about a different noun, that other noun is the subject.

Any subject that cannot answer all three has failed. Do the recovery move and try again.

## Examples

- Wrong: `a LanguageAst > that has been asked to parse a raw source string > it should populate its internal AST from the source` — LanguageAst is a compiler-implementation stereotype with no independent domain meaning; the observation is about internal population
- Right: `a code Story Map > with 4 Epics > every Epic > it should produce a folder named after the Epic` — the domain concept is the subject; the observation is an external fact about it
- Wrong: `a RowPositions > that has been constructed for a tree with max SubEpic depth of 2 > it should place every Epic on the fixed Epic Y` — RowPositions is a layout helper; positioning is a property of the diagram, not a separate concept
- Right: `a diagram Story Map > with 4 Epics > every Epic > it should sit on the Epic row` — same observation on the real subject
- Wrong: `a TypeScriptSynchronizer > that has regenerated the folder > the returned UpdateReport > it should list every change` — synchroniser is a service stereotype; the change list is a fact about the source that changed
- Right: `a TypeScript Story Map > that has been edited in the TypeScript source and synced back > the returned UpdateReport > it should list every change` — the sync behavior belongs on the domain subject that was synced
- Wrong: `a DiagramStoryNode > that has been translated from a source with an added child > it should have carried the new child` — DiagramStoryNode is a code class; the observation is about the diagram, not a node
- Right: `a diagram Story Map > that has been translated from a source with an added Epic > it should show the added Epic on the Epic row` — the diagram is what changed
