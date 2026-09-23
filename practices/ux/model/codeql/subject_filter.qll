import javascript

predicate subjectFilterPrefix(string prefix) { prefix = "" }

predicate firstClassModulePrefix(string prefix) { none() }

predicate inSubject(AstNode n) {
  inSubjectPath(n.getLocation().getFile().getRelativePath().replaceAll("\\", "/"))
}

bindingset[path]
predicate inSubjectPath(string path) {
  any()
}
