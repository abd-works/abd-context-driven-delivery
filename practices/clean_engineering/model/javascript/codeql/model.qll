import javascript
import subject_filter

predicate inSource(AstNode n) {
  exists(string path | path = n.getLocation().getFile().getRelativePath())
}

predicate ownerClass(Function method, ClassDefinition cls) {
  exists(MethodDefinition def | def.getBody() = method and def.getDeclaringType() = cls)
}

string operationLabel(Function f) {
  if exists(ClassDefinition cls | ownerClass(f, cls))
  then result = min(ClassDefinition cls | ownerClass(f, cls) | cls.getName()) + "." + f.getName()
  else result = f.getName()
}

predicate publicName(string name) {
  (
    exists(Function f | name = f.getName())
    or
    exists(ClassDefinition cls | name = cls.getName())
  ) and
  not name.matches("\\_%")
}

predicate publicMethod(ClassDefinition cls, Function method) {
  ownerClass(method, cls) and
  publicName(method.getName())
}

int publicMethodCount(ClassDefinition cls) {
  result = count(Function method | publicMethod(cls, method))
}

bindingset[name]
string identToken(string name) { result = name.toLowerCase().regexpFind("[a-z][a-z0-9]*", _, _) }

class PublicOperation extends Function {
  ClassDefinition owner;

  PublicOperation() { publicMethod(owner, this) }

  ClassDefinition getOwner() { result = owner }

  string getAToken() {
    result = identToken(this.getName())
    or
    exists(PropAccess field |
      field.getEnclosingFunction() = this and
      field.getBase().(VarAccess).getName() = "this" and
      result = identToken(field.getPropertyName())
    )
    or
    exists(Parameter p |
      domainParameter(this, p) and result = identToken(p.getName())
    )
    or
    exists(CallExpr call |
      call.getEnclosingFunction() = this and result = identToken(call.getCalleeName())
    )
  }
}

class ClassWithOperations extends ClassDefinition {
  ClassWithOperations() { exists(PublicOperation op | op.getOwner() = this) }

  int getPublicOperationCount() { result = count(PublicOperation op | op.getOwner() = this) }
}

predicate tooManyPublicMethods(ClassDefinition cls) {
  cls.(ClassWithOperations).getPublicOperationCount() > 3
}

predicate domainParameter(Function f, Parameter p) {
  p = f.getAParameter() and
  p.getName() != "this" and
  p.getName() != "constructor"
}

int domainParameterCount(Function f) { result = count(Parameter p | domainParameter(f, p)) }

predicate tooManyParameters(Function f) {
  f.getName() != "constructor" and
  domainParameterCount(f) > 2
}

int operationStatementCount(Function f) { result = count(Stmt s | s.getContainer() = f) }

int operationLineCount(Function f) { result = operationStatementCount(f) }

predicate longOperation(Function f) { operationStatementCount(f) > 20 }

predicate controlStmt(Stmt s) {
  s instanceof IfStmt
  or
  s instanceof LoopStmt
}

int nestLevel(AstNode n) {
  if exists(Stmt p | p = n.getParent() and controlStmt(p))
  then result = 1 + nestLevel(n.getParent())
  else result = 0
}

predicate deeplyNested(Function f) {
  exists(Stmt s | s.getContainer() = f and nestLevel(s) > 3)
}

predicate bareExcept(Function f, CatchClause ex) {
  ex.getBody().getContainer() = f and
  not exists(ex.getACaughtType())
}

predicate swallowedExcept(Function f, CatchClause ex) {
  ex.getBody().getContainer() = f and
  not exists(Stmt s | s.getParent() = ex.getBody() and not s instanceof EmptyStmt)
}

