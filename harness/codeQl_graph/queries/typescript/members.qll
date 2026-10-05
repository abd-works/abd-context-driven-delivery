import javascript
import subject_filter

predicate classOperation(MethodDefinition method) {
  inSubject(method) and
  not method.getName() = "constructor" and
  not method.getName().matches("\\_%")
}

predicate classProperty(
  string className, string name, string base, int start, string path, int end, string hint
) {
  exists(FieldDefinition field |
    inSubject(field) and
    className = field.getDeclaringType().getName() and
    name = field.getName() and
    not name.matches("\\_%") and
    not field.isStatic() and
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
  or
  exists(GetterMethodDefinition getter |
    inSubject(getter) and
    className = getter.getDeclaringType().getName() and
    name = getter.getName() and
    not name.matches("\\_%") and
    base = getter.getFile().getBaseName() and
    start = getter.getLocation().getStartLine() and
    path = getter.getFile().getRelativePath() and
    end = getter.getLocation().getEndLine() and
    hint = name.prefix(1).toUpperCase() + name.suffix(1)
  )
}

bindingset[hint]
predicate isRelativeHint(string hint) {
  exists(ClassDefinition cls |
    inSubject(cls) and
    hint.matches("%" + cls.getName() + "%") and
    not hint.matches("%[%]%")
  )
}
