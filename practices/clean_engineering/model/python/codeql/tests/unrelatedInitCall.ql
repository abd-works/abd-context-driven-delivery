/**
 * @kind problem
 * @id cdd/practice-graph/test/unrelatedInitCall
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Function caller, Function callee
where
  directCall(caller, callee) and
  caller.getName() = "__init__" and
  callee.getName() = "__init__" and
  caller.getLocation().getFile().getRelativePath().matches("%hide-inner-details%") and
  callee.getLocation().getFile().getRelativePath().matches("%shape-classes-around-resources%")
select caller, callee