predicate constructsTypeInInit(Function init, ClassDefinition constructed) {
  init.getName() = "constructor" and
  inSource(constructed) and
  exists(NewExpr call |
    call.getEnclosingFunction() = init and
    call.getCalleeName() = constructed.getName()
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

predicate staticOrClassMethod(Function f) {
  exists(MethodDefinition def | def.getBody() = f and def.isStatic())
}

bindingset[name]
predicate instanceCreationName(string name) {
  name = "constructor" or
  name = "instance" or
  name = "get_instance" or
  name = "getInstance" or
  name = "shared" or
  name = "create" or
  name.matches("from_%") or
  name.matches("load_%")
}

predicate instanceCreationMethod(Function f) { instanceCreationName(f.getName()) }

predicate staticUtilityMethod(Function f) {
  staticOrClassMethod(f) and
  not instanceCreationMethod(f)
}

predicate moduleLevelFunction(Function f) {
  inSource(f) and
  not exists(ClassDefinition cls | ownerClass(f, cls)) and
  f.getEnclosingStmt().getContainer() instanceof TopLevel
}

predicate privateAttributeRead(Function f, PropAccess attr) {
  attr.getEnclosingFunction() = f and
  attr.getPropertyName().matches("\\_%") and
  not attr.getPropertyName().matches("\\_\\_%")
}

predicate bagClass(ClassDefinition bag) {
  inSource(bag) and
  exists(FieldDefinition field | field.getDeclaringType() = bag) and
  not exists(MethodDefinition method |
    method.getDeclaringType() = bag and method.getName() != "constructor"
  )
}

predicate doerOnBag(ClassDefinition doer, ClassDefinition bag) {
  bagClass(bag) and
  exists(MethodDefinition method, Parameter p |
    publicMethod(doer, method.getBody()) and
    p = method.getBody().getAParameter() and
    exists(PropAccess access |
      access.getEnclosingFunction() = method.getBody() and
      access.getBase().(VarAccess).getName() = p.getName()
    )
  )
}

predicate envies(Function f, Parameter p) {
  domainParameter(f, p) and
  count(PropAccess access |
    access.getEnclosingFunction() = f and access.getBase().(VarAccess).getName() = p.getName()
  ) >= 2
}

predicate untypedPublicParameter(Function f, Parameter p) {
  publicName(f.getName()) and
  domainParameter(f, p) and
  not exists(p.getTypeAnnotation())
}

predicate numberedParameter(Function f, Parameter p) {
  domainParameter(f, p) and
  p.getName().regexpMatch("[A-Za-z]+[0-9]+")
}

string normalizedPath(File f) { result = f.getRelativePath().replaceAll("\\", "/") }

predicate firstClassModule(Module m) {
  m.getFile().getBaseName() = "index.ts" or
  m.getFile().getBaseName() = "index.js"
}

int classCount(Module pkg) {
  firstClassModule(pkg) and
  result = count(ClassDefinition cls | cls.getFile() = pkg.getFile())
}

int publicClassCount(Module pkg) {
  firstClassModule(pkg) and
  result = count(ClassDefinition cls | cls.getFile() = pkg.getFile() and publicName(cls.getName()))
}

predicate shallowModule(Module m) {
  firstClassModule(m) and
  classCount(m) >= 5 and
  publicClassCount(m) * 100 > classCount(m) * 40
}

predicate cyclicModules(Module a, Module b) {
  a != b and
  exists(ImportDeclaration imp |
    imp.getImportedModule() = b and imp.getFile() = a.getFile()
  ) and
  exists(ImportDeclaration back |
    back.getImportedModule() = a and back.getFile() = b.getFile()
  )
}

predicate domainExtensionInFrameworkModule(ClassDefinition extension, ClassDefinition domainType) {
  extension.getASuperClass() = domainType and
  extension.getFile() != domainType.getFile()
}

predicate passThrough(Function f) {
  exists(CallExpr call, ReturnStmt ret |
    call.getEnclosingFunction() = f and
    ret.getEnclosingFunction() = f and
    ret.getExpr() = call and
    not exists(CallExpr other | other.getEnclosingFunction() = f and other != call)
  )
}

predicate moduleOwningClass(ClassDefinition cls) { inSource(cls) }

string moduleOwningClassPath(ClassDefinition cls) {
  result = cls.getFile().getRelativePath()
}
