import python
import subject_filter

predicate inSource(AstNode n) {
  exists(string path | path = n.getLocation().getFile().getRelativePath())
}

predicate ownerClass(Function method, Class cls) { method = cls.getAMethod() }

predicate publicName(string name) {
  (
    exists(Function f | name = f.getName())
    or
    exists(Class cls | name = cls.getName())
  ) and
  not name.matches("\\_%")
}

predicate publicMethod(Class cls, Function method) {
  ownerClass(method, cls) and
  publicName(method.getName())
}

int publicMethodCount(Class cls) { result = count(Function method | publicMethod(cls, method)) }

predicate tooManyPublicMethods(Class cls) { publicMethodCount(cls) > 10 }

predicate domainParameter(Function f, Parameter p) {
  p = f.getAnArg() and
  p.getName() != "self" and
  p.getName() != "cls"
}

int domainParameterCount(Function f) { result = count(Parameter p | domainParameter(f, p)) }

predicate tooManyParameters(Function f) { domainParameterCount(f) > 2 }

int operationLineCount(Function f) {
  result = f.getLocation().getEndLine() - f.getLocation().getStartLine() + 1
}

predicate longOperation(Function f) { operationLineCount(f) > 20 }

predicate controlStmt(Stmt s) {
  s instanceof If
  or
  s instanceof For
  or
  s instanceof While
}

int nestLevel(AstNode n) {
  if exists(Stmt p | p = n.getParentNode() and controlStmt(p))
  then result = 1 + nestLevel(n.getParentNode())
  else result = 0
}

predicate deeplyNested(Function f) {
  exists(Stmt s | s.getScope() = f and nestLevel(s) > 3)
}

predicate bareExcept(Function f, ExceptStmt ex) {
  ex.getScope() = f and
  not exists(ex.getType())
}

predicate swallowedExcept(Function f, ExceptStmt ex) {
  ex.getScope() = f and
  exists(Pass p | p.getScope() = f and p.getParentNode*() = ex)
}

predicate constructsTypeInInit(Function init, Class constructed) {
  init.getName() = "__init__" and
  inSource(constructed) and
  exists(Call call |
    call.getScope() = init and
    call.getFunc().(Name).getId() = constructed.getName()
  )
}

predicate accessorOperation(Function f) {
  f.getName().regexpMatch("get[A-Z_].*")
  or
  f.getName().regexpMatch("set[A-Z_].*")
  or
  f.getName().matches("get_%")
  or
  f.getName().matches("set_%")
}

predicate moduleLevelFunction(Function f) {
  inSource(f) and
  not exists(Class cls | ownerClass(f, cls))
}

predicate calledFromClass(Function f, Class cls) {
  exists(Call call |
    call.getScope() = cls.getAMethod() and
    call.getFunc().(Name).getId() = f.getName()
  )
}

predicate calledOnlyFrom(Function f, Class cls) {
  moduleLevelFunction(f) and
  calledFromClass(f, cls) and
  not exists(Class other | other != cls and calledFromClass(f, other))
}

predicate privateAttributeRead(Function f, Attribute attr) {
  attr.getScope() = f and
  attr.getName().matches("\\_%") and
  not attr.getName().matches("\\_\\_%") and
  attr.getObject().(Name).getId() != "self"
}

predicate bagClass(Class bag) {
  inSource(bag) and
  exists(AnnAssign assign | assign.getScope() = bag) and
  not exists(Function method |
    ownerClass(method, bag) and
    method.getName() != "__init__"
  )
}

predicate doerOnBag(Class doer, Class bag) {
  bagClass(bag) and
  doer != bag and
  exists(Function method | publicMethod(doer, method) and method.getName() != "__init__") and
  forex(Function method | publicMethod(doer, method) and method.getName() != "__init__" |
    exists(Parameter p |
      domainParameter(method, p) and
      (
        p.getName().toLowerCase() = bag.getName().toLowerCase()
        or
        p.getAnnotation().(Name).getId() = bag.getName()
      )
    )
  )
}

predicate envies(Function f, Parameter p) {
  domainParameter(f, p) and
  count(Attribute attr |
    attr.getScope() = f and
    attr.getObject().(Name).getId() = p.getName()
  ) >= 3
}

predicate untypedPublicParameter(Function f, Parameter p) {
  publicName(f.getName()) and
  domainParameter(f, p) and
  (
    not exists(p.getAnnotation())
    or
    p.getAnnotation().(Name).getId() = "dict"
    or
    p.getAnnotation().(Name).getId() = "Any"
    or
    p.getAnnotation().(Name).getId() = "list"
  )
}

predicate numberedName(string name) {
  exists(Parameter p | name = p.getName()) and
  name.regexpMatch("[A-Za-z]+[0-9]+")
}

predicate numberedParameter(Function f, Parameter p) {
  domainParameter(f, p) and
  numberedName(p.getName())
}

string normalizedPath(File f) { result = f.getRelativePath().replaceAll("\\", "/") }

predicate skippedModulePath(string path) {
  path.matches("%/examples/%") or
  path.matches("%_spec.py") or
  path.regexpMatch("(^|/)test_[^/]+\\.py$")
}

predicate firstClassModule(Module m) {
  m.getFile().getBaseName() = "__init__.py" and
  exists(string prefix |
    firstClassModulePrefix(prefix) and
    normalizedPath(m.getFile()) = prefix + "/__init__.py"
  )
}

predicate classInFirstClassModule(Class cls, Module pkg) {
  firstClassModule(pkg) and
  inSource(cls) and
  not skippedModulePath(normalizedPath(cls.getLocation().getFile())) and
  exists(string prefix |
    firstClassModulePrefix(prefix) and
    normalizedPath(pkg.getFile()) = prefix + "/__init__.py" and
    (
      normalizedPath(cls.getLocation().getFile()) = prefix + "/__init__.py" or
      normalizedPath(cls.getLocation().getFile()).matches(prefix + "/%")
    )
  )
}

int classCount(Module pkg) {
  firstClassModule(pkg) and
  result = count(Class cls | classInFirstClassModule(cls, pkg))
}

int publicClassCount(Module pkg) {
  firstClassModule(pkg) and
  result = count(Class cls | classInFirstClassModule(cls, pkg) and publicName(cls.getName()))
}

predicate topLevelClass(Module m, Class cls) { classInFirstClassModule(cls, m) }

predicate topLevelFunction(Module m, Function f) { f.getScope() = m }

int topLevelCount(Module m) { result = classCount(m) }

int publicTopLevelCount(Module m) { result = publicClassCount(m) }

predicate shallowModule(Module m) {
  firstClassModule(m) and
  classCount(m) >= 5 and
  publicClassCount(m) * 100 > classCount(m) * 40
}

predicate moduleDependsOn(Module caller, Module callee) {
  caller != callee and
  exists(Function callerFn, Function calleeFn |
    inSource(callerFn) and
    inSource(calleeFn) and
    callerFn.getEnclosingModule() = caller and
    calleeFn.getEnclosingModule() = callee and
    exists(Call call |
      call.getScope() = callerFn and
      call.getFunc().(Attribute).getName() = calleeFn.getName()
    )
  )
}

predicate cyclicModules(Module a, Module b) {
  a != b and
  moduleDependsOn(a, b) and
  moduleDependsOn(b, a)
}

predicate passThrough(Function f) {
  exists(Call call, Return ret |
    call.getScope() = f and
    ret.getScope() = f and
    ret.getValue() = call and
    not exists(Call other | other.getScope() = f and other != call) and
    not exists(Return other | other.getScope() = f and other != ret)
  )
}
