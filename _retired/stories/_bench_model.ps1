param([string]$Model)
$env:CURSOR_API_KEY = (Select-String -Path "c:\dev\abd-context-driven-delivery\stories\conf\.secrets" -Pattern "^CURSOR_API_KEY=(.+)$" | ForEach-Object { $_.Matches[0].Groups[1].Value })
$scratch = "c:\dev\abd-context-driven-delivery\stories\evals\.last-run\01-shaping\_bench-$Model"
if (Test-Path $scratch) { Remove-Item -Recurse -Force $scratch }
New-Item -ItemType Directory -Path "$scratch\context" -Force | Out-Null
Copy-Item "c:\dev\abd-context-driven-delivery\stories\evals\01-shaping\context\brief.md" "$scratch\context\brief.md"
$prompt = @"
## Required output files (runner-enforced contract)

Write EVERY file below into the current working directory using its exact relative path. Create parent folders as needed.

- drawio/story-map.drawio
- story-graph.json
- story-map.md

Any ``.drawio`` file above is auto-rendered by the runner from your Markdown / JSON model — do NOT hand-write Draw.io XML.

---

# Shape a story map — Treasury Same-Day Transfers

``context/brief.md`` describes a treasury cash-management product we're scoping for a new release. Read it and shape a first-pass story map for the feature at a high level — I want to see the overall structure, not scenarios or tests yet.

Give me the map as both a Markdown outline and a Draw.io diagram so I can walk the shape with product and eyeball the visual.
"@
Push-Location $scratch
$start = Get-Date
cursor-agent --print --output-format text --force --model $Model $prompt 2>&1 | Out-Null
$elapsed = (Get-Date) - $start
Pop-Location
$files = Get-ChildItem $scratch -Recurse -File | Where-Object { $_.FullName -notlike "*\context\*" }
Write-Host "[$Model] $($elapsed.TotalSeconds.ToString('0.0'))s  files=$($files.Count)  bytes=$(($files | Measure-Object Length -Sum).Sum)"
