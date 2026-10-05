/**
 * @name repo-owns-bounded-contexts
 * @kind problem
 * @id cdd/ddd/edges/repo-owns-bounded-contexts
 */

import javascript
import ddd.ddd

from string parent, string child
where parent = dddPracticeId() and child = boundedContextId()
select parent, child, "owns", 2, "direct"
