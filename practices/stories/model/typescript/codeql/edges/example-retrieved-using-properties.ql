/**
 * @name example-retrieved-using-properties
 * @kind problem
 * @id cdd/stories/edges/example-retrieved-using-properties
 */

import javascript

from File f
where none()
select f.getRelativePath(), f.getRelativePath(), "retrievedUsing", 7, "relationship"
