/**
 * @name repository-stores-related-aggregate-by-id
 * @kind problem
 * @id paradise/repository-stores-related-aggregate-by-id
 * @problem.severity warning
 */

import javascript

predicate domainRepository(ClassDefinition repo) {
  repo.getName().matches("%Repository") and
  repo.getFile().getRelativePath().regexpMatch(".*src/domain/.*")
}

predicate aggregateTypeName(string name) {
  name = ["Customer", "AccountCredentials", "Onboarding", "Billing"]
}

predicate aggregatePropertyName(string name) {
  name = ["customer", "accountCredentials", "onboarding", "billing"]
}

predicate idPropertyName(string name) {
  name = ["customerId", "onboardingId", "billingId", "accountEmail"]
}

LocalTypeAccess aggregateTypeAccess(TypeExpr type) {
  result = type and
  aggregateTypeName(result.getName())
  or
  result = aggregateTypeAccess(type.(GenericTypeExpr).getATypeArgument())
  or
  result = aggregateTypeAccess(type.(UnionTypeExpr).getAnElementType())
  or
  result = aggregateTypeAccess(type.(ParenthesizedTypeExpr).getElementType())
  or
  result = aggregateTypeAccess(type.(ArrayTypeExpr).getElementType())
}

predicate aggregateValue(Expr value) {
  aggregatePropertyName(value.(VarAccess).getName())
  or
  aggregatePropertyName(value.(PropAccess).getPropertyName())
  or
  aggregateTypeName(value.(NewExpr).getCalleeName())
}

predicate repositoryMapSet(MethodCallExpr setCall, ClassDefinition repo) {
  domainRepository(repo) and
  setCall.getMethodName() = "set" and
  setCall.getReceiver() instanceof PropAccess and
  setCall.getParent*() = repo
}

predicate storedAggregateField(FieldDefinition field, LocalTypeAccess stored, ClassDefinition repo) {
  domainRepository(repo) and
  field.getDeclaringClass() = repo and
  (
    stored = aggregateTypeAccess(field.getInit().(InvokeExpr).getATypeArgument())
    or
    stored = aggregateTypeAccess(field.getTypeAnnotation())
  )
}

predicate snapshotStoresAggregate(Property prop, Expr evidence, ClassDefinition repo) {
  exists(MethodCallExpr setCall |
    repositoryMapSet(setCall, repo) and
    setCall.getArgument(1) = prop.getObjectExpr()
  ) and
  (
    aggregatePropertyName(prop.getName()) and
    evidence = prop.getNameExpr()
    or
    not idPropertyName(prop.getName()) and
    aggregateValue(prop.getInit()) and
    evidence = prop.getInit()
  )
}

from AstNode subject, string message, AstNode contributor
where
  exists(FieldDefinition field, LocalTypeAccess stored, ClassDefinition repo |
    storedAggregateField(field, stored, repo) and
    subject = field and
    contributor = stored and
    message =
      repo.getName() + " field stores " + stored.getName() +
        ". Store that aggregate's id (customerId, onboardingId, billingId, or accountEmail) and load it from its own repository."
  )
  or
  exists(Property prop, Expr evidence, ClassDefinition repo |
    snapshotStoresAggregate(prop, evidence, repo) and
    subject = evidence and
    contributor = prop.getObjectExpr() and
    message =
      repo.getName() + " snapshot stores " + prop.getName() +
        ". Store the related aggregate as customerId, onboardingId, billingId, or accountEmail."
  )
  or
  exists(MethodCallExpr setCall, Expr stored, ClassDefinition repo |
    repositoryMapSet(setCall, repo) and
    stored = setCall.getArgument(1) and
    aggregateValue(stored) and
    subject = setCall and
    contributor = stored and
    message =
      repo.getName() +
        " stores the live aggregate in the map. Store its id and load the aggregate from its own repository."
  )
select subject, message, contributor
