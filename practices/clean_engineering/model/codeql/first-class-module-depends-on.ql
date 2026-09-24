/**
 * @kind problem
 * @id cdd/practice-graph/verify/first-class-module-depends-on
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Module caller, Module callee, string callerPrefix, string calleePrefix
where
  moduleDependsOn(caller, callee) and
  callerPrefix = enclosingFirstClassPrefix(normalizedPath(caller.getFile())) and
  calleePrefix = enclosingFirstClassPrefix(normalizedPath(callee.getFile())) and
  callerPrefix != calleePrefix
select callerPrefix, calleePrefix
