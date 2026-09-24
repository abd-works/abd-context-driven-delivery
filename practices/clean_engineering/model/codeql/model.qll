import python
import subject_filter

predicate inSource(AstNode n) {
  exists(string path | path = n.getLocation().getFile().getRelativePath())
}

predicate ownerClass(Function method, Class cls) { method = cls.getAMethod() }

string operationLabel(Function f) {
  if exists(Class cls | ownerClass(f, cls))
  then result = min(Class cls | ownerClass(f, cls) | cls.getName()) + "." + f.getName()
  else result = f.getName()
}

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

bindingset[name]
string identToken(string name) { result = name.toLowerCase().regexpFind("[a-z][a-z0-9]*", _, _) }

/** A public method — QL splits identifiers; Python WordNet decides which tokens are nouns. */
class PublicOperation extends Function {
  Class owner;

  PublicOperation() { publicMethod(owner, this) }

  Class getOwner() { result = owner }

  string getAToken() {
    result = identToken(this.getName())
    or
    exists(Attribute field |
      field.getScope() = this and
      field.getObject().(Name).getId() = "self" and
      result = identToken(field.getName())
    )
    or
    exists(Parameter p |
      domainParameter(this, p) and result = identToken(p.getName())
    )
    or
    exists(Attribute attr, Call call |
      call.getScope() = this and
      call.getFunc() = attr and
      attr.getObject().(Name).getId() = "self" and
      result = identToken(attr.getName())
    )
    or
    exists(Call call |
      call.getScope() = this and result = identToken(call.getFunc().(Name).getId())
    )
  }
}

class ClassWithOperations extends Class {
  ClassWithOperations() { exists(PublicOperation op | op.getOwner() = this) }

  int getPublicOperationCount() { result = count(PublicOperation op | op.getOwner() = this) }
}

predicate tooManyPublicMethods(Class cls) {
  cls.(ClassWithOperations).getPublicOperationCount() > 3
}

predicate domainParameter(Function f, Parameter p) {
  p = f.getAnArg() and
  p.getName() != "self" and
  p.getName() != "cls"
}

int domainParameterCount(Function f) { result = count(Parameter p | domainParameter(f, p)) }

predicate tooManyParameters(Function f) {
  f.getName() != "__init__" and
  domainParameterCount(f) > 2
}

int operationStatementCount(Function f) { result = count(Stmt s | s.getScope() = f) }

int operationLineCount(Function f) { result = operationStatementCount(f) }

predicate longOperation(Function f) { operationStatementCount(f) > 20 }

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

predicate decoratorNamed(Function f, string decorator) {
  exists(Expr dec | dec = f.getADecorator() |
    dec.(Name).getId() = decorator
    or
    dec.(Call).getFunc().(Name).getId() = decorator
  )
}

predicate staticOrClassMethod(Function f) {
  decoratorNamed(f, "staticmethod") or decoratorNamed(f, "classmethod")
}

bindingset[name]
predicate instanceCreationName(string name) {
  name = "__new__" or
  name = "instance" or
  name = "get_instance" or
  name = "getInstance" or
  name = "shared" or
  name = "create" or
  name.matches("from_%")
}

predicate returnsNewOwner(Function f) {
  exists(Class cls, Return ret, Call call |
    ownerClass(f, cls) and
    ret.getScope() = f and
    call = ret.getValue() and
    (
      call.getFunc().(Name).getId() = cls.getName() or
      call.getFunc().(Name).getId() = "cls"
    )
  )
}

predicate instanceCreationMethod(Function f) {
  instanceCreationName(f.getName()) or returnsNewOwner(f)
}

predicate staticUtilityMethod(Function f) {
  staticOrClassMethod(f) and
  not instanceCreationMethod(f)
}

predicate moduleLevelFunction(Function f) {
  inSource(f) and
  f.getScope() instanceof Module and
  not exists(Class cls | ownerClass(f, cls))
}

string graphOwnerName(Function method) {
  exists(Class cls | ownerClass(method, cls) and result = cls.getName())
  or
  (
    moduleLevelFunction(method) and
    result = normalizedPath(method.getLocation().getFile())
  )
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
  not ownPrivateRead(f, attr)
}

predicate ownPrivateRead(Function f, Attribute attr) {
  exists(string receiver | receiver = attr.getObject().(Name).getId() |
    receiver = "self"
    or
    receiver = "cls"
    or
    receiver = "this"
    or
    exists(Class owner | ownerClass(f, owner) and receiver = owner.getName())
  )
}

predicate bagClass(Class bag) {
  inSource(bag) and
  exists(AnnAssign assign | assign.getScope() = bag) and
  not exists(Function method |
    ownerClass(method, bag) and
    method.getName() != "__init__"
  ) and
  not resourceNamed(bag.getName())
}

predicate resourceNamed(string name) {
  exists(Class resource, Function method |
    resource.getName() = name and
    publicMethod(resource, method) and
    method.getName() != "__init__"
  )
}

predicate proceduralDoer(Class doer) {
  doer.getName().toLowerCase().regexpMatch(".*(service|handler|manager|processor|helper|worker)$")
}

