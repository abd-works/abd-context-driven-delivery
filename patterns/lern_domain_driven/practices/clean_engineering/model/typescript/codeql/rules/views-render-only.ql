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

predicate viewModule(File f) {
  screenViewFile(f)
  or
  (
    f.getExtension() = "tsx" and
    epicPackagePath(f.getRelativePath()) and
    not clientFile(f) and
    not f.getBaseName() = "main.tsx" and
    not f.getBaseName().matches("%-redirect.tsx") and
    not f.getBaseName().matches("%-shell.tsx") and
    not f.getBaseName().matches("%-view.tsx")
  )
}

from AstNode subject, string message, AstNode contributor
where
  exists(Function fn, File f |
    inSubject(fn) and
    viewModule(f) and
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
    viewModule(fn.getFile()) and
    exists(ExportDeclaration exp | exp.getAChild*() = fn) and
    fn.getName().regexpMatch("^[A-Z].*") and
    not fn.getName().matches("%View") and
    subject = fn and
    contributor = fn and
    message =
      "A screen view only renders. Component '" + fn.getName() + "' does not end with 'View'."
  )
  or
  exists(File f, TopLevel top |
    viewModule(f) and
    top.getFile() = f and
    inSubject(top) and
    f.getBaseName().regexpMatch("^[A-Z].*\\.tsx$") and
    subject = top and
    contributor = top and
    message =
      "A screen view only renders. Screen file '" + f.getBaseName() +
        "' stays kebab-case in the aggregate folder, beside the client file and the node file."
  )
select subject, message, contributor
