/**
 * @name type-aggregation-types
 * @kind problem
 * @id cdd/ddd/edges/type-aggregation-types
 */

import python

from Module m
where none()
select m.getName(), m.getName(), "owns", 0, "direct"
