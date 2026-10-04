/**
 * @name aggregate-lives-in-its-own-folder
 * @kind problem
 * @id paradise/aggregate-lives-in-its-own-folder
 * @problem.severity warning
 */

import javascript

predicate aggregateRoot(ClassDefinition aggregate) {
  aggregate.getName() in [
    "AccountCredentials",
    "Customer",
    "Onboarding",
    "Billing"
  ]
}

predicate underLegacyDomainPath(ClassDefinition aggregate) {
  aggregate.getFile().getRelativePath().regexpMatch("src/domain/.*")
}

predicate pascalCaseCoreFile(ClassDefinition aggregate) {
  aggregate
      .getFile()
      .getRelativePath()
      .regexpMatch("src/[^/]+/[A-Z][^/]*\\.ts$") and
  not aggregate.getFile().getRelativePath().regexpMatch(".*-node\\.ts$")
}

predicate aggregateFolderFile(File file) {
  file.getRelativePath().regexpMatch("src/[^/]+/[^/]+\\.(ts|tsx)$") and
  not file.getRelativePath().regexpMatch("src/[^/]+/[^/]+-node\\.ts$") and
  not file.getRelativePath().regexpMatch("src/[^/]+/[^/]+-client\\.tsx$")
}

predicate coreAggregateFile(File file) {
  exists(string path, string slug |
    path = file.getRelativePath() and
    slug = path.regexpCapture("src/([^/]+)/([^/]+)\\.(ts|tsx)$", 1) and
    path.regexpMatch("src/" + slug + "/" + slug + "\\.ts$")
  )
}

predicate ownedValueObjectInSeparateFile(ClassDefinition valueObject) {
  exists(File file |
    file = valueObject.getFile() and
    aggregateFolderFile(file) and
    not coreAggregateFile(file) and
    not valueObject.getName().matches("%Node") and
    not valueObject.getName().matches("%Client") and
    not valueObject.getName().matches("%Repository") and
    not aggregateRoot(valueObject)
  )
}

from AstNode subject, string message, AstNode contributor
where
  exists(ClassDefinition aggregate |
    aggregateRoot(aggregate) and
    underLegacyDomainPath(aggregate) and
    subject = aggregate and
    contributor = aggregate and
    message =
      "Aggregate " + aggregate.getName() +
        " lives under src/domain/. Put it in src/<domain-slug>/<domain>.ts with -node.ts, -client.tsx, and <domain-plural>.json."
  )
  or
  exists(ClassDefinition aggregate |
    aggregateRoot(aggregate) and
    pascalCaseCoreFile(aggregate) and
    subject = aggregate and
    contributor = aggregate and
    message =
      "Aggregate " + aggregate.getName() +
        " core file uses PascalCase. Name the core file <domain>.ts in src/<domain-slug>/."
  )
  or
  exists(ClassDefinition valueObject |
    ownedValueObjectInSeparateFile(valueObject) and
    subject = valueObject and
    contributor = valueObject and
    message =
      "Value object " + valueObject.getName() +
        " is in its own file. Keep value objects the aggregate owns in the core <domain>.ts file."
  )
select subject, message, contributor
