/**
 * @name lern json stores
 * @kind problem
 * @id cdd/lern/ddd/json-store
 */

import javascript
import model

from File f, string id, string name, string file
where jsonStore(f, id, name, file)
select id, name, "JsonStore", "ddd", file, 1, 1, "implementation"
