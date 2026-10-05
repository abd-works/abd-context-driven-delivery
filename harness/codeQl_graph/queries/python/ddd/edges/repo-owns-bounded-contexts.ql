/**
 * @name repo-owns-bounded-contexts
 * @kind problem
 * @id cdd/ddd/edges/repo-owns-bounded-contexts
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "owns", 0, "direct"
