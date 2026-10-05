/**
 * @name ddd entity roots
 * @kind problem
 * @id cdd/practice-graph/entity-roots
 */

import javascript

from ClassDefinition cls
where cls.getName() in ["AccountCredentials", "Customer"]
select cls.getName(), "EntityRoot", "ddd", cls.getFile().getRelativePath(),
  cls.getLocation().getStartLine(), cls.getLocation().getEndLine()
