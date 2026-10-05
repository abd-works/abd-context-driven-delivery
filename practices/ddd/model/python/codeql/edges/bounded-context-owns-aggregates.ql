/**
 * @name bounded-context-owns-aggregates
 * @kind problem
 * @id cdd/ddd/edges/bounded-context-owns-aggregates
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "owns", 0, "direct"
