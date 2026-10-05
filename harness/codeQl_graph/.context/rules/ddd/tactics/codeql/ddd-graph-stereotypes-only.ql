/**
 * @name ddd-graph-stereotypes-only
 * @kind problem
 * @id cdd/ddd/tactics/ddd-graph-stereotypes-only
 */

import javascript

from ClassDefinition cls
where
  cls.getName().regexpMatch(".*(Exception|Node|Client)$") and
  exists(string path |
    path = cls.getFile().getRelativePath() and
    path.matches("examples/actual/%")
  )
select cls, "DDD graph must not include " + cls.getName() + "; it is not a DDD stereotype.", cls
