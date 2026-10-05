import javascript
import subject_filter

bindingset[path]
string slash(string path) { result = path.replaceAll("\\", "/") }

bindingset[kind, file, name]
string dddNodeId(string kind, string file, string name) {
  result = "ddd:" + kind + ":" + file + ":" + name
}

string dddPracticeId() { result = "ddd:Practice:.:ddd" }

string classFile(ClassDefinition cls) { result = slash(cls.getFile().getRelativePath()) }

string moduleName(ClassDefinition cls) {
  result = classFile(cls).regexpCapture("src/([^/]+)/.*", 1)
}

bindingset[name]
predicate nonTacticalName(string name) {
  name.matches("%Exception") or
  name.matches("%Error") or
  name.regexpMatch(".*(Client|Node|View|Routes|Router)$")
}

predicate commentText(Locatable loc, int start, int end, string text) {
  exists(Comment comment |
    comment.getLocation().getFile() = loc.getLocation().getFile() and
    start = comment.getLocation().getStartLine() and
    end = comment.getLocation().getEndLine() and
    text = comment.toString().toLowerCase()
  )
}

bindingset[tag]
predicate hasStereotype(ClassDefinition cls, string tag) {
  exists(string text, int end |
    commentText(cls, _, end, text) and
    end <= cls.getLocation().getStartLine() and
    end >= cls.getLocation().getStartLine() - 8 and
    text.matches("%<<" + tag + ">>%")
  )
  or
  cls.getName().toLowerCase().matches("%<<" + tag + ">>%")
}

bindingset[needle]
predicate fieldComment(FieldDefinition field, string needle) {
  exists(string text, int end |
    commentText(field, _, end, text) and
    (
      end = field.getLocation().getStartLine() or
      end = field.getLocation().getStartLine() - 1
    ) and
    text.matches("%" + needle + "%")
  )
}

predicate domainClass(ClassDefinition cls) {
  inSubject(cls) and
  not nonTacticalName(cls.getName()) and
  not hasStereotype(cls, "system")
}

predicate bagClass(ClassDefinition cls) {
  domainClass(cls) and
  exists(FieldDefinition field | field.getDeclaringType() = cls) and
  not exists(MethodDefinition method |
    method.getDeclaringType() = cls and method.getName() != "constructor"
  )
}

bindingset[name]
predicate valueObjectSuffix(string name) {
  name.matches("%Token") or
  name.matches("%Code") or
  name.matches("%Message") or
  name.matches("%Requirement") or
  name.matches("%Requirements") or
  name.matches("%Operation")
}

predicate taggedKind(ClassDefinition cls, string kind) {
  domainClass(cls) and
  (
    hasStereotype(cls, "aggregate root") and kind = "EntityRoot"
    or
    not hasStereotype(cls, "aggregate root") and
      hasStereotype(cls, "specification") and
      kind = "Specification"
    or
    not hasStereotype(cls, "aggregate root") and
      not hasStereotype(cls, "specification") and
      hasStereotype(cls, "entity") and
      kind = "Entity"
    or
    not hasStereotype(cls, "aggregate root") and
      not hasStereotype(cls, "specification") and
      not hasStereotype(cls, "entity") and
      hasStereotype(cls, "value object") and
      kind = "ValueObject"
    or
    not hasStereotype(cls, "aggregate root") and
      not hasStereotype(cls, "specification") and
      not hasStereotype(cls, "entity") and
      not hasStereotype(cls, "value object") and
      hasStereotype(cls, "repository") and
      kind = "Repository"
    or
    not hasStereotype(cls, "aggregate root") and
      not hasStereotype(cls, "specification") and
      not hasStereotype(cls, "entity") and
      not hasStereotype(cls, "value object") and
      not hasStereotype(cls, "repository") and
      hasStereotype(cls, "domain event") and
      kind = "DomainEvent"
    or
    not hasStereotype(cls, "aggregate root") and
      not hasStereotype(cls, "specification") and
      not hasStereotype(cls, "entity") and
      not hasStereotype(cls, "value object") and
      not hasStereotype(cls, "repository") and
      not hasStereotype(cls, "domain event") and
      (
        hasStereotype(cls, "domain service") or
        hasStereotype(cls, "service")
      ) and
      kind = "DomainService"
    or
    not hasStereotype(cls, "aggregate root") and
      not hasStereotype(cls, "specification") and
      not hasStereotype(cls, "entity") and
      not hasStereotype(cls, "value object") and
      not hasStereotype(cls, "repository") and
      not hasStereotype(cls, "domain event") and
      not hasStereotype(cls, "domain service") and
      not hasStereotype(cls, "service") and
      hasStereotype(cls, "factory") and
      kind = "Factory"
  )
}

