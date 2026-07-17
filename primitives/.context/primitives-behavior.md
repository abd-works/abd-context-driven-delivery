# HIERARCHY: Generator Primitives

<!--
Spec: primitives/primitives_spec.py
-->

Instruction

  an instruction constructed with plain prose
    expand is called
      the expanded text should remain unchanged

  an instruction whose value is a sibling markdown file
    expand is called
      the expanded text should include the file content

  an instruction whose value is § Section
    expand is called
      the expanded text should include only that section from the canonical markdown

  an instruction whose value is a folder path ending with /
    expand is called
      the expanded text should include every markdown file in that folder

DeclaredMember

  a declared member with name, label, and target
    it should route without holding a value on the declaration

DeclaredProperty

  a declared property with defaultRoot and keyDiscovery none
    route is called on an instance
      it should yield an instruction resolved from defaultRoot

  a declared property with keyDiscovery fileStems
    discoverKeys is called
      it should return stems of markdown files in defaultRoot

  a declared property with keyDiscovery subfolderNames
    discoverKeys is called
      it should return immediate subdirectory names under defaultRoot

  a declared property with activeKey set
    route is called when the active resource is set on the instance
      the resolved path should include the active key segment

DeclaredOperation

  a declared operation with a wired target on the extending class
    route is called
      it should return the target callable

  a declared operation with no wired target
    route is called
      it should return null

ScannerCollection

  scanners/scanner_collection.py — discover, catalog, run

  a scanner collection rooted at formats/python/scanners/
    discover is called
      it should map concept rule slugs to scanner classes

    catalog is called
      it should list every discovered rule slug

    run is called with an explicit file list
      it should return a deterministic report of violations
