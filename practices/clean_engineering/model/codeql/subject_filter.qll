import python

predicate subjectFilterPrefix(string prefix) { prefix = "harness/knowledge_graph" }

predicate firstClassModulePrefix(string prefix) { prefix = "harness/knowledge_graph" }

predicate inSubject(AstNode n) {
  inSubjectPath(n.getLocation().getFile().getRelativePath())
}

predicate inSubjectFilter(Class cls) {
  inSubject(cls)
}

predicate inSubjectPath(string path) {
  exists(File f, string prefix, string normalized |
    subjectFilterPrefix(prefix) and
    path = f.getRelativePath() and
    normalized = path.replaceAll("\\", "/") and
    (normalized = prefix or normalized.matches(prefix + "/%"))
  )
}
