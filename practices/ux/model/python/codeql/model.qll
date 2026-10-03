import python
import subject_filter

predicate domainImport(Import imp) {
  exists(string path | path = imp.getAnImportedModuleName() |
    path.matches("%/domain/%") or path.matches("%/stories/%")
  )
}

predicate uxOnlyAdapter(Import imp) {
  exists(string path | path = imp.getAnImportedModuleName() |
    path.matches("%adapter%") or path.matches("%fake%") or path.matches("%stub%")
  ) and
  not domainImport(imp)
}

predicate gotoLiteral(StringLiteral s) { s.getValue() = "data-goto" }

predicate hasGoto(File file) { exists(StringLiteral s | s.getFile() = file and gotoLiteral(s)) }
