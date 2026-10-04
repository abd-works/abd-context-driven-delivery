/**
 * @name views-render-only
 * @practice clean_engineering
 * @pattern lern_domain_driven
 * @fidelity model
 * @node function
 * @id clean_engineering/model/views-render-only
 */

import javascript
import subject_filter
import model

from AstNode subject, string message, AstNode contributor
where
  exists(Function fn, File f |
    inSubject(fn) and
    screenViewFile(f) and
    fn.getFile() = f and
    fn.getName() = "destination" and
    subject = fn and
    contributor = fn.getIdentifier() and
    message =
      "A screen view only renders. Field entry, host operations, and the next page stay on the client subtype or the node class."
  )
  or
  exists(Function fn |
    inSubject(fn) and
    (clientFile(fn.getFile()) or screenViewFile(fn.getFile())) and
    fn.getName().regexpMatch("^[A-Z].*") and
    not fn.getName().matches("%View") and
    subject = fn and
    contributor = fn and
    message =
      "A screen view only renders. Component '" + fn.getName() + "' does not end with 'View'."
  )
  or
  exists(File f, TopLevel top |
    screenViewFile(f) and
    top.getFile() = f and
    inSubject(top) and
    f.getBaseName().regexpMatch("^[A-Z].*\\.tsx$") and
    subject = top and
    contributor = top and
    message =
      "A screen view only renders. Screen file '" + f.getBaseName() +
        "' stays kebab-case under the sub-epic folder."
  )
select subject, message, contributor
