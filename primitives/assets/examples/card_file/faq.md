# FAQ

## What is AssetLocator?

`AssetLocator` resolves a label to a file, folder, or markdown section beside the
host class. Pass the host object and a label string; call `locate()` to get an
`AssetLocation` describing what was found.

## What is Asset?

`Asset` wraps an `AssetLocation` and provides `collect()` to read the content
as a string.

## What is AssetCollection?

`AssetCollection` wraps a folder-kind location and provides `collect()` (returns
a `dict` of filename → content) and `merged()` (returns all files concatenated).
