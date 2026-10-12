/**
 * @name ddd building block edges
 * @kind problem
 * @id cdd/ddd/edges/building-blocks
 */

import javascript
import ddd

predicate aggregateMember(string kind) {
  kind = "Entity" or
  kind = "EntityRoot" or
  kind = "ValueObject" or
  kind = "Repository" or
  kind = "Specification" or
  kind = "Factory" or
  kind = "DomainEvent" or
  kind = "DomainService"
}

predicate link(string parent, string child, string kind, int weight, string display) {
  exists(ClassDefinition cls, string memberId, string mod, string memberKind |
    aggregateMember(memberKind) and
    dddClass(cls, memberKind, memberId, _, _, _, _) and
    mod = moduleName(cls) and
    (
      parent = memberId and
      child = aggregateId(mod) and
      kind = "belongsTo" and
      weight = 4 and
      display = "relationship"
      or
      memberKind = "EntityRoot" and
      parent = aggregateId(mod) and
      child = memberId and
      kind = "root" and
      weight = 1 and
      display = "direct"
      or
      memberKind != "EntityRoot" and
      parent = aggregateId(mod) and
      child = memberId and
      kind = "owns" and
      weight = 2 and
      display = "direct"
    )
  )
  or
  exists(string mod |
    aggregateFolder(mod) and
    (
      parent = contextIdForAggregate(mod) and
      child = aggregateId(mod) and
      kind = "owns" and
      weight = 2 and
      display = "direct"
      or
      parent = aggregateId(mod) and
      child = contextIdForAggregate(mod) and
      kind = "belongsTo" and
      weight = 4 and
      display = "relationship"
    )
  )
  or
  parent = dddPracticeId() and
  child = boundedContextId() and
  kind = "owns" and
  weight = 2 and
  display = "direct"
  or
  exists(ClassDefinition repo, ClassDefinition root |
    dddClass(repo, "Repository", parent, _, _, _, _) and
    dddClass(root, "EntityRoot", child, _, _, _, _) and
    repo.getName() = root.getName() + "Repository" and
    kind = "accesses" and
    weight = 5 and
    display = "relationship"
  )
  or
  exists(ClassDefinition cls, FieldDefinition field, string file, string role |
    (role = "EntityRoot" or role = "Entity") and
    dddClass(cls, role, parent, _, file, _, _) and
    field.getDeclaringType() = cls and
    (
      field.getName() = "id" or
      field.getName() = "identity" or
      fieldComment(field, "identifier")
    ) and
    child = "ddd:Property:" + file + ":" + field.getName() + ":" + cls.getName() and
    kind = "hasIdentity" and
    weight = 3 and
    display = "direct"
  )
  or
  exists(ClassDefinition fromCls, ClassDefinition toCls, string toKind |
    dddClass(fromCls, "EntityRoot", parent, _, _, _, _) and
    dddClass(toCls, toKind, child, _, _, _, _) and
    fromCls != toCls and
    (toKind = "EntityRoot" or toKind = "Entity") and
    exists(FieldDefinition field |
      field.getDeclaringType() = fromCls and
      fieldComment(field, "foreign") and
      typeNames(field, toCls.getName())
    ) and
    kind = "associates" and
    weight = 6 and
    display = "relationship"
  )
  or
  exists(ClassDefinition fromCls, ClassDefinition toCls, string toKind |
    dddClass(fromCls, "Entity", parent, _, _, _, _) and
    dddClass(toCls, toKind, child, _, _, _, _) and
    fromCls != toCls and
    (toKind = "EntityRoot" or toKind = "Entity") and
    exists(FieldDefinition field |
      field.getDeclaringType() = fromCls and
      fieldComment(field, "foreign") and
      typeNames(field, toCls.getName())
    ) and
    kind = "associates" and
    weight = 6 and
    display = "relationship"
  )
  or
  exists(ClassDefinition fromCls, ClassDefinition toCls |
    dddClass(fromCls, _, parent, _, _, _, _) and
    dddClass(toCls, _, child, _, _, _, _) and
    fromCls != toCls and
    exists(FieldDefinition field |
      field.getDeclaringType() = fromCls and
      fieldComment(field, "<<composition>>") and
      typeNames(field, toCls.getName())
    ) and
    kind = "composition" and
    weight = 7 and
    display = "relationship"
  )
  or
  exists(ClassDefinition fromCls, ClassDefinition toCls |
    dddClass(fromCls, _, parent, _, _, _, _) and
    dddClass(toCls, _, child, _, _, _, _) and
    fromCls != toCls and
    exists(FieldDefinition field |
      field.getDeclaringType() = fromCls and
      fieldComment(field, "aggregation") and
      typeNames(field, toCls.getName())
    ) and
    kind = "aggregation" and
    weight = 8 and
    display = "relationship"
  )
}

from string parent, string child, string kind, int weight, string display
where link(parent, child, kind, weight, display)
select parent, child, kind, weight, display
