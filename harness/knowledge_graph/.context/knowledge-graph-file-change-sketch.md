# knowledge_graph — file change (sketch)

fidelity: model / behavior
status: model written; session, hook/mcp session, graph rules collection, and refresh master green; remaining increments not started

KnowledgeGraph always reads the working copy.

Folders (CodeQL takes any database path):
- master = `.codeql/{language}-master` — created with `--overlay-base`
- working copy = `.codeql/{language}-working-copy` — overlay extract of dirty files

Two methods on KnowledgeGraph, not one populate that switches:
- `updateWorkingCopy` paths — extract onto the working copy, populate from it, then validate as today
- `refreshMaster` — rewrite master, populate master, copy master to working copy; KnowledgeGraph still reads the working copy
- `reloadWorkingCopy` — reload the working copy from the tree, populate from it, then copy the working copy onto master; KnowledgeGraph still reads the working copy
- `createDatabase` root — set the path to that repo, write master there, copy master to working copy

No master classification query. CodeQL.populate is under both calls, not the public seam.

PracticeGuidance.rules and FidelityGuidance.rules return GraphRulesCollection. An entry is a GraphRule when `practices/{practice}/model/codeql/{slug}.ql` exists, otherwise a Rule — GraphRule.validate defers to Rule.validate when there is no query.

Objects live on Session (harness/session). Session.knowledge_graph and Session.practices are lazy: first get instantiates, setter replaces, reset() clears so the next get instantiates again.

This work adds a persistent HookServer process (same ensure/spawn pattern as the CodeQL query daemon). Cursor still launches `hook_server.py` per event; that process is a CLI client onto the daemon. The daemon holds one Session so postToolUse, stop, and present share the same RAM graph and practices across hook runs. McpServer holds its own Session for now — two Sessions is fine; do not join hook and MCP onto one object in this increment.

Two GraphRulesCollection hooks. `inject_rules` stays `@Hook("postToolUse")`.

`notice_changed_file` is `@Hook("stop")` — once per turn, payload has no paths. Dirty set vs master → `updateWorkingCopy` → validate (CodeQL on the working copy) → hits live on `node.rules.violations`. Filter Session.knowledge_graph to dirty paths ∩ violations (same `filterGraph` as the explorer). No report file.

`present_violations` is also `@Hook("stop")` and `@echo`, after notice has updated the daemon Session. Channel is `followup_message` (not `afterAgentResponse` — that fires before stop). The follow-up carries the slice plus instructions: present so the user can navigate, recommend a fix for each, drop items that later validate clean. Empty follow-up when the slice has no hits. Same toast path as `inject_rules`: `PromptEcho.show_ide_toast` names that there are violations and the count.

`Validate.validate` never hand-loops rules. It iterates Guidance (`GuidanceAction.run`). Whole bag → `item.rules.validate`. One `rule=` → that `Rule.validate()` once; guidance is the practice binding, not a slug search.

=========
theme: working copy then validate
---------
ce:

Session
       // harness/session — not WorkSession, not session_logs
  knowledge_graph
       // lazy instantiate on get
       // setter replaces
       -> KnowledgeGraph
  practices
       // lazy instantiate on get
       // one PracticeGuidance per practice
       // hook and mcp read these — never load_toolsets per event
       -> PracticeGuidance
  reset
       // set graph and practices to nothing; next get instantiates again

  ----
HookServer
  session
       -> Session
       // this work: long-lived daemon; Session lives here
       // hook_server.py per Cursor event is the CLI client
       // same Session across hook runs — never a new graph per event
       // never own the graph or the practices as fields beside Session

  ----
McpServer
  session
       -> Session
       // own Session — two Sessions is fine for now
       // never the hook daemon's Session in this increment

  ----
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
  reloadWorkingCopy
       // reload the working copy from the tree, populate from it, copy working copy to master
       -> CodeQL.populate
       // populate from the working copy — never read master
       // never refreshMaster for this job
  createDatabase root
       // set the path to that repo
       // write master in that repo, copy master to working copy
       // never populate for this job
  filterGraph dirty violations
       // explorer already has this
       // dirty paths ∩ nodes with node.rules.violations
       // keep ancestors; drop passing siblings
       // never a report file as the hook contract

  ----
