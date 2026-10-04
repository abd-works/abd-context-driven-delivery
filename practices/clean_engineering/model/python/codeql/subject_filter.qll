import python

predicate subjectFilterPrefix(string prefix) { prefix = "" }

predicate inSubject(AstNode n) { exists(n.getLocation()) }

predicate inSubjectFilter(Class cls) { inSubject(cls) }

predicate inSubjectPath(string path) { exists(File f | path = f.getRelativePath()) }

predicate firstClassModulePrefix(string prefix) {
  exists(File init |
    init.getBaseName() = "__init__.py" and
    prefix = init.getParentContainer().getRelativePath().replaceAll("\\", "/")
  )
}
