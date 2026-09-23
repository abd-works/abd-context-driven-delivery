/**
 * @name Practice graph classes
 * @kind problem
 * @id cdd/practice-graph/classes
 */

import python
import subject_filter
import source_span

from Class cls
where inSubject(cls)
select cls.getName(), cls.getLocation().getFile().getShortName(),
  cls.getLocation().getFile().getRelativePath(), sourceStart(cls),
  cls.getLocation().getEndLine()
