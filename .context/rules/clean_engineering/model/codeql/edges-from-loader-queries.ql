/**
 * @name edges-from-loader-queries
 * @kind problem
 * @id cdd/project/edges-from-loader-queries
 * @problem.severity warning
 *
 * Relatives, properties, or owns stitched in the explorer instead of a CodeQL loader query.
 */

import javascript

predicate knowledgeGraphExplorer(File file) {
  file.getRelativePath().replaceAll("\\", "/").matches("%/explore-knowledge-graph/knowledge-graph/%")
}

predicate stitchesLoaderEdges(Function f) {
  knowledgeGraphExplorer(f.getFile()) and
  (
    f.getName() = "isRelativeTypeName" or
    f.getName() = "isRelativeProperty" or
    f.getName() = "isListedRelative" or
    exists(StringLiteral group |
      group.getEnclosingFunction() = f and
      group.getValue() = "properties" and
      f.getName() = "arrangeListedClassChildren"
    )
  )
}

from Function subject
where stitchesLoaderEdges(subject)
select subject,
  "Emit owns, relative, and other edges from CodeQL loader queries; populate only registers then relates, and the explorer sorts by edge.sequential_order and immediate.",
  subject
