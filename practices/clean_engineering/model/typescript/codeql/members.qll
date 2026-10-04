import javascript
import subject_filter

bindingset[name]
predicate isInfraTypeName(string name) {
  name.regexpMatch(".*(Repository|Requirements|Operation|Exception|Error)")
}

predicate isLoadedClassName(string name) {
  exists(ClassDefinition cls | inSubject(cls) and cls.getName() = name)
}

bindingset[hint]
string firstTypeName(string hint) {
  result = hint.regexpCapture(".*?\\b([A-Z][A-Za-z0-9_]*).*", 1)
}

bindingset[hint]
predicate isRelativeHint(string hint) {
  exists(string name |
    name = firstTypeName(hint) and
    isLoadedClassName(name) and
    not isInfraTypeName(name)
  )
}

predicate classField(FieldDefinition field) {
  inSubject(field) and
  exists(ClassDefinition cls | cls = field.getDeclaringType())
}

predicate classAccessor(MethodDefinition method) {
  inSubject(method) and
  exists(method.getDeclaringType().getName()) and
  (
    method instanceof GetterMethodDefinition or
    method instanceof SetterMethodDefinition
  )
}

predicate classOperation(MethodDefinition method) {
  inSubject(method) and
  exists(method.getDeclaringType().getName()) and
  not method instanceof GetterMethodDefinition and
  not method instanceof SetterMethodDefinition
}

string fieldHint(FieldDefinition field) {
  exists(TypeAnnotation ann | ann = field.getTypeAnnotation() and result = ann.toString())
  or
  not exists(field.getTypeAnnotation()) and result = ""
}

string accessorHint(MethodDefinition method) {
  method instanceof GetterMethodDefinition and
  (
    exists(TypeAnnotation ann |
      ann = method.getBody().getReturnTypeAnnotation() and result = ann.toString()
    )
    or
    not exists(method.getBody().getReturnTypeAnnotation()) and result = ""
  )
  or
  method instanceof SetterMethodDefinition and
  (
    exists(Parameter p, TypeAnnotation ann |
      p = method.getBody().getParameter(0) and
      ann = p.getTypeAnnotation() and
      result = ann.toString()
    )
    or
    not exists(Parameter p |
      p = method.getBody().getParameter(0) and exists(p.getTypeAnnotation())
    ) and
    result = ""
  )
}

predicate classProperty(
  string className, string name, string base, int start, string path, int end, string hint
) {
  exists(FieldDefinition field |
    classField(field) and
    className = field.getDeclaringType().getName() and
    name = field.getName() and
    base = field.getFile().getBaseName() and
    start = field.getLocation().getStartLine() and
    path = field.getFile().getRelativePath() and
    end = field.getLocation().getEndLine() and
    hint = fieldHint(field)
  )
  or
  exists(MethodDefinition accessor |
    classAccessor(accessor) and
    className = accessor.getDeclaringType().getName() and
    name = accessor.getName() and
    base = accessor.getFile().getBaseName() and
    start = accessor.getLocation().getStartLine() and
    path = accessor.getFile().getRelativePath() and
    end = accessor.getLocation().getEndLine() and
    hint = accessorHint(accessor)
  )
}
