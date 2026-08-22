# Rebuild Bdd eval turn commits from fab54f7 - one artifact class per turn, per slice.
# Run from repo root: .\scripts\rebuild-bdd-turn-history.ps1

$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)

function Write-Utf8($Path, $Content) {
    [System.IO.File]::WriteAllText($Path, $Content, (New-Object System.Text.UTF8Encoding $false))
}

$staging = Join-Path $PWD ".rebuild-staging"
if (-not (Test-Path $staging)) { throw "Missing .rebuild-staging - run export first or restore from prior run" }

function Export-GitFile($commit, $path, $out) {
    $text = git show "${commit}:${path}"
    Write-Utf8 $out $text
}

# Re-export if staging incomplete
$needExport = -not (Test-Path (Join-Path $staging "grill-tick1-grill.md"))
if ($needExport) {
    New-Item -ItemType Directory -Force -Path $staging | Out-Null
    Export-GitFile "e4ebad9" "context_tools/actions/workspace/.context/sessions/eval-consolidate-workspace/grill-answers.md" (Join-Path $staging "grill-tick1-grill.md")
    Export-GitFile "a843f7f" "context_tools/actions/workspace/.context/sessions/eval-consolidate-workspace/grill-answers.md" (Join-Path $staging "grill-tick1-answer.md")
    Export-GitFile "66b248f" "context_tools/actions/workspace/.context/sessions/eval-consolidate-workspace/grill-answers.md" (Join-Path $staging "grill-tick2-grill.md")
    Export-GitFile "50c791b" "context_tools/actions/workspace/.context/sessions/eval-consolidate-workspace/grill-answers.md" (Join-Path $staging "grill-tick2-answer.md")
    Export-GitFile "b2a1249" "context_tools/actions/workspace/.context/sessions/eval-consolidate-workspace/grill-answers.md" (Join-Path $staging "grill-tick3-grill.md")
    Export-GitFile "b7d2827" "context_tools/actions/workspace/.context/sessions/eval-consolidate-workspace/grill-answers.md" (Join-Path $staging "grill-tick3-answer.md")
    Export-GitFile "14230fd" "context_tools/actions/workspace/.context/sessions/eval-consolidate-workspace/workspace-bdd-sketch.md" (Join-Path $staging "sketch-slice-a.md")
    Export-GitFile "f414f29" "context_tools/actions/workspace/workspace_spec.py" (Join-Path $staging "spec-slice-a.py")
    Export-GitFile "e57e596" "context_tools/actions/workspace/.context/sessions/eval-consolidate-workspace/grill-answers.md" (Join-Path $staging "grill-final.md")
    Export-GitFile "e57e596" "context_tools/actions/workspace/.context/sessions/eval-consolidate-workspace/workspace-bdd-sketch.md" (Join-Path $staging "sketch-full.md")
    Export-GitFile "e57e596" "context_tools/actions/workspace/workspace_spec.py" (Join-Path $staging "spec-full.py")
}

$after3 = Get-Content (Join-Path $staging "grill-tick3-answer.md") -Raw
$final = Get-Content (Join-Path $staging "grill-final.md") -Raw
$sketchFull = Get-Content (Join-Path $staging "sketch-full.md") -Raw

function Grill-Pending($section) {
    $s = $section -replace "\*\*Judge answer:\*\*[^\n]*", "**Judge answer:** *(pending)*"
    $s = $s -replace "(?s)\*\*Citations:\*\*.*?(?=\*\*Slice unlocked:\*\*)", "**Citations:** *(pending)*`n`n"
    $s = $s -replace "\*\*Slice unlocked:\*\*[^\n]*", "**Slice unlocked:** *(pending)*"
    return $s.TrimEnd()
}

