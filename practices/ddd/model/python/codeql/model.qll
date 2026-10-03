import python
import subject_filter

predicate inSource(AstNode n) { exists(n.getLocation().getFile().getRelativePath()) }

bindingset[name]
predicate publicName(string name) { not name.matches("\\_%") }

predicate publicMethod(Class cls, Function method) {
  method = cls.getAMethod() and publicName(method.getName())
}

predicate bagClass(Class bag) {
  inSource(bag) and
  exists(AnnAssign assign | assign.getScope() = bag) and
  not exists(Function method | method = bag.getAMethod() and method.getName() != "__init__")
}

predicate screenClass(Class cls) {
  exists(Function method |
    method = cls.getAMethod() and
    (method.getName() = "open" or method.getName() = "isShowing" or method.getName() = "is_showing")
  )
}

predicate mentionsClass(Class owner, Class named) {
  owner != named and
  exists(Name n | n.getScope() = owner.getAMethod() or n.getScope() = owner |
    n.getId() = named.getName()
  )
}

predicate orphanClass(Class cls) {
  inSubject(cls) and
  not exists(Class other | mentionsClass(other, cls))
}

predicate homelessService(Class cls) {
  cls.getName().matches("%Service") and
  exists(Function method, Parameter p |
    publicMethod(cls, method) and
    p = method.getAnArg() and
    p.getName() != "self" and
    exists(Attribute attr | attr.getScope() = method and attr.getObject().(Name).getId() = p.getName())
  )
}

predicate collectionLifecycle(Function method) {
  method.getName() = "add" or
  method.getName() = "remove" or
  method.getName() = "update" or
  method.getName().matches("find_%") or
  method.getName() = "get" or
  method.getName() = "load"
}

predicate thinRepository(Class cls) {
  cls.getName().matches("%Repository") and
  exists(Function method | publicMethod(cls, method)) and
  not exists(Function method | publicMethod(cls, method) and collectionLifecycle(method))
}

predicate loadWithoutIdentity(Function method) {
  method.getName() = "load" and
  count(Parameter p | p = method.getAnArg() and p.getName() != "self") = 0
}

predicate leakedPrivate(Function f, Call call) {
  f.getName().matches("\\_%") and
  not f.getName().matches("\\_\\_%") and
  call.getFunc().(Attribute).getName() = f.getName() and
  call.getScope() != f
}
