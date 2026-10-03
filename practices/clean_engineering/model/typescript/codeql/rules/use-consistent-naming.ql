/**
 * @name use-consistent-naming
 * @practice clean_engineering
 * @fidelity model
 * @node class
 * @id clean_engineering/model/use-consistent-naming
 */

import javascript
import subject_filter
import model

from Module m, Function f
where inSubject(f) and mixedNamingFunction(m, f)
select f,
  "Operation '" + f.getName() + "' mixes snake_case and camelCase in one module.", f
