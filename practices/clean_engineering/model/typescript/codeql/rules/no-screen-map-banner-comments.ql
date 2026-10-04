/**
 * @name no-screen-map-banner-comments
 * @kind problem
 * @id paradise/no-screen-map-banner-comments
 * @problem.severity warning
 */

import javascript

predicate isStoryMapBannerComment(Comment c) {
  c.getText().toLowerCase().regexpMatch("(?s).*(screen|story|sub-epic|sources)\\s*:.*")
}

predicate isFileHeaderComment(File f, Comment c) {
  c.getLocation().getFile() = f and
  (
    exists(ImportDeclaration imp |
      imp.getFile() = f and
      c.getLocation().getEndLine() < imp.getLocation().getStartLine()
    )
    or
    not exists(ImportDeclaration imp | imp.getFile() = f) and
    c.getLocation().getStartLine() <= 12
  )
}

from File f, Comment c
where
  isStoryMapBannerComment(c) and
  isFileHeaderComment(f, c)
select c,
  "File '" + f.getRelativePath() +
    "' already names its type from folder and filename. Delete the Screen/Story/Sub-epic/Sources header comment block and keep only code.",
  f
