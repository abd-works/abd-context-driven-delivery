import python

predicate subjectFilterPrefix(string prefix) { prefix = "" }

predicate firstClassModulePrefix(string prefix) {
  prefix = "actions" or
  prefix = "actions/grill_context" or
  prefix = "actions/improvement" or
  prefix = "actions/iterate" or
  prefix = "actions/partition" or
  prefix = "actions/scan" or
  prefix = "actions/sketch" or
  prefix = "builders" or
  prefix = "builders/create_agent_toolset" or
  prefix = "builders/create_context_tool" or
  prefix = "harness" or
  prefix = "harness/agent_tools" or
  prefix = "harness/hooks" or
  prefix = "harness/knowledge_graph" or
  prefix = "harness/markdown" or
  prefix = "harness/mcp" or
  prefix = "installation" or
  prefix = "practices/agent_bdd" or
  prefix = "practices/bdd" or
  prefix = "practices/clean_engineering" or
  prefix = "practices/clean_engineering/model" or
  prefix = "practices/clean_engineering/model/drawio" or
  prefix = "practices/clean_engineering/scanners" or
  prefix = "practices/ddd" or
  prefix = "practices/kanban" or
  prefix = "practices/stories" or
  prefix = "practices/ux" or
  prefix = "practices/ux/model" or
  prefix = "practices/ux/model/drawio" or
  prefix = "practices/ux/model/html" or
  prefix = "practices/ux/model/json" or
  prefix = "practices/ux/model/markdown" or
  prefix = "practices/ux/scanners" or
  prefix = "practices/ux/scripts" or
  prefix = "practices/ux/story-demo" or
  prefix = "practices/ux/story-demo/play-dual-runner" or
  prefix = "tools" or
  prefix = "tools/catalog_generator" or
  prefix = "tools/diagnose" or
  prefix = "tools/echo" or
  prefix = "tools/git" or
  prefix = "tools/handoff" or
  prefix = "tools/plan" or
  prefix = "tools/prompt_echo" or
  prefix = "tools/record_decisions" or
  prefix = "tools/workflow"
}

predicate inSubject(AstNode n) {
  inSubjectPath(n.getLocation().getFile().getRelativePath())
}

predicate inSubjectFilter(Class cls) {
  inSubject(cls)
}

predicate inSubjectPath(string path) {
  exists(File f |
    path = f.getRelativePath().replaceAll("\\", "/")
  )
}