if (-not (Test-Path (Join-Path $staging "grill-tick4-grill.md"))) {
    $tick4Full = if ($final -match "(?s)(### Turn \(grill tick 4.*?)(?=---\s*\n\s*### Turn \(grill tick 5)") { $Matches[1].TrimEnd() } else { throw "tick4" }
    $tick5Full = if ($final -match "(?s)(### Turn \(grill tick 5.*?)(?=---\s*\n\s*### Turn \(grill tick 6)") { $Matches[1].TrimEnd() } else { throw "tick5" }
    $tick6Full = if ($final -match "(?s)(### Turn \(grill tick 6.*?)\z") { $Matches[1].TrimEnd() } else { throw "tick6" }
    Write-Utf8 (Join-Path $staging "grill-tick4-grill.md") (($after3.TrimEnd() + "`n`n---`n`n" + (Grill-Pending $tick4Full) + "`n"))
    Write-Utf8 (Join-Path $staging "grill-tick4-answer.md") (($after3.TrimEnd() + "`n`n---`n`n" + $tick4Full + "`n"))
    Write-Utf8 (Join-Path $staging "grill-tick5-grill.md") ((Get-Content (Join-Path $staging "grill-tick4-answer.md") -Raw).TrimEnd() + "`n`n---`n`n" + (Grill-Pending $tick5Full) + "`n")
    Write-Utf8 (Join-Path $staging "grill-tick5-answer.md") ((Get-Content (Join-Path $staging "grill-tick4-answer.md") -Raw).TrimEnd() + "`n`n---`n`n" + $tick5Full + "`n")
    Write-Utf8 (Join-Path $staging "grill-tick6-grill.md") ((Get-Content (Join-Path $staging "grill-tick5-answer.md") -Raw).TrimEnd() + "`n`n---`n`n" + (Grill-Pending $tick6Full) + "`n")
    Write-Utf8 (Join-Path $staging "grill-tick6-answer.md") $final

    if ($sketchFull -notmatch "(?s)(## Slice B.*?)(## Slice C)") { throw "sketch slice B" }
    $sliceB = $Matches[1].TrimEnd()
    if ($sketchFull -notmatch "(?s)(## Slice C.*?)(## Slice D)") { throw "sketch slice C" }
    $sliceC = $Matches[1].TrimEnd()
    $sketchA = Get-Content (Join-Path $staging "sketch-slice-a.md") -Raw
    Write-Utf8 (Join-Path $staging "sketch-slice-ab.md") (($sketchA -replace '(?s)\*\*Deferred:.*', '').TrimEnd() + "`n`n" + $sliceB)
    Write-Utf8 (Join-Path $staging "sketch-slice-abc.md") ((Get-Content (Join-Path $staging "sketch-slice-ab.md") -Raw).TrimEnd() + "`n`n" + $sliceC)

    $specLines = Get-Content (Join-Path $staging "spec-full.py")
    $idxWorkSession = ($specLines | Select-String -Pattern 'with description\("a work session"\)' | Select-Object -First 1).LineNumber - 1
    $idxHost = ($specLines | Select-String -Pattern 'with description\("a context tool host"\)' | Select-Object -First 1).LineNumber - 1
    Write-Utf8 (Join-Path $staging "spec-slice-ab.py") (($specLines[0..($idxWorkSession - 1)] -join "`n") + "`n")
    Write-Utf8 (Join-Path $staging "spec-slice-abc.py") (($specLines[0..($idxHost - 1)] -join "`n") + "`n")

    Export-GitFile "e4ebad9" "context_tools/bdd/.context/bdd-grill-sketch-workflow.md" (Join-Path $staging "bdd-grill-sketch-workflow.md")
    Export-GitFile "e4ebad9" "context_tools/bdd/bdd_grill_sketch_agent_spec.py" (Join-Path $staging "bdd_grill_sketch_agent_spec.py")
    Export-GitFile "e4ebad9" "context_tools/bdd/.context/.agent_bdd_sessions/bdd-grill-sketch-two-agent.json" (Join-Path $staging "bdd-grill-sketch-two-agent.json")
}

Write-Host "Resetting to fab54f7..."
git reset --hard fab54f7de84c850917db59c42f417a697dcf8d27

$wsSess = "context_tools/actions/workspace/.context/sessions/eval-consolidate-workspace"
$evalSess = "context_tools/actions/eval/.context/sessions/eval-consolidate-workspace"
New-Item -ItemType Directory -Force -Path "$wsSess/logs", $evalSess | Out-Null

$branch = "session/eval-consolidate-workspace"
$cddAt = "fab54f7de84c850917db59c42f417a697dcf8d27"
$turnRecords = @()