PracticeGraph
  root
  nodes
       // node.rules.violations is the source of truth

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
       // payload has no paths
       -> dirty paths vs master
       -> KnowledgeGraph.updateWorkingCopy
       -> validate
       // CodeQL on the working copy; write node.rules.violations on the objects
       -> session.knowledge_graph.filterGraph dirty violations
       // objects on Session; never a report file
  present_violations payload
       @echo
       @Hook("stop")
       // after notice_changed_file on the same daemon Session
       // not afterAgentResponse
       -> followup_message from those objects + instructions
       -> PromptEcho.show_ide_toast
       // same path as inject_rules
       // toast: we have violations + the count
       // no toast when the slice is empty
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
        with dirty story-test and production-code files
          it should take dirty paths vs master, not the stop payload
          it should update the working copy from those paths
          it should extract onto the working copy
          it should not rewrite the master
          it should run CodeQL on the working copy
          it should validate from the nodes in that hierarchy
          it should attach rule violations to nodes in those files
          it should filter the knowledge graph to dirty paths and violations
          it should keep ancestors so the path stays visible
          it should drop passing siblings
          it should not write a report file for the hook
          it should keep those objects on the session knowledge graph
          with no remaining violations
            it should present an empty slice
            it should not echo a violations toast
          that has remaining violations
            it should return a followup_message on stop
            it should not use afterAgentResponse
            it should echo a toast that names the violation count
            it should instruct the agent to present the violations so the user can navigate them
            it should instruct the agent to recommend a fix for each violation
            it should instruct the agent to drop violations that have been fixed
            that the agent has fixed some of those violations
              it should keep the remaining violations on the objects
              it should not show the ones that now validate
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
      that has a working copy to reload
        it should reload the working copy
        it should populate from the working copy
        it should repopulate the master

a knowledge graph
  that has been pointed at a different repo
    it should set the path to that repo
    it should create the database in that repo
    it should copy the master to the working copy

a session
  that the hook server holds
    it should live on the persistent hook server
    it should be the same object across hook runs
    it should expose a knowledge graph
    it should expose each practice guidance
    that has no graph yet
      it should instantiate a knowledge graph on get
    that has no practices yet
      it should instantiate practice guidance on get
    that has been given a knowledge graph
      it should return that graph on get
    that has been reset
      it should instantiate a knowledge graph on the next get
      it should instantiate practice guidance on the next get
    it should not load toolsets on each hook event
  that the mcp server holds
    it should be a session
    it should not be the hook server session
    it should expose a knowledge graph
    it should expose each practice guidance
    it should not load toolsets on each mcp call

=========
theme: increments
---------

each: one real slice, mamba on real files, no stubs; then the next

an increment
  that is session
    it should lazy load knowledge_graph and practices
    it should accept a setter
    it should reset so the next get instantiates again
    // a session — except hook/mcp
  that is hook and mcp session
    it should keep a persistent hook server and a CLI per Cursor event
    it should reuse the hook session across hook runs
    it should let mcp keep its own session
    // two Sessions is fine for now
  that is graph rules collection
    it should use GraphRule when a .ql exists
    it should still inject with globs
    // that is injecting on postToolUse
  that is refresh master
    it should extract codeql-slice into master
    it should copy master to working copy
    // that is ready to become the master
  that is reload working copy
    it should reload the working copy from the tree
    it should copy the working copy onto master
    // that has a working copy to reload
  that is create database
    it should set the path to a different repo
    it should write master in that repo
    // that has been pointed at a different repo
  that is update working copy
    it should extract dirty story-test and production files onto the working copy
    it should not rewrite the master
    // that has changed… file-type nests
  that is validate from the hierarchy
    it should attach node.rules.violations
    it should validate only that rule when rule is passed
    // that has updated the working copy / that has been validated
  that is filter graph
    it should keep dirty paths and violations
    it should keep ancestors
    it should drop passing siblings
  that is notice changed file
    it should run on stop
    it should take dirty paths vs master
    it should run update working copy then validate then filter onto the session
    // that the agent loop has stopped — minus present
  that is present violations
    it should return followup_message on stop
    it should echo a toast with the violation count
    it should not use afterAgentResponse
    it should keep remaining violations after a real fix

 