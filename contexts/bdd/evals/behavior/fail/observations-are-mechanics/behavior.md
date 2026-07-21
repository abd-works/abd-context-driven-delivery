# HIERARCHY: story-graph-ops (excerpt captured as a failure fixture)
<!-- Every leaf here observes an internal method call, super chain, or private helper — not a result the reader could verify from outside the implementation. -->

a StoryNode

  that has been translated from a source with an added child
    the target
      it should hold the new child
      it should have called its own createChildXxx factory to produce the new child
      it should have called translateFrom on the new child to fill its fields

  that is reconciling a child collection
    the reconciliation
      it should match self-children to source-children by name and sequential order via findMatch before creating any new child
      it should call translateFrom on every matched pair
      it should process child collection pairs in the order declared by childCollections

a DiagramStoryNode

  that has had updateSelf called
    it should have copied the domain fields from source first via super.updateSelf
    it should have set position and size from the placementRules for its type
    it should have applied the formatting from the formattingRules for its type

a CodeStoryNode

  that has had updateSelf called
    it should have copied the domain fields from source first via super.updateSelf
    it should have written the language-agnostic structure to the held LanguageAst
    the held LanguageAst
      it should never be replaced
