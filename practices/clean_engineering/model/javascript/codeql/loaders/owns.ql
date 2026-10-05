/**
 * @name Practice graph owns
 * @kind problem
 * @id cdd/practice-graph/owns
 */

import javascript
import subject_filter
import members

from MethodDefinition method
where classOperation(method)
select method.getDeclaringType().getName(), method.getName(),
  method.getLocation().getStartLine(), "true", method.getFile().getRelativePath()
union
from string className, string name, string base, int start, string path, int end, string hint
where classProperty(className, name, base, start, path, end, hint)
select className, name, start, if isRelativeHint(hint) then "true" else "false", path
