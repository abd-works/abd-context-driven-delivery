# HIERARCHY: story-graph-ops (excerpt captured as a failure fixture)
<!-- Every top-level describe here is a code-level class name, not a domain concept. LanguageAst / TypeScriptAst / CodeStoryNode are compiler-implementation stereotypes; RowPositions is a layout helper; MarkdownSynchronizer / TypeScriptSynchronizer are service classes; DiagramStoryNode is an abstract class exposed as a subject instead of the domain concept it represents (a diagram Story Map). The state-oriented and observations-are-results rules can be clean while this rule is still violated. -->

a LanguageAst

  that has been asked to parse a raw source string
    it should populate its internal AST from the source

  that has been asked to generate source code
    it should produce a raw source string from the internal AST

a TypeScriptAst

  that is generating from a StoryNode
    it should produce a TypeScript interface for the node
    it should produce a describe block for the node

a CodeStoryNode

  that has had updateSelf called from a source
    it should carry the same domain fields as the source
    the held LanguageAst
      it should reflect the language-agnostic structure of the node

a RowPositions

  that has been constructed for a tree with a maximum SubEpic depth of 2
    the SubEpic row for depth 0
      it should sit directly below the Epic row
    the actor row
      it should sit directly below the deepest SubEpic row

a DiagramStoryNode

  a SubEpic
    with an Epic parent
      it should accept the parent
    with a Story parent
      it should reject the parent

a MarkdownSynchronizer
  that has synced a canonical Story Map into an existing Markdown document
    the returned UpdateReport
      it should list every add, remove, rename, reorder, and move applied to the document

a TypeScriptSynchronizer
  that has regenerated the folder from a canonical Story Map
    the returned UpdateReport
      it should list every add, remove, rename, reorder, and move applied to the folder
