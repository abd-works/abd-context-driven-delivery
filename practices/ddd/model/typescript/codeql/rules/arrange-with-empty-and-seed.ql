/**
 * @name arrange-with-empty-and-seed
 * @kind problem
 * @id paradise/arrange-with-empty-and-seed
 * @problem.severity warning
 */

import javascript

bindingset[name]
predicate suffixedEmptyOrSeed(string name) {
  name.regexpMatch("_empty.+|_seed.+")
}

bindingset[name]
predicate fieldBagTypeName(string name) {
  name.regexpMatch(".+Data")
}

bindingset[name]
predicate factoryOrSeederName(string name) {
  name.regexpMatch(".*(Factory|Seeder)")
}

predicate accountRepositoryLoad(MethodCallExpr call) {
  call.getMethodName() = "load" and
  (
    call.getReceiver().(PropAccess).getPropertyName() = "accountRepository"
    or
    call.getReceiver().(VarAccess).getName() = "accountRepository"
  )
}

predicate loadReadsEmailOffAnAccount(MethodCallExpr call, Expr arg) {
  accountRepositoryLoad(call) and
  arg = call.getArgument(0) and
  (
    arg.(PropAccess).getPropertyName() = "email"
    or
    arg.(VarAccess).getName().regexpMatch("(?i).*account.*")
    or
    arg instanceof NewExpr
    or
    arg instanceof CallExpr
  )
}

from AstNode subject, string message, AstNode contributor
where
  (
    exists(MethodDefinition method |
      subject = method and
      suffixedEmptyOrSeed(method.getName()) and
      contributor = method.getDeclaringClass() and
      message =
        "Name the test control _empty or _seed. Do not suffix it with the aggregate name."
    )
    or
    exists(MethodCallExpr call |
      subject = call and
      suffixedEmptyOrSeed(call.getMethodName()) and
      contributor = call.getReceiver() and
      message =
        "Call repo._empty() or repo._seed(aggregate). Do not call a suffixed _empty* or _seed* test control."
    )
    or
    exists(TypeAliasDeclaration alias |
      subject = alias and
      fieldBagTypeName(alias.getName()) and
      contributor = alias and
      message =
        "Do not add a field-bag type. Fill the aggregate from repo._empty() and set its business fields."
    )
    or
    exists(InterfaceDeclaration iface |
      subject = iface and
      fieldBagTypeName(iface.getName()) and
      contributor = iface and
      message =
        "Do not add a field-bag type. Fill the aggregate from repo._empty() and set its business fields."
    )
    or
    exists(MethodCallExpr call |
      subject = call and
      call.getMethodName() = ["new", "seed"] and
      call.getNumArgument() > 0 and
      call.getFile().getRelativePath().regexpMatch(".*tests/.*") and
      contributor = call.getArgument(0) and
      message =
        "Do not call repository.new(data) or repository.seed(data). Call repo._empty() and repo._seed(aggregate)."
    )
    or
    exists(ClassDefinition type |
      subject = type and
      factoryOrSeederName(type.getName()) and
      contributor = type and
      message =
        "Do not introduce a factory or seeder. The scenario calls the named example function."
    )
    or
    exists(Property enter, Function fn |
      subject = enter and
      enter.getName() = "enter" and
      fn = enter.getInit() and
      enter.getFile().getRelativePath().regexpMatch(".*tests/.*") and
      contributor = fn and
      message =
        "Do not put a function on outline property enter. The scenario calls the named example function."
    )
    or
    exists(MethodCallExpr call, Expr arg |
      subject = call and
      loadReadsEmailOffAnAccount(call, arg) and
      contributor = arg and
      message =
        "load takes an email string. Do not build an account only to read .email."
    )
  )
select subject, message, contributor
