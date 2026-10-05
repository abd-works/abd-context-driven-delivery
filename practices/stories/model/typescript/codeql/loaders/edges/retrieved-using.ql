/**
 * @name retrieved-using
 * @kind problem
 * @id cdd/stories/edges/retrieved-using
 */

import javascript

from File f
where none()
select f.getRelativePath(), f.getRelativePath(), "retrievedUsing", 7, "relationship"
