/**
 * @name key-interactions-wired
 * @practice ux
 * @fidelity mockup
 * @node screen
 * @id ux/mockup/key-interactions-wired
 * @problem.severity warning
 */

import javascript
import subject_filter
import model

from File file
where
  inSubjectPath(file.getRelativePath()) and
  file.getBaseName().matches("%.js") and
  not hasGoto(file)
select file, "Screen module '" + file.getBaseName() + "' has no data-goto interaction wiring.", file
