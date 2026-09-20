fidelity: model
scope: annotated markdown collection — not nested toolsets
status: agreed

=========
theme: we already locate; collection keeps .markdown
---------
ce:
Markdown
  // already: folder / file / section via AssetLocator
  extract
  coerce return_type
       // RulesCollection.from_markdown already maps section bullets

MarkdownCollection
  markdown
       // original extract — one file is that file; never formatted() rebuild
  // list return type → iterate section bullets or files in the folder
  // map return type → key = bullet label or file stem
  from_markdown text
       -> Markdown.extract

RulesCollection : MarkdownCollection
  // keep appliesTo / from_markdown bullets
  markdown
       // replaces Guidance.rules_markdown

@markdownCollection label
       -> Markdown.from_label
       -> Markdown.extract
       -> Markdown.coerce return_type
       // same locate as @markdown; result.markdown is the extract

Guidance
  rules
       // @markdownCollection("shared rules") -> RulesCollection
       // @rules lives on this member — not a twin string property
  inject_rules
       -> rules.markdown
  instructions
       -> rules.markdown
  // drop rules_markdown
