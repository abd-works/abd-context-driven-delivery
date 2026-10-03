/**
 * @kind problem
 * @id cdd/practice-graph/test/numberedName
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Parameter p
where numberedName(p.getName())
select p, p.getName()
