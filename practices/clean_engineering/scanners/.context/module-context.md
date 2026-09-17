# CleanEngineering scanners

## Purpose

Rule scanners that validate Clean Engineering concepts against module folders and production source, reading the class-model language channels rather than ad-hoc regex on raw text. A few process rules also scan markdown design artifacts (sketch / model notation, naming vocabulary).

## Seam

`CodeScanner` / `ModuleScanner` subclasses registered for discovery under `clean_engineering/`. Each scanner implements `scan(root, files)` and emits violations with a stable rule slug.

## Public API

`CodeScanner`, `ModuleScanner`, and concrete rule scanners (function size, SRP, encapsulation, domain language, missing module context, public-seam-only, prefer class operations, reuse-established-notation, reuse-existing-not-invent-parallel, do-not-invent-parallel-object-models, …).

## Dependencies

`utilities.scanners.Scanner` / `ScannerCollection`; `class_model` language channels for parse; stdlib `ast` where structural Python checks are needed.
