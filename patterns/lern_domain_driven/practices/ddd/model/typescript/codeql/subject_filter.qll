import javascript

predicate subjectFilterPrefix(string prefix) { prefix = "" }

predicate firstClassModulePrefix(string prefix) { none() }

predicate inSubject(AstNode n) { exists(n.getLocation()) }

predicate inSubjectPath(string path) { exists(File f | path = f.getRelativePath()) }
