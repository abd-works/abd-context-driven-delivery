import javascript
import subject_filter

predicate inSource(AstNode n) { exists(n.getLocation().getFile().getRelativePath()) }

bindingset[name]
predicate publicName(string name) { not name.matches("\\_%") }

predicate publicMethod(ClassDefinition cls, MethodDefinition method) {
  method = cls.getMethod(method.getName()) and publicName(method.getName())
}

predicate bagClass(ClassDefinition bag) {
  inSource(bag) and
  exists(FieldDefinition field | field.getDeclaringType() = bag) and
  not exists(MethodDefinition method |
    method.getDeclaringType() = bag and method.getName() != "constructor"
  )
}

predicate screenClass(ClassDefinition cls) {
  exists(MethodDefinition method |
    method.getDeclaringType() = cls and
    (method.getName() = "open" or method.getName() = "isShowing" or method.getName() = "is_showing")
  )
}

predicate mentionsClass(ClassDefinition owner, ClassDefinition named) {
  owner != named and
  exists(Identifier id |
    id.getName() = named.getName() and
    id.getFile() = owner.getFile()
  )
}

predicate orphanClass(ClassDefinition cls) {
  inSubject(cls) and
  not exists(ClassDefinition other | mentionsClass(other, cls))
}

predicate homelessService(ClassDefinition cls) {
  cls.getName().matches("%Service") and
  exists(MethodDefinition method, Parameter p |
    publicMethod(cls, method) and
    p = method.getBody().getAParameter() and
    exists(PropAccess access |
      access.getEnclosingFunction() = method.getBody() and
      access.getBase().(VarAccess).getName() = p.getName()
    )
  )
}

predicate collectionLifecycle(MethodDefinition method) {
  method.getName() = "add" or
  method.getName() = "remove" or
  method.getName() = "update" or
  method.getName().matches("find_%") or
  method.getName() = "get" or
  method.getName() = "load"
}

predicate thinRepository(ClassDefinition cls) {
  cls.getName().matches("%Repository") and
  exists(MethodDefinition method | publicMethod(cls, method)) and
  not exists(MethodDefinition method | publicMethod(cls, method) and collectionLifecycle(method))
}

predicate loadWithoutIdentity(MethodDefinition method) {
  method.getName() = "load" and
  count(Parameter p | p = method.getBody().getAParameter()) = 0
}

predicate leakedPrivate(MethodDefinition f, CallExpr call) {
  f.getName().regexpMatch("^_[^_].*") and
  call.getCalleeName() = f.getName() and
  call.getEnclosingFunction() != f.getBody()
}