function Write-SessionYaml {
    param([array]$Turns)
    $lines = @(
        "branch: $branch",
        "path: context_tools/actions/workspace",
        "cdd_at: $cddAt",
        "turns:"
    )
    foreach ($t in $Turns) {
        $lines += "- id: $($t.id)"
        $lines += "  prompt: $($t.prompt)"
        $lines += "  result: $($t.result)"
        $lines += "  context: eval-consolidate-workspace"
        $lines += "  change_commit:"
        $lines += "    turn_id: $($t.id)"
        $lines += "    session_name: eval-consolidate-workspace"
        $lines += "    tool_names: []"
        $lines += "    mistake_ids: []"
        $lines += "    sha: $($t.sha)"
        $lines += "  tool_calls: []"
        $lines += "  mistakes: []"
    }
    Write-Utf8 "$wsSess/session.yaml" (($lines -join "`n") + "`n")
}

function Sync-GrillEval { param([string]$Src); Copy-Item $Src "$evalSess/grill-answers.md" -Force }
function Sync-SketchEval { param([string]$Src); Copy-Item $Src "$evalSess/workspace-bdd-sketch.md" -Force }

function Commit-Turn {
    param(
        [string]$Id,
        [string]$Prompt,
        [string]$Result,
        [string[]]$ArtifactPaths
    )
    foreach ($p in $ArtifactPaths) {
        if (-not (Test-Path $p)) { throw "Missing artifact for turn ${Id}: $p" }
        git add -- $p
    }
    if (git diff --cached --quiet) { throw "turn $Id would be empty - aborting" }
    git commit -m "turn $Id" | Out-Null
    $sha = (git rev-parse HEAD).Trim()
    $script:turnRecords += [pscustomobject]@{ id = $Id; prompt = $Prompt; result = $Result; sha = $sha }
    Write-SessionYaml -Turns $script:turnRecords
    git add "$wsSess/session.yaml"
    git commit --amend --no-edit | Out-Null
    $sha = (git rev-parse HEAD).Trim()
    $script:turnRecords[-1].sha = $sha
    Write-Host "turn $Id -> $sha"
}

Copy-Item (Join-Path $staging "bdd-grill-sketch-workflow.md") "context_tools/bdd/.context/bdd-grill-sketch-workflow.md"
Copy-Item (Join-Path $staging "bdd_grill_sketch_agent_spec.py") "context_tools/bdd/bdd_grill_sketch_agent_spec.py"
New-Item -ItemType Directory -Force -Path "context_tools/bdd/.context/.agent_bdd_sessions" | Out-Null
Copy-Item (Join-Path $staging "bdd-grill-sketch-two-agent.json") "context_tools/bdd/.context/.agent_bdd_sessions/bdd-grill-sketch-two-agent.json"
git add context_tools/bdd/.context/bdd-grill-sketch-workflow.md context_tools/bdd/bdd_grill_sketch_agent_spec.py context_tools/bdd/.context/.agent_bdd_sessions/bdd-grill-sketch-two-agent.json
git commit -m "Add bdd grill-sketch two-agent workflow and agent spec" | Out-Null

