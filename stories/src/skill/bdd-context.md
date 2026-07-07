# HIERARCHY: Assemble Skill Components

## Parse Fidelity Levels

  a Fidelity level
    with a known string value
      it should resolve to the matching level
    with all five level strings supplied in pipeline order
      it should resolve to all five levels in that order
    with a string that contains a typo
      it should not be recognised as a valid level
      the error
        it should carry the unrecognised string
    the full ordered set of levels
      it should run from shaping through to engineering

## Scope Files by Phase

  a Phase
    with the Interview scope requested
      it should include concepts and grill-me-questions only
    with the Generate scope requested
      it should include templates, rules, behavior, and concepts
    with the Validate scope requested
      it should include rules only
    with an unrecognised phase string
      it should not be resolved

## Match Files by Front Matter

  a Front Matter record
    with a fidelity set that overlaps the requested set
      it should match the request
    with a fidelity set that does not overlap the requested set
      it should not match the request
    with no format declared
      it should match any requested format
    with a format declared
      with the requested format matching the declared format
        it should match
      with the requested format differing from the declared format
        it should not match
    with an empty fidelity set
      it should not match any request

## Assemble a Manifest

  a Skill Package
    with the Generate phase requested
      it should include files whose fidelity overlaps the requested set
      it should include files whose format matches or is absent
      it should group the included files by their directory
    with the Validate phase requested
      it should include rules files only
    with a file whose format does not match the request
      it should exclude that file
    with a file whose fidelity does not overlap the requested set
      it should exclude that file
    with a file covering multiple fidelity levels
      with one of those levels requested
        it should include the file
    with two files in the same directory
      it should list them in deterministic path order

## Load Skill from Disk

  a Skill Package loaded from a skill root
    with all files carrying valid front matter
      it should include every file
      it should record no anomalies
      the loaded front matter
        it should carry the declared fidelities
        it should carry the declared format
        it should carry the declared section
    with a file carrying an unrecognised fidelity value
      it should still include the file with its valid fidelities only
      the anomaly record
        it should name the unrecognised value
    with a file missing a front matter block
      it should exclude that file
      the anomaly record
        it should identify the file as missing front matter
    with a file in an unrecognised directory
      it should ignore the file
    with a non-markdown file in a known directory
      it should ignore the file

## Run Assembly Command

  the Assembly Command
    with valid arguments and a well-formed skill root
      it should complete the assembly
      it should emit a manifest on standard output as structured data
      it should emit nothing on standard error
      the manifest
        it should list the requested phase
        it should list the requested fidelities
        it should group matched files by their directory
    with a skill root containing files with unrecognised fidelity values
      it should still complete the assembly
      it should emit the anomaly on standard error as structured data
    with an unrecognised fidelity value passed as an argument
      it should refuse the request
      it should emit a structured error on standard error
