import javascript
import subject_filter

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
  (method.isGetter() or method.isSetter())
}

predicate classOperation(MethodDefinition method) {
  inSubject(method) and
  exists(method.getDeclaringType().getName()) and
  not method.isGetter() and
  not method.isSetter()
}

string fieldHint(FieldDefinition field) {
  exists(TypeAnnotation ann | ann = field.getTypeAnnotation() and result = ann.toString())
  or
  not exists(field.getTypeAnnotation()) and result = ""
}

string accessorHint(MethodDefinition method) {
  method.isGetter() and
  (
    exists(TypeAnnotation ann |
      ann = method.getBody().getReturnTypeAnnotation() and result = ann.toString()
    )
    or
    not exists(method.getBody().getReturnTypeAnnotation()) and result = ""
  )
  or
  method.isSetter() and
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
