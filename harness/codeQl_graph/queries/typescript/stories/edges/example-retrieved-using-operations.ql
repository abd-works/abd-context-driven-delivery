/**
 * @name example-retrieved-using-operations
 * @kind problem
 * @id cdd/stories/edges/example-retrieved-using-operations
 */

import javascript

from File f
where none()
select f.getRelativePath(), f.getRelativePath(), "retrievedUsing", 7, "relationship"
