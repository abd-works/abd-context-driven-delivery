/**
 * @kind problem
 * @id cdd/practice-graph/test/directCall
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Function caller, Function callee
where directCall(caller, callee) and callee.getName() = "pong"
select caller, callee.getName()
