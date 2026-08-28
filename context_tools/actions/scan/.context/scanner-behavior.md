# HIERARCHY: Scanner Framework

<!--
Spec: scanners/scanner_spec.py
Per-scanner repair fixtures: context_tools/clean_engineering/evals/engineering/<rule>/faultyAsset and repairedAsset (scanners_spec.py)
-->

Scanner

  a scanner constructed with a rule slug
    scan is called on a single file path
      violations should carry that rule slug

Violation

  a violation created from a scanner
    to_dict is called
      the dict should include rule, violation_message, severity, line_number, and location

execute_scan

  a scanner class and explicit file list
    execute_scan is called
      it should delegate to scanner.scan and return violations

Clean Code python scanners

  scanners_spec.py — one example test per scanner class

  each scanner class
    it should define faultyAsset and repairedAsset under context_tools/clean_engineering/evals/engineering/<rule>/
    scanning repairedAsset should produce zero violations
    scanning faultyAsset should produce at least one violation for that rule
