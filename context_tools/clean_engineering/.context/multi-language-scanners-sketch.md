MultiLanguageScan
  // common RuleEvals once; language = class_model/{lang}_class_model.py channel

  RuleEval : Scanner
    check module -> Violations via Operation / OoadClass fields
    // no direct ast in scanners

  Channels
    class_model/base_class_model.py
    class_model/python_class_model.py
    class_model/c_family_parse.py
    class_model/{typescript,javascript,java}_class_model.py

  Layout
    context_tools/clean_engineering/
      class_model/
      scanners/   // all RuleEvals + multi_language_scanners_spec

## Done
- One scanner set; CodeScanner picks channel by extension
- All 17 code RuleEvals covered × Python / TypeScript / JavaScript / Java
  in multi_language_scanners_spec (68 examples)
- Python repair fixtures still in scanners_spec (17 examples)
- Module/folder scanners remain structure-oriented (not per-language)
