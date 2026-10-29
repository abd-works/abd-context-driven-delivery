/**
 * @name story-tests-aggregate
 * @kind problem
 * @id cdd/lern/stories/edges/story-tests-aggregate
 */

import javascript
import lern

from CallExpr call, string name, string file, ImportDeclaration imp
where
  sharedStoryCall(call, name, file) and
  imp.getFile() = call.getFile() and
  exists(aggregateOfImport(imp))
select storySharedId(file, name), aggregateOfImport(imp), "links", 5, "relationship"
