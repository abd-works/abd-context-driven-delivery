/**
 * @name Practice graph classes
 * @kind problem
 * @id cdd/practice-graph/classes-javascript
 */

import javascript

from ClassDefinition cls
where exists(cls.getName())
select cls.getName(), cls.getFile().getBaseName(),
  cls.getFile().getRelativePath(), cls.getLocation().getStartLine(),
  cls.getLocation().getEndLine()
