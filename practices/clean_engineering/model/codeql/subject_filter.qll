import python

predicate subjectFilterPrefix(string prefix) { prefix = "practices/stories/catalog-examples" }

predicate firstClassModulePrefix(string prefix) {
  prefix = "practices/stories/catalog-examples"
}

predicate inSubject(AstNode n) {
  inSubjectPath(n.getLocation().getFile().getRelativePath().replaceAll("\\", "/"))
}

predicate inSubjectFilter(Class cls) {
  inSubject(cls)
}

bindingset[path]
predicate inSubjectPath(string path) {
  exists(string filterPrefix, string normalized |
    subjectFilterPrefix(filterPrefix) and
    normalized = path.replaceAll("\\", "/") and
    (normalized = filterPrefix or normalized.matches(filterPrefix + "/%"))
  )
}
