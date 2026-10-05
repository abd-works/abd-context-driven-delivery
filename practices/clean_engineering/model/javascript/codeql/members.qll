import javascript
import subject_filter

predicate classOperation(MethodDefinition method) {
  inSubject(method) and
  exists(method.getDeclaringType().getName())
}

predicate classProperty(
  string className, string name, string base, int start, string path, int end, string hint
) {
  exists(FieldDefinition field, ClassDefinition cls |
    inSubject(field) and
    cls = field.getDeclaringType() and
    className = cls.getName() and
    name = field.getName() and
    base = field.getFile().getBaseName() and
    start = field.getLocation().getStartLine() and
    path = field.getFile().getRelativePath() and
    end = field.getLocation().getEndLine() and
    (
      hint = field.getTypeAnnotation().toString()
      or
      not exists(field.getTypeAnnotation()) and hint = ""
    )
  )
}

bindingset[hint]
predicate isRelativeHint(string hint) {
  hint.regexpMatch(".*[A-Z][A-Za-z0-9_].*") and
  not hint.regexpMatch(".*(Repository|Requirements|Operation|Exception|Error).*")
}
