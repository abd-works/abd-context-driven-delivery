import python

predicate subjectFilterPrefix(string prefix) { prefix = "" }

predicate firstClassModulePrefix(string prefix) { prefix = "" }

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
