import python

predicate subjectFilterPrefix(string prefix) { prefix = "" }

predicate firstClassModulePrefix(string prefix) {
  prefix = "deep-module" or
  prefix = "language-modules-one-section" or
  prefix = "modules-not-model-blocks" or
  prefix = "public-seam-only" or
  prefix = "extensions-live-with-the-domain/framework" or
  prefix = "extensions-live-with-the-domain/domain"
}

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