predicate doerOnBag(Class doer, Class bag) {
  inSubject(bag) and
  bagClass(bag) and
  proceduralDoer(doer) and
  doer != bag and
  exists(Function method | publicMethod(doer, method) and method.getName() != "__init__") and
  forex(Function method | publicMethod(doer, method) and method.getName() != "__init__" |
    exists(Parameter p |
      domainParameter(method, p) and
      (
        p.getName().toLowerCase() = bag.getName().toLowerCase()
        or
        p.getAnnotation().(Name).getId() = bag.getName()
      ) and
      usesParameterField(method, p, _)
    )
  )
}

predicate iterationName(For loop, string name) {
  loop.getTarget().(Name).getId() = name
  or
  loop.getTarget().(Tuple).getAnElt().(Name).getId() = name
}

predicate iteratesParameter(Function f, Parameter p, For loop) {
  domainParameter(f, p) and
  loop.getScope() = f and
  (
    loop.getIter().(Name).getId() = p.getName()
    or
    exists(Call call |
      loop.getIter() = call and
      call.getFunc().(Attribute).getObject().(Name).getId() = p.getName()
    )
  )
}

predicate dataAttribute(Attribute attr) { not exists(Call call | call.getFunc() = attr) }

predicate usesParameterField(Function f, Parameter p, Expr e) {
  domainParameter(f, p) and
  e.getScope() = f and
  exists(Attribute attr |
    attr = e and
    dataAttribute(attr) and
    (
      attr.getObject().(Name).getId() = p.getName()
      or
      exists(For loop, string name |
        iteratesParameter(f, p, loop) and
        iterationName(loop, name) and
        attr.getObject().(Name).getId() = name
      )
    )
  )
}

predicate inComputation(Expr e) {
  exists(BinaryExpr bin | e = bin.getLeft() or e = bin.getRight())
  or
  exists(Compare cmp | e = cmp.getLeft())
  or
  exists(Compare cmp, int i | e = cmp.getComparator(i))
  or
  exists(BoolExpr b, int i | e = b.getValue(i))
  or
  exists(UnaryExpr u | e = u.getOperand())
  or
  exists(AugAssign a | e = a.getValue() or e = a.getTarget())
}

predicate usesSelfField(Function f, Expr e) {
  exists(Attribute attr |
    attr = e and
    attr.getScope() = f and
    attr.getObject().(Name).getId() = "self"
  )
  or
  exists(Subscript sub |
    sub = e and
    sub.getScope() = f and
    sub.getObject().(Name).getId() = "self"
  )
}

predicate envies(Function f, Parameter p) {
  domainParameter(f, p) and
  count(Expr e | usesParameterField(f, p, e) and inComputation(e)) >= 2 and
  count(Expr e | usesParameterField(f, p, e) and inComputation(e)) >=
    count(Expr e | usesSelfField(f, e))
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
  exists(File f | path = normalizedPath(f)) and
  (
    path.matches("%/examples/%") or
    path.matches("%_spec.py") or
    path.regexpMatch("(^|/)test_[^/]+\\.py$")
  )
}

string enclosingFirstClassPrefix(string path) {
  exists(File f | path = normalizedPath(f)) and
  firstClassModulePrefix(result) and
  result != "" and
  (path = result or path.matches(result + "/%")) and
  not exists(string nested |
    firstClassModulePrefix(nested) and
    nested != result and
    nested.matches(result + "/%") and
    (path = nested or path.matches(nested + "/%"))
  )
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
  enclosingFirstClassPrefix(normalizedPath(cls.getLocation().getFile())) =
    enclosingFirstClassPrefix(normalizedPath(pkg.getFile()))
}

predicate classModulePrefix(Class cls, string prefix) {
  prefix = enclosingFirstClassPrefix(normalizedPath(cls.getLocation().getFile()))
}

predicate inheritsNamed(Class child, Class parent) {
  child.getABase().(Name).getId() = parent.getName()
}

predicate domainExtensionInFrameworkModule(Class extension, Class domainType) {
  inheritsNamed(extension, domainType) and
  exists(Class frameworkType, string host, string domainPrefix |
    inheritsNamed(extension, frameworkType) and
    frameworkType != domainType and
    classModulePrefix(extension, host) and
    classModulePrefix(frameworkType, host) and
    classModulePrefix(domainType, domainPrefix) and
    host != domainPrefix
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
  (
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
    or
    exists(Import imp |
      imp.getScope() = caller and
      callee.getFile().getBaseName() = imp.getAnImportedModuleName() + ".py"
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

predicate moduleContextSourceFile(File f) {
  f.getExtension() = "py" and
  not f.getBaseName() = "__init__.py" and
  not f.getBaseName() = "register.py" and
  not f.getBaseName().matches("%_spec.py") and
  not f.getBaseName().matches("test_%") and
  not f.getBaseName().matches("%_test.py") and
  not normalizedPath(f).matches("%/scanners/%") and
  not normalizedPath(f).matches("%/templates/%")
}

/** A class whose folder should own `.context/module-context.md`. Markdown is not in the Python DB — Python reads the file after this row. */
predicate moduleOwningClass(Class cls) {
  inSubject(cls) and
  publicName(cls.getName()) and
  moduleContextSourceFile(cls.getLocation().getFile()) and
  not skippedModulePath(normalizedPath(cls.getLocation().getFile()))
}

string moduleOwningClassPath(Class cls) {
  moduleOwningClass(cls) and
  result = cls.getLocation().getFile().getAbsolutePath()
}
