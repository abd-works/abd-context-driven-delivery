# CleanEngineering scanners

## Purpose

Rule scanners that validate Clean Engineering concepts against module folders and production source, reading the class-model language channels rather than ad-hoc regex on raw text.

## Seam

`CodeScanner` / `ModuleScanner` subclasses registered for discovery under `clean_engineering/`. Each scanner implements `scan(root, files)` and emits violations with a stable rule slug.

## Public API

`CodeScanner`, `ModuleScanner`, and concrete rule scanners (function size, SRP, encapsulation, domain language, missing module context, prefer class operations, …).

## Dependencies

`utilities.scanners.Scanner` / `ScannerCollection`; `class_model` language channels for parse; stdlib `ast` where structural Python checks are needed.

## Known scan notes

Some scanners still keep private module-level helpers that belong on the scanner class (`prefer-class-operations`). Prefer class methods when touching those files.
