/**
 * @name codeql-loaders-only
 * @kind problem
 * @id cdd/clean_engineering/code/codeql-loaders-only
 * @problem.severity warning
 *
 * src/ must not import knowledge_graph, typescript-source, or the typescript package as an AST stand-in.
 */

import javascript

predicate forbiddenLoaderPath(string imported) {
  imported.regexpMatch(".*knowledge_graph.*")
  or
  imported.regexpMatch(".*typescript-source.*")
  or
  imported = "typescript"
  or
  imported.regexpMatch("typescript/.*")
}

from Import imp
where
  forbiddenLoaderPath(imp.getImportedPath().getValue()) and
  imp.getFile().getRelativePath().regexpMatch("src/.*")
select imp,
  "Populate fills CodeQLKnowledgeGraph from queries/ loaders; do not import knowledge_graph, legacy loaders, or a TypeScript AST stand-in.",
  imp
