/**
 * @kind problem
 * @id cdd/practice-graph/test/moduleDependsOn
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Module caller, Module callee
where moduleDependsOn(caller, callee)
select caller, caller.getFile().getRelativePath(), callee
