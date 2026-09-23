# knowledge_graph — file change (sketch)

fidelity: model / behavior
status: unlocked from grill; not generate yet

KnowledgeGraph always reads the working copy.

Folders (CodeQL takes any database path):
- master = `.codeql/{language}-master` — created with `--overlay-base`
- working copy = `.codeql/{language}-working-copy` — overlay extract of dirty files

Two methods on KnowledgeGraph, not one populate that switches:
- `updateWorkingCopy` paths — extract onto the working copy, populate from it, then validate as today
- `refreshMaster` — rewrite master, populate master, copy master to working copy; KnowledgeGraph still reads the working copy

No master classification query. CodeQL.populate is under both calls, not the public seam.

PracticeGuidance.rules and FidelityGuidance.rules return GraphRulesCollection. An entry is a GraphRule when `practices/{practice}/model/codeql/{slug}.ql` exists, otherwise a Rule — GraphRule.validate defers to Rule.validate when there is no query.

The file-change hook is `@Hook("stop")` on GraphRulesCollection — agent loop end, once per turn. `inject_rules` stays `@Hook("postToolUse")`. Stop payload has no paths; dirty set is working copy vs master.

`Validate.validate` never hand-loops rules. It iterates Guidance (`GuidanceAction.run`). Whole bag → `item.rules.validate`. One `rule=` → that `Rule.validate()` once; guidance is the practice binding, not a slug search.

=========
theme: working copy then validate
---------
ce:

KnowledgeGraph
  practice_graphs
       // always the working copy — never master
  updateWorkingCopy paths
       // extract those paths onto the working copy
       -> CodeQL.populate
       // populate from the working copy; never rewrite master
       // never a classify.ql
  refreshMaster
       // rewrite master, populate master, then copy master to working copy
       -> CodeQL.populate
       // populate from the new working copy — never read master
       // never updateWorkingCopy for this job

  ----
PracticeGraph
  root
  nodes
  report_path
       // last validate written for the agent to Read

  ----
PracticeGuidance
  rules
       -> GraphRulesCollection
       // override Guidance.rules

  ----
FidelityGuidance
  rules
       -> GraphRulesCollection
       // override Guidance.rules

  ----
Validate
  validate guidance rule
       -> GuidanceAction.run guidance
       // one on(item) per Guidance — not a rule loop
       -> item.rules.validate
       // when rule is omitted — same as today: walk the bag / filter with violations
       -> rule.validate
       // when rule is passed; that object only; no collection walk; no slug lookup on item.rules

  ----
RulesCollection
  inject_rules payload
       @Hook("postToolUse")
       -> matches path
       -> additional_context markdown
       // never CodeQL
  from_markdown text
  validate
       // @collect of Rule.validate — agent instructions, not CodeQL

  ----
GraphRulesCollection : RulesCollection
  notice_changed_file payload
       @Hook("stop")
       // end of agent loop — not postToolUse, not afterAgentResponse
       // 30s, no CodeQL; payload has no paths
       -> dirty paths vs master
       -> last node.rules.violations for those locations
       -> additional_context count + report_path
       // empty when no RuleViolation.location matches a dirty path
  validate
       // inherited @collect — GraphRule.validate or Rule.validate per entry
       -> node.rules.violations
  // do not add evaluate
  // mixed bag: GraphRule where .ql exists, Rule otherwise
  // do not override matches yet for inject — glob channel stays on RulesCollection

  ----
CodeQL
  populate graph database
       // one operation; database is master or working copy
       // same fact queries either way
       // updateWorkingCopy passes working copy
       // refreshMaster passes master, then copies master to working copy
       // KnowledgeGraph never reads master
       // never the KnowledgeGraph seam
       // never a parallel classify.ql that restates populate
       // never AppliesTo.globs
  run query
  ensure_database language
       // updateWorkingCopy: working copy + dirty-file extract
       // refreshMaster: rewrite master, populate master, copy to working copy
       // never copy master on each edit
       // never OverlayManager / OverlayDatabase

  ----
GraphRule : Rule
  practice
  applies_to
       // node types from FIDELITY_NODE_SCOPE — already on the Node
  validate
       // same verb as Rule.validate
       -> CodeQL.run graphQuery when .ql exists
       -> Rule.validate when it does not
       -> node.rules.violations
  // do not add evaluate

  ----
RuleViolation
  rule_slug
  message
  practice
  location
  line
  node_id

=========
theme: master vs working copy
---------
ce:

CodeQL
  master
       // .codeql/{language}-master — full extract of a known-good tree
       // CodeQL --overlay-base on this folder
       // written only by refreshMaster
       // cleanup --cache-cleanup=overlay after a warm populate + rules.ql
       // never --expect-discarded-cache on master
       // never extract dirty files onto this folder
  working_copy
       // .codeql/{language}-working-copy — the only database KnowledgeGraph reads
       // copied from master only in refreshMaster
       // updateWorkingCopy extracts dirty files onto this folder
       // never copy master on each edit
  // subject_filter still limits printed subjects; working copy is the extract, not a line filter
  // never restrictAlertsTo as the main mechanism — graph rules need unchanged types, calls, imports

=========
theme: bdd behavior
---------

a repo
  that has been captured as a kg database
    with production code and story tests already defined
      that has changed story-test and production-code files
        it should update the working copy from those paths
        it should keep the same practice-graph hierarchy
        it should keep rules on those nodes
        it should include story and scenario nodes from the tests
        it should include module or class nodes from the production files
        it should extract onto the working copy
        it should not rewrite the master
        that has updated the working copy
          it should validate from the nodes in that hierarchy
          it should not iterate the rule list on validate
          it should not require a classification query
          with a single rule passed
            it should validate only that rule
            it should not walk the collection
          that has been validated
            it should attach rule violations to nodes in those files
            it should expose those hits on node.rules.violations
            it should run graph rules as one batch
            it should still collect markdown rules as instruction text
      that has changed a story-test file
        it should include story nodes whose location is that file
        it should include scenario nodes whose location is that file
      that has changed a python module file
        it should include module or class nodes whose location is that file
        it should not treat the file as a story
      that the agent loop has stopped
        it should not run CodeQL on the hook
        it should read the last evaluation only
        it should take dirty paths vs master, not the stop payload
        with violations stored for those files
          it should return additional_context that names the report path
        with no violations for those files
          it should return no additional_context
      that is injecting on postToolUse
        it should still match bags with AppliesTo.globs
        it should not use graph matching for inject yet
        it should still return markdown additional_context from matches
        it should not run graph-rule validate
      that is ready to become the master
        it should rewrite the master
        it should populate the master
        it should copy the master to the working copy
        it should not read the master after the copy
 