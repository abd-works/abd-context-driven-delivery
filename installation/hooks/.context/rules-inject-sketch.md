fidelity: model
scope: inject rules into chat via @Hook
status: implemented — inject_rules on Guidance and GuidanceAction; installation unchanged

=========
theme: no new installer types
---------
ce:
MarkdownInstallation
  write rules markdown
       // .mdc files from @rules — unchanged

HookInstallation
  write hook member
       // existing walk; enrolls @Hook on Guidance.inject_rules and GuidanceAction.inject_rules

=========
theme: two operations, two events
---------
ce:
Guidance
  rules_markdown
       // @rules — one formatted markdown string (practice shared rules or fidelity rules)
  inject_rules payload
       // @echo @Hook("preToolUse")
       // toast Rules → slug when it actually injects
       // agent Write / StrReplace from chat, not Tab, not the human editor
       // body injected is rules_markdown — not walking RulesCollection
       // glob from that host's appliesTo / deployed front matter against the tool path

GuidanceAction
  inject_rules payload
       // @echo @Hook("postToolUse")
       // toast Rules → action when it actually injects
       // after this action's MCP/skill returns, except Document
       // additional_context <- listed Guidances' rules_markdown
       // Generate, Sketch, Iterate, Partition, … inherit this one operation

  ----
 notes
  Do not add RulesInstallation or a special install step
  Document inherits inject_rules and returns empty
  beforeSubmitPrompt cannot inject
  @Hook is a sibling operation of the property, not stacked on the getter — install still needs the string; the hook needs the payload
