/**
 * @kind problem
 * @id cdd/practice-graph/test/moduleDependsOn
 * @problem.severity warning
 */

import python
import subject_filter
import model

from File caller, File callee
where moduleDependsOn(caller, callee)
select caller, caller.getRelativePath(), callee
