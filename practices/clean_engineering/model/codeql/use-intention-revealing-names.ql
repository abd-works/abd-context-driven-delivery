/**
 * @name use-intention-revealing-names
 * @practice clean_engineering
 * @fidelity model
 * @node class
 * @id clean_engineering/model/use-intention-revealing-names
 * @problem.severity warning
 */

import python
import subject_filter
import model

from Function f, Name nm
where inSubject(f) and intentionHidingName(f, nm)
select f,
  "Operation '" + f.getName() + "' assigns the unclear name '" + nm.getId() + "'.", nm
