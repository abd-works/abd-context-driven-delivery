# Every format reads into the base nodes, and each text format keeps only its notation

**Status:** decided, release 1.2 (design proposal 3 c). Replaces cdr 0002.

## Decision

The markdown, sketch, draw.io and whiteboard formats all read a map into the base *BoundedContext* and *Aggregate*
(the sketch through *SketchBoundedContext* and *SketchAggregate*, which hold only what a sketch read needs while it
reads). The building blocks are the cards every format writes: *DomainClass* and its subclasses in `building_blocks.py`
hold a card's invariants, whether a repository is drawn inside its root's card, its root mark, and how it takes the
words of the card it replaces. *Aggregate* answers its root card, its repository, its members, its drawn members, the
root a drawing shows, and the cards it takes from a class model, whichever format it was read from.

Each text format keeps only its notation, as objects that read into and write from the base nodes: markdown's
*ContextSection*, *AggregateSection* and *CardSection*; the sketch's *SketchedContext*, *SketchedAggregate* and
*SketchedCard*; and *AggregateLines*, an aggregate's own lines (its root line, members, `Integrations:` and events),
which both write. An arc reads and writes its own `- target` lines (*Integration*).

## Why

- cdr 0002 had every format read into the markdown nodes so that each could write every document format. That made
  the sketch and the drawn map import the markdown format, and kept two copies of the aggregate's behaviour (the base
  and the markdown subclass) that disagreed on what `take_class` and `take_root_from_classes` do.
- Writing through notation objects over the base nodes gives the same reach as 0002 with no format depending on
  another: any map writes as markdown or a sketch because the writers ask only the base nodes.

## Consequences

A new document format adds its own reader and writer over the base nodes; it does not subclass another format's nodes
or add a second set of context and aggregate fields.
