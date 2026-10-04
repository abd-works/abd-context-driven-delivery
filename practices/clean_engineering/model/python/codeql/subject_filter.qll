import python

predicate subjectFilterPrefix(string prefix) { prefix = "" }

predicate firstClassModulePrefix(string prefix) {
  prefix = "deep-module" or
  prefix = "extensions-live-with-the-domain/faulty/domain" or
  prefix = "extensions-live-with-the-domain/faulty/framework" or
  prefix = "language-modules-one-section/faulty" or
  prefix = "language-modules-one-section/repaired" or
  prefix = "missing-module-context/repaired" or
  prefix = "modules-not-model-blocks/faulty" or
  prefix = "modules-not-model-blocks/repaired" or
  prefix = "public-seam-only/faulty" or
  prefix = "public-seam-only/repaired"
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
