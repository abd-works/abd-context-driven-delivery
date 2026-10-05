import python

predicate subjectFilterPrefix(string prefix) { prefix = "" }

predicate firstClassModulePrefix(string prefix) { none() }

predicate inSubject(AstNode n) {
  inSubjectPath(n.getLocation().getFile().getRelativePath().replaceAll("\\", "/"))
}

predicate inSubjectFilter(Class cls) {
  inSubject(cls)
}

bindingset[path]
predicate inSubjectPath(string path) {
  any()
}