predicate nameRepository(ClassDefinition cls) {
  domainClass(cls) and cls.getName().matches("%Repository")
}

predicate nameEntityRoot(ClassDefinition cls) {
  domainClass(cls) and
  exists(ClassDefinition repo | nameRepository(repo) and repo.getName() = cls.getName() + "Repository")
}

predicate inferredKind(ClassDefinition cls, string kind) {
  domainClass(cls) and
  not taggedKind(cls, _) and
  (
    nameRepository(cls) and kind = "Repository"
    or
    not nameRepository(cls) and nameEntityRoot(cls) and kind = "EntityRoot"
    or
    not nameRepository(cls) and
      not nameEntityRoot(cls) and
      cls.getName().matches("%Specification") and
      kind = "Specification"
    or
    not nameRepository(cls) and
      not nameEntityRoot(cls) and
      not cls.getName().matches("%Specification") and
      cls.getName().matches("%Factory") and
      kind = "Factory"
    or
    not nameRepository(cls) and
      not nameEntityRoot(cls) and
      not cls.getName().matches("%Specification") and
      not cls.getName().matches("%Factory") and
      cls.getName().matches("%Event") and
      kind = "DomainEvent"
    or
    not nameRepository(cls) and
      not nameEntityRoot(cls) and
      not cls.getName().matches("%Specification") and
      not cls.getName().matches("%Factory") and
      not cls.getName().matches("%Event") and
      cls.getName().matches("%Service") and
      kind = "DomainService"
    or
    not nameRepository(cls) and
      not nameEntityRoot(cls) and
      not cls.getName().matches("%Specification") and
      not cls.getName().matches("%Factory") and
      not cls.getName().matches("%Event") and
      not cls.getName().matches("%Service") and
      (valueObjectSuffix(cls.getName()) or bagClass(cls)) and
      kind = "ValueObject"
    or
    not nameRepository(cls) and
      not nameEntityRoot(cls) and
      not cls.getName().matches("%Specification") and
      not cls.getName().matches("%Factory") and
      not cls.getName().matches("%Event") and
      not cls.getName().matches("%Service") and
      not valueObjectSuffix(cls.getName()) and
      not bagClass(cls) and
      kind = "Entity"
  )
}

predicate kindOf(ClassDefinition cls, string kind) {
  taggedKind(cls, kind) or inferredKind(cls, kind)
}

predicate dddClass(
  ClassDefinition cls, string kind, string id, string name, string file, int start, int end
) {
  kindOf(cls, kind) and
  name = cls.getName() and
  file = classFile(cls) and
  id = dddNodeId(kind, file, name) and
  start = cls.getLocation().getStartLine() and
  end = cls.getLocation().getEndLine()
}

predicate contextPath(string dir, string name) {
  exists(File marker, string path |
    path = slash(marker.getRelativePath()) and
    dir = path.regexpCapture("(.*)/\\.context/bounded-context\\.md", 1) and
    (
      name = dir.regexpCapture(".*/([^/]+)$", 1)
      or
      not dir.matches("%/%") and name = dir
    )
  )
}

predicate implicitContext() { not contextPath(_, _) }

string boundedContextId() {
  implicitContext() and result = dddNodeId("BoundedContext", ".", "bounded context")
  or
  exists(string dir, string name |
    contextPath(dir, name) and result = dddNodeId("BoundedContext", dir, name)
  )
}

predicate aggregateFolder(string mod) {
  exists(ClassDefinition cls | kindOf(cls, "EntityRoot") and moduleName(cls) = mod)
}

bindingset[mod]
string aggregateId(string mod) {
  result = dddNodeId("Aggregate", "src/" + mod, mod)
}

bindingset[name]
predicate typeNames(FieldDefinition field, string name) {
  field.getTypeAnnotation().toString().matches("%" + name + "%")
}