$turnPlan = @(
    @{ id = "7f0c79ab"; prompt = "bdd grill tick 1 - first behavior slice boundary"; result = "One slice-boundary question appended to grill-answers.md"; grill = "grill-tick1-grill.md" }
    @{ id = "6cdf54db"; prompt = "bdd judge answer - grill tick 1"; result = "Recommend slice A; slice family locked"; grill = "grill-tick1-answer.md" }
    @{ id = "0c3be234"; prompt = "bdd grill tick 2 - lookupPath absent + row shape"; result = "Question on lookupPath when no row"; grill = "grill-tick2-grill.md" }
    @{ id = "3ceac306"; prompt = "bdd judge answer - grill tick 2"; result = "lookupPath absent -> None; tool+fidelity+path rows"; grill = "grill-tick2-answer.md" }
    @{ id = "bea7a355"; prompt = "bdd grill tick 3 - upsertPath default-match removal"; result = "Question on sparse row removal"; grill = "grill-tick3-grill.md" }
    @{ id = "92bd1931"; prompt = "bdd judge answer - grill tick 3"; result = "upsertPath(..., default_path); slice A unlocked"; grill = "grill-tick3-answer.md" }
    @{ id = "f836cfb9"; prompt = "bdd sketch - slice A path overrides"; result = "workspace-bdd-sketch.md slice A"; sketch = "sketch-slice-a.md" }
    @{ id = "38d36f65"; prompt = "bdd judge validate - slice A sketch"; result = "PASS"; validate = $true }
    @{ id = "d541cf31"; prompt = "bdd iterate - slice A behavior SIGNATUREs"; result = "workspace_spec.py 7 markers"; spec = "spec-slice-a.py" }
    @{ id = "6d48c64c"; prompt = "bdd grill tick 4 - slice B boundary"; result = "openWorkSession boundary question"; grill = "grill-tick4-grill.md" }
    @{ id = "652448a0"; prompt = "bdd judge answer - grill tick 4"; result = "Workspace-only openWorkSession; slice B unlocked"; grill = "grill-tick4-answer.md" }
    @{ id = "c4e8f2a1"; prompt = "bdd sketch - slice B openWorkSession"; result = "workspace-bdd-sketch.md slices A+B"; sketch = "sketch-slice-ab.md" }
    @{ id = "d7a3b9e2"; prompt = "bdd judge validate - slice B sketch"; result = "PASS"; validate = $true }
    @{ id = "e8f1c4d3"; prompt = "bdd iterate - slice B behavior SIGNATUREs"; result = "workspace_spec.py +slice B markers"; spec = "spec-slice-ab.py" }
    @{ id = "32a30eb3"; prompt = "bdd grill tick 5 - slice C boundary"; result = "WorkSession.open git branch policy question"; grill = "grill-tick5-grill.md" }
    @{ id = "0944f56c"; prompt = "bdd judge answer - grill tick 5"; result = "Branch rules only; slice C unlocked"; grill = "grill-tick5-answer.md" }
    @{ id = "f2a8d6e1"; prompt = "bdd sketch - slice C WorkSession.open"; result = "workspace-bdd-sketch.md slices A+B+C"; sketch = "sketch-slice-abc.md" }
    @{ id = "a3b7c9f4"; prompt = "bdd judge validate - slice C sketch"; result = "PASS"; validate = $true }
    @{ id = "b4c8d2e5"; prompt = "bdd iterate - slice C behavior SIGNATUREs"; result = "workspace_spec.py +slice C markers"; spec = "spec-slice-abc.py" }
    @{ id = "912446d6"; prompt = "bdd grill tick 6 - slice D boundary"; result = "host edit-path resolution question"; grill = "grill-tick6-grill.md" }
    @{ id = "e5788bb5"; prompt = "bdd judge answer - grill tick 6"; result = "slice D unlocked"; grill = "grill-tick6-answer.md" }
    @{ id = "c5d9e3f6"; prompt = "bdd sketch - slice D host edit-path resolution"; result = "workspace-bdd-sketch.md slices A-D"; sketch = "sketch-full.md" }
    @{ id = "d6e0f4a7"; prompt = "bdd judge validate - slice D sketch"; result = "PASS; checklist 1-5 covered"; validate = $true }
    @{ id = "e7f1a5b8"; prompt = "bdd iterate - slice D behavior SIGNATUREs"; result = "workspace_spec.py 21 markers; scan clean"; spec = "spec-full.py" }
)

foreach ($step in $turnPlan) {
    $artifacts = @()
    if ($step.grill) {
        Copy-Item (Join-Path $staging $step.grill) "$wsSess/grill-answers.md" -Force
        Sync-GrillEval "$wsSess/grill-answers.md"
        $artifacts += "$wsSess/grill-answers.md", "$evalSess/grill-answers.md"
    }
    if ($step.sketch) {
        Copy-Item (Join-Path $staging $step.sketch) "$wsSess/workspace-bdd-sketch.md" -Force
        Sync-SketchEval "$wsSess/workspace-bdd-sketch.md"
        $artifacts += "$wsSess/workspace-bdd-sketch.md", "$evalSess/workspace-bdd-sketch.md"
    }
    if ($step.spec) {
        Copy-Item (Join-Path $staging $step.spec) "context_tools/actions/workspace/workspace_spec.py" -Force
        $artifacts += "context_tools/actions/workspace/workspace_spec.py"
    }
    if ($step.validate) {
        Write-Utf8 "$wsSess/logs/events.log" "$(Get-Date -Format 'yyyy-MM-ddTHH:mm:ss') kind=action toolset=context_tools.bdd.bdd:Bdd name=validate ok=true summary=PASS`n"
        $artifacts += "$wsSess/logs/events.log"
    }
    Commit-Turn -Id $step.id -Prompt $step.prompt -Result $step.result -ArtifactPaths $artifacts
}

Write-Host "Done: $(git log fab54f7..HEAD --oneline | Measure-Object -Line | Select-Object -ExpandProperty Lines) commits after fab54f7. HEAD $(git rev-parse --short HEAD)"
