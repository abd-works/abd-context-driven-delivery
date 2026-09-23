import python

predicate inSource(AstNode n) {
  exists(string path | path = n.getLocation().getFile().getRelativePath())
}

predicate ownerClass(Function method, Class cls) { method = cls.getAMethod() }

predicate bagClass(Class bag) {
  inSource(bag) and
  exists(AnnAssign assign | assign.getScope() = bag) and
  not exists(Function method |
    ownerClass(method, bag) and
    method.getName() != "__init__"
  )
}

bindingset[name]
predicate shownQueryName(string name) {
  name.regexpMatch("is.*(Showing|Shown).*")
}

predicate screenDriver(Class cls) {
  inSource(cls) and
  exists(Function open, Function shown |
    ownerClass(open, cls) and
    ownerClass(shown, cls) and
    open.getName() = "open" and
    shownQueryName(shown.getName())
  )
}

predicate tacticalStereotypeName(string name) {
  name =
    [
      "Entity", "EntityRoot", "AggregateRoot", "ValueObject", "Repository",
      "DomainEvent", "DomainService"
    ]
}

predicate tacticalBaseName(Expr base, string name) {
  name = base.(Name).getId()
  or
  name = base.(Attribute).getName()
}

predicate inheritsTacticalStereotype(Class cls) {
  exists(string name |
    tacticalBaseName(cls.getABase(), name) and
    tacticalStereotypeName(name)
  )
}

predicate classDocString(Class cls, string doc) {
  exists(ExprStmt stmt, StrConst str |
    stmt.getScope() = cls and
    str = stmt.getValue() and
    doc = str.getText()
  )
}

predicate docstringHasStereotypeTag(Class cls) {
  exists(string doc |
    classDocString(cls, doc) and
    doc.regexpMatch("(?s).*<<(Aggregate Root|Entity|Value Object|Repository|Domain Event|Domain Service)>>.*")
  )
}

predicate stereotypedClass(Class cls) {
  tacticalStereotypeName(cls.getName()) or
  inheritsTacticalStereotype(cls) or
  docstringHasStereotypeTag(cls)
}

predicate domainClass(Class cls) {
  inSource(cls) and
  not tacticalStereotypeName(cls.getName()) and
  (
    exists(AnnAssign assign | assign.getScope() = cls) or
    exists(Function method | ownerClass(method, cls) and method.getName() != "__init__")
  )
}

predicate missingTacticalStereotype(Class cls) {
  domainClass(cls) and
  not stereotypedClass(cls)
}
