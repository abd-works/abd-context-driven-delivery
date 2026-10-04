/**
 * @name Practice graph classes
 * @kind problem
 * @id cdd/practice-graph/classes
 */

import javascript
import subject_filter
import source_span

from ClassDefinition cls
where inSubject(cls)
select cls.getName(), cls.getLocation().getFile().getBaseName(),
  cls.getLocation().getFile().getRelativePath(), sourceStart(cls),
  cls.getLocation().getEndLine()
